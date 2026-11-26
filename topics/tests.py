"""Комплексные автоматизированные тесты для ПР9, ПР10 и ПР11 сервиса выбора тем курсовых работ.

Охватывает:
- ПР9: ORM-модели, связи ForeignKey, кастомные методы моделей, целостность данных
- ПР10: Кастомный QuerySet/Manager, SlugField, GeneratedField, Django Admin регистрация и действия
- ПР11: Валидация форм (TopicFilterForm, ApplicationForm, ApplicationEditForm с instance, TopicForm)
- HTML-представления, пагинация, контекстный процессор и RESTful API
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.admin.sites import site

from .models import Discipline, Student, Topic, Application
from .forms import TopicFilterForm, ApplicationForm, ApplicationEditForm, TopicForm


class ModelAndORMTestCase(TestCase):
    """Тестирование моделей данных Django ORM (ПР9 и ПР10)."""

    def setUp(self):
        self.discipline = Discipline.objects.create(
            name="Технологии разработки приложений на базе фреймворков",
            code="TRAPBF-01",
        )
        self.student = Student.objects.create(
            name="Узунян Овсеп Норайрович",
            course=3,
            gpa=4.8,
            is_budget=True,
            email="uzunyan.o.n@mirea.ru",
        )
        self.topic = Topic.objects.create(
            title="Разработка микросервисной архитектуры на Django",
            discipline=self.discipline,
            supervisor="доц. Ящун Т.В.",
            min_course=3,
            min_gpa=4.0,
            capacity=2,
            current_students=0,
            is_available=True,
        )

    def test_student_priority_and_honor_generated_field(self):
        """Проверка формулы приоритета и вычисленного поля GeneratedField (is_honor_student)."""
        self.assertEqual(self.student.calculate_priority(), 106)
        self.student.refresh_from_db()
        # GPA 4.8 >= 4.5 -> True
        self.assertTrue(self.student.is_honor_student)

        # Проверка контрактника
        self.student.is_budget = False
        self.student.save()
        self.assertEqual(self.student.calculate_priority(), 96)

    def test_topic_slug_generation_and_competitive_generated_field(self):
        """Проверка автоматической генерации слага и флага is_competitive."""
        self.topic.refresh_from_db()
        self.assertTrue(len(self.topic.slug) > 0)
        self.assertIn("django", self.topic.slug)
        self.assertEqual(self.topic.get_absolute_url(), f"/topic/slug/{self.topic.slug}/")
        # capacity=2 > 1 -> is_competitive=True
        self.assertTrue(self.topic.is_competitive)

    def test_topic_suitability_check(self):
        """Проверка академического соответствия соискателя требованиям темы."""
        self.assertTrue(self.topic.is_suitable_for(student_course=3, gpa=4.8))
        self.assertFalse(self.topic.is_suitable_for(student_course=2, gpa=4.8))
        self.assertFalse(self.topic.is_suitable_for(student_course=3, gpa=3.8))

    def test_slot_reservation_and_release(self):
        """Проверка квотирования и резервирования мест."""
        self.assertTrue(self.topic.has_free_capacity())
        self.assertTrue(self.topic.reserve_slot())

        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 1)
        self.assertTrue(self.topic.is_available)

        # Резервируем второй слот (квота = 2)
        self.assertTrue(self.topic.reserve_slot())
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 2)
        self.assertFalse(self.topic.is_available)

        # Освобождение слота
        self.topic.release_slot()
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 1)
        self.assertTrue(self.topic.is_available)

    def test_application_manager_and_cancellation(self):
        """Проверка кастомного менеджера Application (active, cancelled) и отмены."""
        app = Application.objects.create(student=self.student, topic=self.topic)
        self.assertEqual(app.status, Application.Status.ACTIVE)
        self.assertFalse(app.is_cancelled)

        self.assertEqual(Application.objects.active().count(), 1)
        self.assertEqual(Application.objects.cancelled().count(), 0)

        # Отмена заявки
        app.cancel()
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.CANCELLED)
        self.assertTrue(app.is_cancelled)
        self.assertEqual(Application.objects.cancelled().count(), 1)
        self.assertEqual(Application.objects.active().count(), 0)


class FormsTestCase(TestCase):
    """Тестирование форм Django (ПР11: TopicFilterForm, ApplicationForm, ApplicationEditForm, TopicForm)."""

    def setUp(self):
        self.discipline = Discipline.objects.create(name="Веб-технологии", code="WEB-01")
        self.student = Student.objects.create(
            name="Иванов Иван",
            course=3,
            gpa=4.5,
            is_budget=True,
            email="ivanov@mirea.ru",
        )
        self.topic = Topic.objects.create(
            title="Интеграция Django с внешними API",
            discipline=self.discipline,
            supervisor="доц. Ящун Т.В.",
            min_course=3,
            min_gpa=4.0,
            capacity=1,
            is_available=True,
        )

    def test_topic_filter_form_valid(self):
        """Проверка формы фильтрации каталога тем."""
        form = TopicFilterForm(
            data={"q": "Django", "discipline": self.discipline.id, "min_course": "3", "sort": "title"}
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["q"], "Django")

    def test_application_form_valid(self):
        """Проверка успешной валидации создания заявки."""
        form = ApplicationForm(data={"student": self.student.id, "topic": self.topic.id})
        self.assertTrue(form.is_valid())

    def test_application_form_academic_mismatch(self):
        """Проверка блокировки подачи заявки при нехватке среднего балла."""
        low_gpa_student = Student.objects.create(name="Слабый Студент", course=3, gpa=3.2, email="weak@mirea.ru")
        form = ApplicationForm(data={"student": low_gpa_student.id, "topic": self.topic.id})
        self.assertFalse(form.is_valid())
        self.assertIn("не соответствует академическим требованиям", str(form.errors))

    def test_application_form_duplicate_check(self):
        """Проверка запрета повторной активной заявки на одну и ту же тему."""
        Application.objects.create(student=self.student, topic=self.topic, status=Application.Status.ACTIVE)
        form = ApplicationForm(data={"student": self.student.id, "topic": self.topic.id})
        self.assertFalse(form.is_valid())
        self.assertIn("уже имеет активную", str(form.errors))

    def test_application_edit_form_instance_exclude(self):
        """Проверка корректной работы instance в ApplicationEditForm без ложного срабатывания дубликата."""
        app = Application.objects.create(student=self.student, topic=self.topic, status=Application.Status.ACTIVE)
        form = ApplicationEditForm(
            data={"student": self.student.id, "topic": self.topic.id, "status": Application.Status.ACTIVE},
            instance=app,
        )
        self.assertTrue(form.is_valid())

    def test_topic_form_with_image(self):
        """Проверка формы создания темы с загрузкой файла изображения (Pillow)."""
        # 1x1 пиксель gif/png
        image_data = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
            b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )
        image_file = SimpleUploadedFile("test_topic.gif", image_data, content_type="image/gif")

        form = TopicForm(
            data={
                "title": "Новая тема с изображением",
                "discipline": self.discipline.id,
                "supervisor": "Ящун Т.В.",
                "min_course": 3,
                "min_gpa": 3.8,
                "capacity": 2,
                "is_available": True,
            },
            files={"image": image_file},
        )
        self.assertTrue(form.is_valid())
        topic = form.save()
        self.assertTrue(bool(topic.image))


class ViewsAndAdminTestCase(TestCase):
    """Тестирование представлений веб-интерфейса, контекстных процессоров и админки (ПР10)."""

    def setUp(self):
        self.client = Client()
        self.discipline = Discipline.objects.create(name="Архитектура ИС", code="AIS-01")
        self.student = Student.objects.create(name="Смирнов Алексей", course=3, gpa=4.7, email="smirnov@mirea.ru")
        self.topic = Topic.objects.create(
            title="Проектирование микросервисов",
            discipline=self.discipline,
            supervisor="Ящун Т.В.",
            min_course=3,
            min_gpa=4.0,
            capacity=2,
            is_available=True,
        )

    def test_context_processor(self):
        """Проверка доступности глобальных переменных контекстного процессора в шаблоне."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("site_name", response.context)
        self.assertIn("topics_total_count", response.context)
        self.assertEqual(response.context["topics_total_count"], 1)

    def test_topic_detail_slug_view(self):
        """Проверка отображения темы по каноническому слагу."""
        response = self.client.get(reverse("topic_detail_slug", kwargs={"slug": self.topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.title)

    def test_apply_view_post_success(self):
        """Проверка подачи заявки через view с валидацией ModelForm."""
        response = self.client.post(reverse("apply"), {"student": self.student.id, "topic": self.topic.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Application.objects.filter(student=self.student, topic=self.topic).exists())

    def test_cancel_application_post_only(self):
        """Проверка отмены заявки через POST-метод."""
        app = Application.objects.create(student=self.student, topic=self.topic)
        self.topic.reserve_slot()

        response = self.client.post(reverse("cancel_application", args=[app.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, Application.Status.CANCELLED)

    def test_admin_registration(self):
        """Проверка регистрации моделей в Django Admin."""
        self.assertIn(Discipline, site._registry)
        self.assertIn(Student, site._registry)
        self.assertIn(Topic, site._registry)
        self.assertIn(Application, site._registry)
