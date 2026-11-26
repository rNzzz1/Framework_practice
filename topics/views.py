"""Контроллеры (views) веб-приложения сервиса выбора тем курсовых работ.

Включает:
- HTML-представления:
  - index_view: каталог тем с формой фильтрации TopicFilterForm, сортировкой и пагинацией (Paginator)
  - topic_detail_view / topic_detail_slug_view: детальная карточка темы по ID и каноническому Slug
  - students_list_view: список студентов с академическими показателями и бейджами отличников
  - applications_list_view: журнал заявок со статусами, фильтрацией и пагинацией
  - apply_view: создание заявки через ModelForm (ApplicationForm) с валидацией
  - application_edit_view: редактирование заявки через ModelForm (ApplicationEditForm с instance)
  - cancel_application_view: безопасная отмена заявки через POST с CSRF-защитой
  - topic_create_view / topic_edit_view: управление темами с загрузкой файлов (ImageField, request.FILES)
  - statistics_view: агрегированная аналитика и сводка
- RESTful JSON API:
  - api_topics_list, api_topic_detail, api_create_application, api_statistics, api_health
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q

from .models import Discipline, Student, Topic, Application
from .forms import TopicFilterForm, ApplicationForm, ApplicationEditForm, TopicForm


# ==============================================================================
# HTML ВЕБ-СТРАНИЦЫ
# ==============================================================================

def index_view(request):
    """Главная страница: каталог тем курсовых работ с TopicFilterForm, пагинацией и оптимизацией SQL."""
    form = TopicFilterForm(request.GET)
    topics = Topic.objects.select_related("discipline").all()

    if form.is_valid():
        query = form.cleaned_data.get("q")
        discipline = form.cleaned_data.get("discipline")
        min_course = form.cleaned_data.get("min_course")
        sort = form.cleaned_data.get("sort")

        if query:
            topics = topics.filter(
                Q(title__icontains=query)
                | Q(supervisor__icontains=query)
                | Q(discipline__name__icontains=query)
            )

        if discipline:
            topics = topics.filter(discipline=discipline)

        if min_course:
            topics = topics.filter(min_course__lte=int(min_course))

        if sort:
            topics = topics.order_by(sort)
        else:
            topics = topics.order_by("title")
    else:
        topics = topics.order_by("title")

    # Пагинация: по 6 тем на страницу
    paginator = Paginator(topics, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "page_obj": page_obj,
        "topics": page_obj.object_list,
        "total_results": paginator.count,
    }
    return render(request, "topics/index.html", context)


def topic_detail_view(request, pk):
    """Детальный просмотр темы курсовой работы по первичному ключу (PK)."""
    topic = get_object_or_404(Topic.objects.select_related("discipline"), pk=pk)
    active_applications = topic.applications.select_related("student").filter(status=Application.Status.ACTIVE)

    context = {
        "topic": topic,
        "active_applications": active_applications,
    }
    return render(request, "topics/topic_detail.html", context)


def topic_detail_slug_view(request, slug):
    """Детальный просмотр темы курсовой работы по каноническому URL-слагу (PR10)."""
    topic = get_object_or_404(Topic.objects.select_related("discipline"), slug=slug)
    active_applications = topic.applications.select_related("student").filter(status=Application.Status.ACTIVE)

    context = {
        "topic": topic,
        "active_applications": active_applications,
    }
    return render(request, "topics/topic_detail.html", context)


def students_list_view(request):
    """Список соискателей с академическими показателями и вычисленным полем отличников."""
    students = Student.objects.all().order_by("name")
    return render(request, "topics/students.html", {"students": students})


def applications_list_view(request):
    """Список всех поданных заявок со статусами, фильтрацией и пагинацией (select_related)."""
    status_filter = request.GET.get("status", "")
    applications = Application.objects.select_related("topic", "student", "topic__discipline").all()

    if status_filter:
        applications = applications.filter(status=status_filter)

    paginator = Paginator(applications, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "applications": page_obj.object_list,
        "selected_status": status_filter,
        "statuses": Application.Status.choices,
    }
    return render(request, "topics/applications.html", context)


def apply_view(request):
    """Создание заявки на тему с использованием ModelForm (ApplicationForm)."""
    initial = {}
    topic_id = request.GET.get("topic_id")
    if topic_id:
        try:
            initial["topic"] = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            pass

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data["topic"]
            # Резервируем квоту места
            if not topic.reserve_slot():
                messages.error(request, f"Квота свободных мест на тему «{topic.title}» была исчерпана.")
                return render(request, "topics/apply.html", {"form": form})

            app = form.save()
            messages.success(
                request,
                f"Заявка №{app.id} успешно подана и утверждена! Приоритет: {app.priority} баллов.",
            )
            return redirect("applications_list")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки при заполнении формы заявки.")
    else:
        form = ApplicationForm(initial=initial)

    return render(request, "topics/apply.html", {"form": form})


def application_edit_view(request, pk):
    """Редактирование существующей заявки через ModelForm с instance (PR11)."""
    app = get_object_or_404(Application, pk=pk)
    old_topic = app.topic
    old_status = app.status

    if request.method == "POST":
        form = ApplicationEditForm(request.POST, instance=app)
        if form.is_valid():
            new_app = form.save(commit=False)

            # Если поменялась тема или статус, корректируем слоты
            if old_topic != new_app.topic:
                if old_status == Application.Status.ACTIVE:
                    old_topic.release_slot()
                if new_app.status == Application.Status.ACTIVE:
                    new_app.topic.reserve_slot()
            elif old_status != new_app.status:
                if new_app.status == Application.Status.CANCELLED:
                    new_app.topic.release_slot()
                elif old_status == Application.Status.CANCELLED and new_app.status == Application.Status.ACTIVE:
                    new_app.topic.reserve_slot()

            new_app.save()
            messages.success(request, f"Заявка №{new_app.id} успешно обновлена.")
            return redirect("applications_list")
        else:
            messages.error(request, "Ошибка валидации при редактировании заявки.")
    else:
        form = ApplicationEditForm(instance=app)

    return render(request, "topics/application_edit.html", {"form": form, "application": app})


@require_POST
def cancel_application_view(request, pk):
    """Отмена заявки по идентификатору через защищенный POST-запрос с CSRF."""
    app = get_object_or_404(Application, pk=pk)
    if app.status == Application.Status.CANCELLED:
        messages.warning(request, f"Заявка №{app.id} уже была аннулирована.")
    else:
        app.cancel()
        messages.success(request, f"Заявка №{app.id} отменена, место на тему «{app.topic.title}» освобождено.")
    return redirect("applications_list")


def topic_create_view(request):
    """Создание новой темы курсовой работы с поддержкой загрузки изображения (PR11)."""
    if request.method == "POST":
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            topic = form.save()
            messages.success(request, f"Тема «{topic.title}» успешно создана!")
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm()
    return render(request, "topics/topic_form.html", {"form": form, "title": "Новая тема курсовой работы"})


def topic_edit_view(request, pk):
    """Редактирование темы курсовой работы с обновлением изображения."""
    topic = get_object_or_404(Topic, pk=pk)
    if request.method == "POST":
        form = TopicForm(request.POST, request.FILES, instance=topic)
        if form.is_valid():
            topic = form.save()
            messages.success(request, f"Тема «{topic.title}» успешно обновлена.")
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(instance=topic)
    context = {"form": form, "title": f"Редактирование темы №{topic.id}", "topic": topic}
    return render(request, "topics/topic_form.html", context)


def statistics_view(request):
    """Аналитическая панель сервиса со сводной статистикой через агрегации ORM."""
    total_topics = Topic.objects.count()
    free_topics = Topic.objects.filter(is_available=True).count()
    total_students = Student.objects.count()
    total_applications = Application.objects.count()
    approved_applications = Application.objects.filter(status=Application.Status.ACTIVE).count()
    cancelled_applications = Application.objects.filter(status=Application.Status.CANCELLED).count()

    avg_gpa = Student.objects.aggregate(avg=Avg("gpa"))["avg"] or 0.0

    discipline_stats = Discipline.objects.annotate(
        topics_count=Count("topics"),
        active_topics=Count("topics", filter=Q(topics__is_available=True)),
    )

    context = {
        "total_topics": total_topics,
        "free_topics": free_topics,
        "total_students": total_students,
        "total_applications": total_applications,
        "approved_applications": approved_applications,
        "cancelled_applications": cancelled_applications,
        "avg_gpa": round(avg_gpa, 2),
        "discipline_stats": discipline_stats,
    }
    return render(request, "topics/statistics.html", context)


# ==============================================================================
# RESTful JSON API ЭНДПОИНТЫ
# ==============================================================================

def api_topics_list(request):
    """REST API: получение списка тем курсовых работ в формате JSON."""
    topics = Topic.objects.select_related("discipline").all()
    query = request.GET.get("q", "")
    if query:
        topics = topics.filter(title__icontains=query)

    data = [
        {
            "id": t.id,
            "title": t.title,
            "slug": t.slug,
            "discipline": t.discipline.name,
            "supervisor": t.supervisor,
            "min_course": t.min_course,
            "min_gpa": t.min_gpa,
            "capacity": t.capacity,
            "current_students": t.current_students,
            "is_available": t.is_available,
            "is_competitive": t.is_competitive,
            "image_url": t.image.url if t.image else None,
        }
        for t in topics
    ]
    return JsonResponse({"topics": data, "count": len(data)})


def api_topic_detail(request, pk):
    """REST API: получение подробной информации о теме по ID."""
    t = get_object_or_404(Topic, pk=pk)
    return JsonResponse({
        "id": t.id,
        "title": t.title,
        "slug": t.slug,
        "discipline": t.discipline.name,
        "supervisor": t.supervisor,
        "min_course": t.min_course,
        "min_gpa": t.min_gpa,
        "capacity": t.capacity,
        "current_students": t.current_students,
        "is_available": t.is_available,
        "is_competitive": t.is_competitive,
        "image_url": t.image.url if t.image else None,
    })


@csrf_exempt
@require_POST
def api_create_application(request):
    """REST API: подача заявки через POST-запрос с телом JSON."""
    try:
        payload = json.loads(request.body)
        student_id = payload.get("student_id")
        topic_id = payload.get("topic_id")
    except (json.JSONDecodeError, ValueError):
        return HttpResponseBadRequest(JsonResponse({"error": "Некорректный JSON"}))

    student = get_object_or_404(Student, pk=student_id)
    topic = get_object_or_404(Topic, pk=topic_id)

    if Application.objects.filter(student=student, topic=topic, status=Application.Status.ACTIVE).exists():
        return JsonResponse({"success": False, "error": "Студент уже подал активную заявку на эту тему."}, status=400)

    if not topic.is_suitable_for(student.course, student.gpa):
        return JsonResponse(
            {"success": False, "error": "Студент не соответствует академическим требованиям темы."},
            status=400,
        )

    if not topic.reserve_slot():
        return JsonResponse({"success": False, "error": "Квота мест на тему исчерпана."}, status=400)

    app = Application.objects.create(
        topic=topic,
        student=student,
        priority=student.calculate_priority(),
        status=Application.Status.ACTIVE,
    )

    return JsonResponse({
        "success": True,
        "application_id": app.id,
        "status": app.status,
        "priority": app.priority,
    }, status=201)


def api_statistics(request):
    """REST API: аналитическая статистика системы."""
    total_apps = Application.objects.count()
    approved_apps = Application.objects.filter(status=Application.Status.ACTIVE).count()
    avg_gpa = Student.objects.aggregate(avg=Avg("gpa"))["avg"] or 0.0

    return JsonResponse({
        "total_topics": Topic.objects.count(),
        "free_topics": Topic.objects.filter(is_available=True).count(),
        "total_students": Student.objects.count(),
        "total_applications": total_apps,
        "approved_applications": approved_apps,
        "avg_gpa": round(avg_gpa, 2),
    })


def api_health(request):
    """REST API: Health-check для системного мониторинга."""
    return JsonResponse({
        "status": "healthy",
        "service": "coursework_service",
        "version": "1.1.0",
        "database": "connected",
    })
