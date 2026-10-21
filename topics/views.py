"""Контроллеры (views) веб-приложения сервиса выбора тем курсовых работ.

Включает:
- HTML-представления (каталог, детали, студенты, заявки, подача, отмена, статистика)
- RESTful JSON API эндпоинты (список тем, подача заявки, статистика, health-check)
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Q

from .models import Discipline, Student, Topic, Application


# ==============================================================================
# HTML ВЕБ-СТРАНИЦЫ (ПР5 / ПР6)
# ==============================================================================

def index_view(request):
    """Главная страница: каталог тем курсовых работ с поиском и фильтрацией."""
    query = request.GET.get("q", "").strip()
    discipline_id = request.GET.get("discipline", "")

    topics = Topic.objects.select_related("discipline").all()

    if query:
        topics = topics.filter(
            Q(title__icontains=query)
            | Q(supervisor__icontains=query)
            | Q(discipline__name__icontains=query)
        )

    if discipline_id:
        topics = topics.filter(discipline_id=discipline_id)

    disciplines = Discipline.objects.all()

    context = {
        "topics": topics,
        "disciplines": disciplines,
        "selected_discipline": discipline_id,
        "query": query,
    }
    return render(request, "topics/index.html", context)


def topic_detail_view(request, pk):
    """Детальный просмотр темы курсовой работы и поданных заявок."""
    topic = get_object_or_404(Topic.objects.select_related("discipline"), pk=pk)
    active_applications = topic.applications.select_related("student").filter(is_cancelled=False)

    context = {
        "topic": topic,
        "active_applications": active_applications,
    }
    return render(request, "topics/topic_detail.html", context)


def students_list_view(request):
    """Список соискателей с академическими показателями."""
    students = Student.objects.all().order_by("name")
    return render(request, "topics/students.html", {"students": students})


def applications_list_view(request):
    """Список всех поданных заявок со статусами и кнопкой отмены."""
    applications = Application.objects.select_related("topic", "student", "topic__discipline").all()
    return render(request, "topics/applications.html", {"applications": applications})


def apply_view(request):
    """Страница и форма подачи заявки на закрепление темы."""
    if request.method == "POST":
        student_id = request.POST.get("student")
        topic_id = request.POST.get("topic")

        if not student_id or not topic_id:
            messages.error(request, "Необходимо выбрать студента и тему курсовой работы.")
            return redirect("apply")

        student = get_object_or_404(Student, pk=student_id)
        topic = get_object_or_404(Topic, pk=topic_id)

        # 1. Проверка повторной подачи
        if Application.objects.filter(student=student, topic=topic, is_cancelled=False).exists():
            messages.error(request, f"Студент {student.name} уже подал активную заявку на данную тему.")
            return redirect("apply")

        # 2. Проверка академического допуска
        if not topic.is_suitable_for(student.course, student.gpa):
            messages.error(
                request,
                f"Студент {student.name} не соответствует требованиям темы "
                f"(требуется курс >= {topic.min_course}, GPA >= {topic.min_gpa:.2f}).",
            )
            return redirect("apply")

        # 3. Проверка квоты мест
        if not topic.reserve_slot():
            messages.error(request, f"На тему «{topic.title}» исчерпана квота свободных мест.")
            return redirect("apply")

        # 4. Создание заявки
        app = Application.objects.create(
            topic=topic,
            student=student,
            priority=student.calculate_priority(),
            is_cancelled=False,
        )

        messages.success(
            request,
            f"Заявка №{app.id} успешно подана и утверждена! Приоритет соискателя: {app.priority} баллов.",
        )
        return redirect("applications_list")

    students = Student.objects.all().order_by("name")
    topics = Topic.objects.filter(is_available=True).order_by("title")
    selected_topic_id = request.GET.get("topic_id")

    return render(
        request,
        "topics/apply.html",
        {
            "students": students,
            "topics": topics,
            "selected_topic_id": int(selected_topic_id) if selected_topic_id else None,
        },
    )


@require_POST
def cancel_application_view(request, pk):
    """Отмена заявки по идентификатору."""
    app = get_object_or_404(Application, pk=pk)
    if app.is_cancelled:
        messages.warning(request, f"Заявка №{app.id} уже была отменена ранее.")
    else:
        app.cancel()
        messages.success(request, f"Заявка №{app.id} отменена, место на тему «{app.topic.title}» освобождено.")
    return redirect("applications_list")


def statistics_view(request):
    """Аналитическая панель сервиса со сводной статистикой."""
    total_topics = Topic.objects.count()
    free_topics = Topic.objects.filter(is_available=True).count()
    total_students = Student.objects.count()
    total_applications = Application.objects.count()
    approved_applications = Application.objects.filter(is_cancelled=False).count()
    cancelled_applications = Application.objects.filter(is_cancelled=True).count()

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
# RESTful JSON API ЭНДПОИНТЫ (ПР5 / ПР6 / ПР7)
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
            "discipline": t.discipline.name,
            "supervisor": t.supervisor,
            "min_course": t.min_course,
            "min_gpa": t.min_gpa,
            "capacity": t.capacity,
            "current_students": t.current_students,
            "is_available": t.is_available,
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
        "discipline": t.discipline.name,
        "supervisor": t.supervisor,
        "min_course": t.min_course,
        "min_gpa": t.min_gpa,
        "capacity": t.capacity,
        "current_students": t.current_students,
        "is_available": t.is_available,
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

    if Application.objects.filter(student=student, topic=topic, is_cancelled=False).exists():
        return JsonResponse({"success": False, "error": "Студент уже подал активную заявку на эту тему."}, status=400)

    if not topic.is_suitable_for(student.course, student.gpa):
        return JsonResponse({"success": False, "error": "Студент не соответствует требованиям темы."}, status=400)

    if not topic.reserve_slot():
        return JsonResponse({"success": False, "error": "Квота мест на тему исчерпана."}, status=400)

    app = Application.objects.create(
        topic=topic,
        student=student,
        priority=student.calculate_priority(),
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
    approved_apps = Application.objects.filter(is_cancelled=False).count()
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
    """REST API: Health-check для мониторинга доступности сервера (DevOps / ПР7)."""
    return JsonResponse({
        "status": "healthy",
        "service": "coursework_service",
        "version": "1.0.0",
        "database": "connected",
    })
