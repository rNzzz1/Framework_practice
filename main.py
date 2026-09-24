"""
Сервис выбора тем курсовых работ.

Начальная реализация в рамках Практической работы № 1.
Используются базовые конструкции Python: простые типы данных,
операции, преобразование типов, условные конструкции if/elif/else,
функции и импорт модулей из стандартной библиотеки.
"""

from datetime import date


def check_topic_availability(is_available: bool) -> str:
    """
    Проверяет статус доступности темы курсовой работы для выбора.
    """
    if is_available:
        return "Тема свободна для выбора"
    else:
        return "Тема уже закреплена за другим студентом"


def validate_student_eligibility(
    student_course: int,
    required_course: int,
    gpa: float,
    min_gpa: float,
) -> bool:
    """
    Проверяет допуск студента к выбору темы по курсу обучения и среднему баллу.
    """
    is_course_valid = student_course >= required_course
    is_gpa_valid = gpa >= min_gpa

    if is_course_valid and is_gpa_valid:
        return True
    return False


def calculate_application_priority(gpa: float, is_budget: bool) -> int:
    """
    Рассчитывает числовой приоритет заявки.

    Формула: базовый балл рассчитывается на основе среднего балла (GPA * 20),
    плюс надбавка 10 баллов для студентов бюджетной формы обучения.
    """
    base_priority = int(gpa * 20)
    bonus = 10 if is_budget else 0
    total_priority = base_priority + bonus
    return total_priority


def format_application_summary(
    app_id: int,
    student_name: str,
    topic_title: str,
    discipline_name: str,
    app_date: date,
    is_approved: bool,
) -> str:
    """
    Формирует итоговую текстовую сводку по заявке на тему курсовой работы.
    """
    status_text = "ОДОБРЕНА" if is_approved else "ОТКЛОНЕНА"

    summary = (
        "==================================================\n"
        f"КАРТОЧКА ЗАЯВКИ № {app_id}\n"
        "==================================================\n"
        f"Дата подачи:     {app_date.strftime('%d.%m.%Y')}\n"
        f"Студент:         {student_name}\n"
        f"Дисциплина:      {discipline_name}\n"
        f"Тема работы:     {topic_title}\n"
        f"Статус заявки:   {status_text}\n"
        "=================================================="
    )
    return summary


def main():
    print("--- СЕРВИС ВЫБОРА ТЕМ КУРСОВЫХ РАБОТ ---\n")

    # Входные данные: Сущность Студент
    student_name = "Узунян Осип"
    student_course_str = "3"
    student_gpa_str = "4.75"
    is_budget = True

    # Преобразование типов данных
    student_course = int(student_course_str)
    student_gpa = float(student_gpa_str)

    # Входные данные: Сущность Дисциплина
    discipline_name = "Технологии разработки приложений на базе фреймворков"
    required_course = 3
    min_required_gpa = 3.5

    # Входные данные: Сущность Тема курсовой работы
    topic_title = "Разработка веб-сервиса распределения курсовых работ"
    is_topic_available = True
    topic_supervisor = "доц. Ящун Т. В."

    # Входные данные: Сущность Заявка
    application_id = 101
    submission_date = date(2026, 9, 24)

    # Вывод информации о запросе
    print(f"Подача заявки студентом: {student_name} ({student_course} курс)")
    print(f"Средний балл успеваемости (GPA): {student_gpa}")
    print(f"Форма обучения: {'Бюджет' if is_budget else 'Договор'}")
    print(f"Выбранная дисциплина: {discipline_name}")
    print(f"Выбранная тема: {topic_title}")
    print(f"Научный руководитель: {topic_supervisor}")
    print(f"Статус темы: {check_topic_availability(is_topic_available)}\n")

    # Проверка условий допуска студента
    is_eligible = validate_student_eligibility(
        student_course=student_course,
        required_course=required_course,
        gpa=student_gpa,
        min_gpa=min_required_gpa,
    )

    if is_eligible:
        print("[+] Студент соответствует академическим требованиям.")
    else:
        print("[-] Студент НЕ соответствует требованиям для выбора данной темы.")

    # Вычисление приоритета заявки
    priority = calculate_application_priority(student_gpa, is_budget)
    print(f"[i] Рассчитанный приоритет заявки: {priority} баллов")

    # Принятие решения по заявке
    if is_eligible and is_topic_available:
        is_approved = True
        print("[+] Решение: Заявка успешно утверждена!\n")
    else:
        is_approved = False
        print("[-] Решение: Заявка отклонена.\n")

    # Формирование и вывод итоговой карточки заявки
    summary = format_application_summary(
        app_id=application_id,
        student_name=student_name,
        topic_title=topic_title,
        discipline_name=discipline_name,
        app_date=submission_date,
        is_approved=is_approved,
    )
    print(summary)


if __name__ == "__main__":
    main()
