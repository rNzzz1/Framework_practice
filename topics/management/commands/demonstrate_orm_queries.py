"""Management-команда для демонстрации 15+ типовых выражений Django ORM (ПР9 и ПР10)."""

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q
from topics.models import Discipline, Student, Topic, Application


class Command(BaseCommand):
    help = "Демонстрирует выполнение 15+ выражений Django ORM"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== ДЕМОНСТРАЦИЯ 15+ ОПЕРАЦИЙ DJANGO ORM ==="))

        # 1. all()
        all_topics = Topic.objects.all()
        self.stdout.write(f"1. all(): Получено {all_topics.count()} тем")

        # 2. filter()
        avail_topics = Topic.objects.filter(is_available=True)
        self.stdout.write(f"2. filter(is_available=True): {avail_topics.count()} свободных тем")

        # 3. exclude()
        non_cancelled_apps = Application.objects.exclude(status=Application.Status.CANCELLED)
        self.stdout.write(f"3. exclude(status=CANCELLED): {non_cancelled_apps.count()} неотмененных заявок")

        # 4. order_by()
        sorted_students = Student.objects.order_by("-gpa")
        top_s = sorted_students.first()
        self.stdout.write(f"4. order_by('-gpa'): Топ студент — {top_s.name} (GPA {top_s.gpa})")

        # 5. get()
        first_topic = Topic.objects.get(pk=1)
        self.stdout.write(f"5. get(pk=1): {first_topic.title[:35]}...")

        # 6. values()
        topic_vals = Topic.objects.values("id", "title")[:2]
        self.stdout.write(f"6. values('id', 'title'): {list(topic_vals)}")

        # 7. values_list()
        student_emails = Student.objects.values_list("email", flat=True)[:3]
        self.stdout.write(f"7. values_list('email', flat=True): {list(student_emails)}")

        # 8. select_related() (исключение N+1 запросов)
        apps_with_relations = Application.objects.select_related("topic", "student", "topic__discipline")[:3]
        for a in apps_with_relations:
            self.stdout.write(
                f"8. select_related(): Заявка #{a.id} -> {a.student.name} "
                f"выбрал {a.topic.title[:20]} ({a.topic.discipline.name})"
            )

        # 9. Q-объекты (сложная логика ИЛИ / И)
        q_filter = Topic.objects.filter(Q(capacity__gt=1) | Q(min_gpa__gte=4.5))
        self.stdout.write(f"9. Q(capacity__gt=1) | Q(min_gpa__gte=4.5): найдено {q_filter.count()} тем")

        # 10. aggregate() с Avg и Max
        gpa_stats = Student.objects.aggregate(avg_gpa=Avg("gpa"), max_gpa=Max("gpa"), min_gpa=Min("gpa"))
        self.stdout.write(f"10. aggregate(Avg, Max, Min): {gpa_stats}")

        # 11. annotate() с Count и фильтрацией
        disc_annotated = Discipline.objects.annotate(
            total_topics=Count("topics"),
            active_topics=Count("topics", filter=Q(topics__is_available=True)),
        )
        disc_summary = [(d.name[:15], d.total_topics, d.active_topics) for d in disc_annotated]
        self.stdout.write(f"11. annotate(Count): {disc_summary}")

        # 12. exists()
        has_apps = Application.objects.filter(status=Application.Status.ACTIVE).exists()
        self.stdout.write(f"12. exists(): Есть ли активные заявки? {has_apps}")

        # 13. count()
        total_students = Student.objects.count()
        self.stdout.write(f"13. count(): Всего студентов — {total_students}")

        # 14. Paginator (постраничный вывод)
        paginator = Paginator(Topic.objects.all().order_by("id"), 2)
        page1 = paginator.get_page(1)
        self.stdout.write(f"14. Paginator: Страниц всего: {paginator.num_pages}, объектов на стр. 1: {len(page1)}")

        # 15. Кастомный QuerySet менеджер: active(), cancelled(), completed()
        active_apps = Application.objects.active()
        cancelled_apps = Application.objects.cancelled()
        self.stdout.write(f"15. Custom QuerySet: active()={active_apps.count()}, cancelled()={cancelled_apps.count()}")

        # 16. GeneratedField: вычисленные поля в БД
        honor_students = Student.objects.filter(is_honor_student=True)
        competitive_topics = Topic.objects.filter(is_competitive=True)
        self.stdout.write(
            f"16. GeneratedField: отличников={honor_students.count()}, командных тем={competitive_topics.count()}"
        )

        self.stdout.write(self.style.SUCCESS("Все 16 ORM-операций успешно выполнены!"))
