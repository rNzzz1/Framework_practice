"""Комплексные тесты моделей, представлений и REST API сервиса выбора тем курсовых работ."""

import json
from django.test import TestCase, Client
from django.urls import reverse

from .models import Discipline, Student, Topic, Application


class ModelTestCase(TestCase):
    """Тестирование бизнес-логики моделей данных."""

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
            capacity=1,
            current_students=0,
            is_available=True,
        )

    def test_student_priority_calculation(self):
        """Проверка формулы расчета приоритета студента."""
        # priority = int(4.8 * 20) + 10 = 96 + 10 = 106
        self.assertEqual(self.student.calculate_priority(), 106)

        # Контрактный студент без бонуса в 10 баллов
        self.student.is_budget = False
        self.assertEqual(self.student.calculate_priority(), 96)

    def test_topic_suitability_check(self):
        """Проверка проверки академических требований темы."""
        # Подходящий студент (3 курс, GPA 4.8 >= 4.0)
        self.assertTrue(self.topic.is_suitable_for(student_course=3, gpa=4.8))
        # Слишком младший курс
        self.assertFalse(self.topic.is_suitable_for(student_course=2, gpa=4.8))
        # Слишком низкий средний балл
        self.assertFalse(self.topic.is_suitable_for(student_course=3, gpa=3.8))

    def test_slot_reservation_and_release(self):
        """Проверка квотирования и резервирования мест."""
        self.assertTrue(self.topic.has_free_capacity())
        self.assertTrue(self.topic.reserve_slot())

        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 1)
        self.assertFalse(self.topic.is_available)
        self.assertFalse(self.topic.has_free_capacity())

        # Повторная попытка резерва должна вернуть False
        self.assertFalse(self.topic.reserve_slot())

        # Освобождение места
        self.topic.release_slot()
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 0)
        self.assertTrue(self.topic.is_available)
        self.assertTrue(self.topic.has_free_capacity())

    def test_application_creation_and_cancellation(self):
        """Проверка создания и аннулирования заявки."""
        app = Application.objects.create(
            student=self.student,
            topic=self.topic,
        )
        self.assertEqual(app.priority, 106)
        self.assertEqual(app.status, "ОДОБРЕНА")

        # Резервируем место
        self.topic.reserve_slot()
        self.assertEqual(self.topic.current_students, 1)

        # Отменяем заявку
        app.cancel()
        self.assertTrue(app.is_cancelled)
        self.assertEqual(app.status, "ОТМЕНЕНА")

        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 0)
        self.assertTrue(self.topic.is_available)


class ViewsTestCase(TestCase):
    """Тестирование HTML-представлений веб-интерфейса."""

    def setUp(self):
        self.client = Client()
        self.discipline = Discipline.objects.create(
            name="Базы данных",
            code="BD-02",
        )
        self.student = Student.objects.create(
            name="Иванов Иван Иванович",
            course=3,
            gpa=4.5,
            is_budget=True,
            email="ivanov@mirea.ru",
        )
        self.topic = Topic.objects.create(
            title="Оптимизация запросов PostgreSQL",
            discipline=self.discipline,
            supervisor="ст. преп. Макиевский С.Е.",
            min_course=3,
            min_gpa=4.0,
            capacity=2,
            current_students=0,
            is_available=True,
        )

    def test_index_view_status_code_and_content(self):
        """Проверка главной страницы каталога тем."""
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог тем курсовых работ")
        self.assertContains(response, "Оптимизация запросов PostgreSQL")

    def test_topic_detail_view(self):
        """Проверка страницы с деталями конкретной темы."""
        response = self.client.get(reverse("topic_detail", args=[self.topic.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Оптимизация запросов PostgreSQL")
        self.assertContains(response, "Макиевский С.Е.")

    def test_students_list_view(self):
        """Проверка страницы списка студентов."""
        response = self.client.get(reverse("students_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Иванов Иван Иванович")

    def test_applications_list_view(self):
        """Проверка журнала заявок."""
        response = self.client.get(reverse("applications_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Журнал поданных заявок")

    def test_statistics_view(self):
        """Проверка аналитической панели."""
        response = self.client.get(reverse("statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Аналитическая панель сервиса")

    def test_apply_view_post_successful(self):
        """Проверка успешной подачи заявки через веб-форму."""
        response = self.client.post(
            reverse("apply"),
            {"student": self.student.id, "topic": self.topic.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Application.objects.filter(student=self.student, topic=self.topic).exists())

        self.topic.refresh_from_db()
        self.assertEqual(self.topic.current_students, 1)

    def test_apply_view_post_unsuitable_student(self):
        """Проверка блокировки подачи заявки при несоответствии критериям."""
        low_gpa_student = Student.objects.create(
            name="Петров Петр",
            course=2,
            gpa=3.0,
            is_budget=False,
            email="petrov@mirea.ru",
        )
        response = self.client.post(
            reverse("apply"),
            {"student": low_gpa_student.id, "topic": self.topic.id},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Application.objects.filter(student=low_gpa_student, topic=self.topic).exists())

    def test_cancel_application_view(self):
        """Проверка отзыва заявки пользователем."""
        app = Application.objects.create(student=self.student, topic=self.topic)
        self.topic.reserve_slot()

        response = self.client.post(reverse("cancel_application", args=[app.id]), follow=True)
        self.assertEqual(response.status_code, 200)

        app.refresh_from_db()
        self.assertTrue(app.is_cancelled)


class ApiTestCase(TestCase):
    """Тестирование RESTful JSON API сервиса."""

    def setUp(self):
        self.client = Client()
        self.discipline = Discipline.objects.create(
            name="Архитектура корпоративных ИС",
            code="AKIS-03",
        )
        self.student = Student.objects.create(
            name="Сидоров Сидор",
            course=4,
            gpa=4.6,
            is_budget=True,
            email="sidorov@mirea.ru",
        )
        self.topic = Topic.objects.create(
            title="Проектирование сервисно-ориентированной архитектуры",
            discipline=self.discipline,
            supervisor="доц. Ящун Т.В.",
            min_course=4,
            min_gpa=4.2,
            capacity=1,
            current_students=0,
            is_available=True,
        )

    def test_api_health_check(self):
        """Проверка системного мониторинга health-check (ПР7)."""
        response = self.client.get(reverse("api_health"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["service"], "coursework_service")

    def test_api_topics_list(self):
        """Проверка эндпоинта получения каталога тем в JSON."""
        response = self.client.get(reverse("api_topics_list"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("topics", data)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["topics"][0]["title"], "Проектирование сервисно-ориентированной архитектуры")

    def test_api_create_application_success(self):
        """Проверка успешной подачи заявки через JSON REST API."""
        payload = {
            "student_id": self.student.id,
            "topic_id": self.topic.id,
        }
        response = self.client.post(
            reverse("api_create_application"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        res_data = response.json()
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["status"], "ОДОБРЕНА")

    def test_api_create_application_quota_exceeded(self):
        """Проверка ошибки исчерпания квоты при вызове REST API."""
        # Занимаем единственный слот
        self.topic.reserve_slot()

        payload = {
            "student_id": self.student.id,
            "topic_id": self.topic.id,
        }
        response = self.client.post(
            reverse("api_create_application"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        res_data = response.json()
        self.assertFalse(res_data["success"])
        self.assertIn("исчерпана", res_data["error"])

    def test_api_statistics(self):
        """Проверка REST API аналитики."""
        response = self.client.get(reverse("api_statistics"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_topics", data)
        self.assertIn("total_students", data)
        self.assertIn("total_applications", data)
        self.assertEqual(data["total_topics"], 1)
