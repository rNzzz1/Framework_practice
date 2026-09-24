"""Модуль управления заявками на темы курсовых работ."""

from datetime import date
from typing import Dict, Any, List, Optional


def validate_student_eligibility(
    student_course: int,
    required_course: int,
    gpa: float,
    min_gpa: float,
) -> bool:
    """Проверяет допуск студента по курсу и GPA (преемственность ПР1)."""
    return (student_course >= required_course) and (gpa >= min_gpa)


def calculate_application_priority(gpa: float, is_budget: bool) -> int:
    """Рассчитывает числовой приоритет заявки (преемственность ПР1)."""
    base_priority = int(gpa * 20)
    bonus = 10 if is_budget else 0
    return base_priority + bonus


def is_student_already_applied(
    applications: List[Dict[str, Any]],
    student_name: str,
    topic_id: int,
) -> bool:
    """Проверяет, подавал ли студент уже заявку на указанную тему."""
    target_name = student_name.strip().lower()
    for app in applications:
        if (
            app["student_name"].strip().lower() == target_name
            and app["topic_id"] == topic_id
            and app.get("status") != "ОТМЕНЕНА"
        ):
            return True
    return False


def create_application(
    applications: List[Dict[str, Any]],
    topics: Dict[int, Dict[str, Any]],
    topic_id: int,
    student_name: str,
    student_course: int,
    gpa: float,
    is_budget: bool,
    app_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Создает новую заявку на курсовую работу с проверкой условий.

    Raises:
        ValueError: Если тема не найдена, студент не допущен или тема недоступна.
    """
    if topic_id not in topics:
        raise ValueError(f"Тема с ID {topic_id} не найдена в системе.")

    topic = topics[topic_id]

    # Проверка повторной подачи
    if is_student_already_applied(applications, student_name, topic_id):
        raise ValueError(
            f"Студент {student_name} уже подал активную заявку на тему №{topic_id}."
        )

    # Проверка академического допуска студента
    is_eligible = validate_student_eligibility(
        student_course=student_course,
        required_course=topic["min_course"],
        gpa=gpa,
        min_gpa=topic["min_gpa"],
    )
    if not is_eligible:
        raise ValueError(
            f"Студент не соответствует требованиям темы (требуется курс >= "
            f"{topic['min_course']}, GPA >= {topic['min_gpa']})."
        )

    # Проверка квоты свободных мест на тему
    if topic["current_students"] >= topic["capacity"] or not topic["is_available"]:
        raise ValueError("На выбранную тему исчерпана квота или тема недоступна.")

    # Генерация ID и даты
    new_id = (
        max((app["id"] for app in applications), default=100) + 1
        if applications else 101
    )
    current_date = app_date or date.today()
    priority = calculate_application_priority(gpa, is_budget)

    new_application: Dict[str, Any] = {
        "id": new_id,
        "topic_id": topic_id,
        "student_name": student_name.strip(),
        "student_course": student_course,
        "gpa": round(gpa, 2),
        "is_budget": is_budget,
        "application_date": current_date.isoformat(),
        "priority": priority,
        "status": "ОДОБРЕНА",
    }

    # Обновление состояния темы
    topic["current_students"] += 1
    if topic["current_students"] >= topic["capacity"]:
        topic["is_available"] = False

    applications.append(new_application)
    return new_application


def cancel_application(
    applications: List[Dict[str, Any]],
    topics: Dict[int, Dict[str, Any]],
    application_id: int,
) -> bool:
    """Отменяет заявку по идентификатору и освобождает место в теме."""
    for app in applications:
        if app["id"] == application_id:
            if app.get("status") == "ОТМЕНЕНА":
                return False

            app["status"] = "ОТМЕНЕНА"
            topic_id = app["topic_id"]
            if topic_id in topics:
                topic = topics[topic_id]
                topic["current_students"] = max(0, topic["current_students"] - 1)
                topic["is_available"] = True
            return True
    return False


def get_applications_statistics(
    applications: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Вычисляет сводную статистику по поданным заявкам."""
    total = len(applications)
    approved = sum(1 for app in applications if app.get("status") == "ОДОБРЕНА")
    cancelled = sum(1 for app in applications if app.get("status") == "ОТМЕНЕНА")

    avg_gpa = (
        round(sum(app["gpa"] for app in applications) / total, 2)
        if total > 0 else 0.0
    )

    return {
        "total": total,
        "approved": approved,
        "cancelled": cancelled,
        "avg_gpa": avg_gpa,
    }


def format_application_summary(
    app_id: int,
    student_name: str,
    topic_title: str,
    discipline_name: str,
    app_date_str: str,
    status_text: str,
) -> str:
    """Формирует текстовую карточку заявки (преемственность ПР1)."""
    return (
        "==================================================\n"
        f"КАРТОЧКА ЗАЯВКИ № {app_id}\n"
        "==================================================\n"
        f"Дата подачи:     {app_date_str}\n"
        f"Студент:         {student_name}\n"
        f"Дисциплина:      {discipline_name}\n"
        f"Тема работы:     {topic_title}\n"
        f"Статус заявки:   {status_text}\n"
        "=================================================="
    )
