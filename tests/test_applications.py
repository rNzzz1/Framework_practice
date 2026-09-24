"""Тесты для объектной модели Application и взаимодействия объектов."""

import unittest
from models import Topic, Student, Application
from models.applications import (
    create_application,
    cancel_application,
    is_student_applied,
    get_applications_statistics,
)


class TestApplicationModel(unittest.TestCase):
    """Набор тестов для сущности Application и ее взаимодействия с Topic и Student."""

    def test_application_creation_with_object_links(self):
        """Проверка создания объекта Application со ссылками на объекты Topic и Student."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
        student = Student(1, "Студент 1", 3, 4.5, is_budget=True)

        app = Application(
            app_id=101,
            topic=topic,
            student=student,
            application_date="2026-09-24",
        )
        self.assertEqual(app.id, 101)
        self.assertIs(app.topic, topic)
        self.assertIs(app.student, student)
        self.assertEqual(app.topic.title, "Тема 1")
        self.assertEqual(app.student.name, "Студент 1")
        self.assertEqual(app.priority, 100)
        self.assertEqual(app.status, "ОДОБРЕНА")
        self.assertFalse(app.is_cancelled)

    def test_application_cancel(self):
        """Проверка метода cancel(), изменения статуса и освобождения места в Topic."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
        student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
        topic.reserve_slot()

        app = Application(101, topic, student, "2026-09-24")
        self.assertFalse(topic.is_available)

        # Отмена заявки через метод объекта
        app.cancel()
        self.assertTrue(app.is_cancelled)
        self.assertEqual(app.status, "ОТМЕНЕНА")
        self.assertTrue(topic.is_available)
        self.assertEqual(topic.current_students, 0)

    def test_create_application_logic(self):
        """Проверка бизнес-логики создания заявки через create_application."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
        student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
        applications = []

        app = create_application(applications, topic, student)
        self.assertIsNotNone(app)
        self.assertEqual(len(applications), 1)
        self.assertIs(app.topic, topic)
        self.assertEqual(topic.current_students, 1)
        self.assertFalse(topic.is_available)

    def test_duplicate_application_forbidden(self):
        """Проверка запрета повторной подачи заявки тем же студентом."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=2)
        student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
        applications = []

        create_application(applications, topic, student)
        self.assertTrue(is_student_applied(applications, student, topic))

    def test_application_statistics(self):
        """Проверка расчета агрегированной статистики по заявкам."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Руководитель")
        s1 = Student(1, "Студент 1", 3, 4.0)
        s2 = Student(2, "Студент 2", 3, 5.0)

        app1 = Application(101, topic, s1, "2026-09-24", is_cancelled=False)
        app2 = Application(102, topic, s2, "2026-09-24", is_cancelled=True)

        stats = get_applications_statistics([app1, app2])
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["approved"], 1)
        self.assertEqual(stats["cancelled"], 1)
        self.assertEqual(stats["avg_gpa"], 4.5)

    def test_cancel_application_helper(self):
        """Проверка вспомогательной функции cancel_application."""
        topic = Topic(1, "Тема 1", "Фреймворки", "Руководитель", capacity=1)
        student = Student(1, "Студент 1", 3, 4.0)
        app = Application(101, topic, student, "2026-09-24")
        topic.reserve_slot()

        apps = [app]
        self.assertTrue(cancel_application(apps, 101))
        self.assertTrue(app.is_cancelled)
        self.assertFalse(cancel_application(apps, 999))


if __name__ == "__main__":
    unittest.main()
