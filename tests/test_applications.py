"""Тесты для модуля applications.py."""

from datetime import date
from applications import (
    validate_student_eligibility,
    calculate_application_priority,
    create_application,
    cancel_application,
    get_applications_statistics,
    is_student_already_applied,
)


def test_validate_student_eligibility():
    """Проверка допуска студента по курсу и среднему баллу."""
    assert validate_student_eligibility(3, 3, 4.5, 3.5) is True
    assert validate_student_eligibility(2, 3, 4.5, 3.5) is False
    assert validate_student_eligibility(3, 3, 3.2, 3.5) is False


def test_calculate_application_priority():
    """Проверка расчета приоритета заявки."""
    # GPA 4.5 * 20 = 90 + 10 (бюджет) = 100
    assert calculate_application_priority(4.5, is_budget=True) == 100
    # GPA 4.0 * 20 = 80 + 0 (договор) = 80
    assert calculate_application_priority(4.0, is_budget=False) == 80


def test_create_application_success():
    """Проверка успешного создания заявки и уменьшения квоты темы."""
    applications = []
    topics = {
        1: {
            "id": 1,
            "title": "Тестовая тема",
            "discipline": "Тестовая дисциплина",
            "supervisor": "Тестов Т. Т.",
            "min_course": 3,
            "min_gpa": 3.5,
            "capacity": 1,
            "current_students": 0,
            "is_available": True,
        }
    }
    app = create_application(
        applications=applications,
        topics=topics,
        topic_id=1,
        student_name="Иванов И. И.",
        student_course=3,
        gpa=4.6,
        is_budget=True,
        app_date=date(2026, 9, 24),
    )
    assert len(applications) == 1
    assert app["id"] == 101
    assert app["status"] == "ОДОБРЕНА"
    assert topics[1]["current_students"] == 1
    assert topics[1]["is_available"] is False


def test_duplicate_application_forbidden():
    """Проверка запрета повторной подачи заявки тем же студентом на ту же тему."""
    applications = [
        {
            "id": 101,
            "topic_id": 1,
            "student_name": "Иванов И. И.",
            "status": "ОДОБРЕНА",
        }
    ]
    assert is_student_already_applied(applications, "Иванов И. И.", 1) is True
    assert is_student_already_applied(applications, "Петров П. П.", 1) is False


def test_cancel_application():
    """Проверка отмены заявки и освобождения темы."""
    applications = [
        {
            "id": 101,
            "topic_id": 1,
            "student_name": "Иванов И. И.",
            "status": "ОДОБРЕНА",
        }
    ]
    topics = {
        1: {
            "id": 1,
            "capacity": 1,
            "current_students": 1,
            "is_available": False,
        }
    }
    assert cancel_application(applications, topics, 101) is True
    assert applications[0]["status"] == "ОТМЕНЕНА"
    assert topics[1]["current_students"] == 0
    assert topics[1]["is_available"] is True


def test_get_applications_statistics():
    """Проверка вычисления агрегированной статистики по заявкам."""
    apps = [
        {"id": 101, "gpa": 4.0, "status": "ОДОБРЕНА"},
        {"id": 102, "gpa": 5.0, "status": "ОДОБРЕНА"},
        {"id": 103, "gpa": 3.0, "status": "ОТМЕНЕНА"},
    ]
    stats = get_applications_statistics(apps)
    assert stats["total"] == 3
    assert stats["approved"] == 2
    assert stats["cancelled"] == 1
    assert stats["avg_gpa"] == 4.0
