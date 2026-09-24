"""Тесты для объектной модели Application и взаимодействия объектов."""

from models import Topic, Student, Application
from models.applications import (
    create_application,
    cancel_application,
    is_student_applied,
    get_applications_statistics,
)


def test_application_creation_with_object_links():
    """Проверка создания объекта Application со ссылками на объекты Topic и Student."""
    topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
    student = Student(1, "Студент 1", 3, 4.5, is_budget=True)

    app = Application(
        app_id=101,
        topic=topic,
        student=student,
        application_date="2026-09-24",
    )
    assert app.id == 101
    assert app.topic is topic
    assert app.student is student
    assert app.topic.title == "Тема 1"
    assert app.student.name == "Студент 1"
    assert app.priority == 100
    assert app.status == "ОДОБРЕНА"
    assert app.is_cancelled is False


def test_application_cancel():
    """Проверка метода cancel(), изменения статуса и освобождения места в Topic."""
    topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
    student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
    topic.reserve_slot()

    app = Application(101, topic, student, "2026-09-24")
    assert topic.is_available is False

    # Отмена заявки через метод объекта
    app.cancel()
    assert app.is_cancelled is True
    assert app.status == "ОТМЕНЕНА"
    assert topic.is_available is True
    assert topic.current_students == 0


def test_create_application_logic():
    """Проверка бизнес-логики создания заявки через create_application."""
    topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=1)
    student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
    applications = []

    app = create_application(applications, topic, student)
    assert app is not None
    assert len(applications) == 1
    assert app.topic is topic
    assert topic.current_students == 1
    assert topic.is_available is False


def test_duplicate_application_forbidden():
    """Проверка запрета повторной подачи заявки тем же студентом."""
    topic = Topic(1, "Тема 1", "Фреймворки", "Преподаватель", 3, 3.5, capacity=2)
    student = Student(1, "Студент 1", 3, 4.5, is_budget=True)
    applications = []

    create_application(applications, topic, student)
    assert is_student_applied(applications, student, topic) is True


def test_application_statistics():
    """Проверка расчета агрегированной статистики по заявкам."""
    topic = Topic(1, "Тема 1", "Фреймворки", "Руководитель")
    s1 = Student(1, "Студент 1", 3, 4.0)
    s2 = Student(2, "Студент 2", 3, 5.0)

    app1 = Application(101, topic, s1, "2026-09-24", is_cancelled=False)
    app2 = Application(102, topic, s2, "2026-09-24", is_cancelled=True)

    stats = get_applications_statistics([app1, app2])
    assert stats["total"] == 2
    assert stats["approved"] == 1
    assert stats["cancelled"] == 1
    assert stats["avg_gpa"] == 4.5
