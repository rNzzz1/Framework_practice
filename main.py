"""Главный модуль запуска объектно-ориентированного приложения.

Сервис выбора тем курсовых работ (Практическая работа № 3).
"""

import sys
from datetime import date
from typing import List

from models import Topic, Student, Application
from models.topics import (
    find_topic_by_id,
    find_topics,
    filter_topics_by_discipline,
    show_topics,
)
from models.students import (
    add_student,
    find_student_by_id,
    show_students,
)
from models.applications import (
    create_application,
    cancel_application,
    get_applications_statistics,
    show_applications,
    format_application_summary,
)
from storage import (
    load_topics,
    save_topics,
    load_students,
    save_students,
    load_applications,
    save_applications,
)
from utils import (
    input_int,
    input_float,
    input_str,
)

TOPICS_FILE = "data/topics.json"
STUDENTS_FILE = "data/students.json"
APPLICATIONS_FILE = "data/applications.json"


def create_new_application(
    applications: List[Application],
    topics: List[Topic],
    students: List[Student],
) -> None:
    """Организует сценарий подачи заявки студентом на тему курсовой работы."""
    print("\n--- ПОДАЧА НОВОЙ ЗАЯВКИ ---")
    topic_id = input_int("Введите ID выбранной темы: ")
    topic = find_topic_by_id(topics, topic_id)
    if not topic:
        print(f"[-] Тема с ID {topic_id} не найдена.")
        return

    student_id = input_int("Введите ID студента: ")
    student = find_student_by_id(students, student_id)
    if not student:
        print(f"[-] Студент с ID {student_id} не найден.")
        return

    print(f"\nВыбрана тема: {topic.title} (Курс >= {topic.min_course}, GPA >= {topic.min_gpa})")
    print(f"Студент:      {student.name} ({student.course} курс, GPA: {student.gpa})")

    try:
        app = create_application(
            applications=applications,
            topic=topic,
            student=student,
            app_date=date.today(),
        )
        if app is None:
            print("[-] Ошибка: на выбранную тему закончились свободные места.")
            return

        save_topics(TOPICS_FILE, topics)
        save_applications(APPLICATIONS_FILE, applications)

        print("\n[+] Заявка успешно утверждена и сохранена!")
        print(format_application_summary(app))

    except ValueError as err:
        print(f"\n[-] Отказ в регистрации заявки: {err}")


def run_demo_scenario(
    topics: List[Topic],
    students: List[Student],
    applications: List[Application],
) -> None:
    """Запускает демонстрационный сценарий взаимодействия объектов."""
    print("\n=======================================================")
    print("ДЕМОНСТРАЦИОННЫЙ СЦЕНАРИЙ ВЗАИМОДЕЙСТВИЯ ОБЪЕКТОВ (ООП)")
    print("=======================================================")

    print("\n1. Каталог доступных тем курсовых работ:")
    show_topics(topics)

    print("\n2. Список зарегистрированных студентов:")
    show_students(students)

    print("\n3. Взаимодействие объектов: создание новой заявки")
    target_topic = find_topic_by_id(topics, 3)
    target_student = find_student_by_id(students, 2)

    if target_topic and target_student:
        print(f"Подача заявки студентом '{target_student.name}' на тему [{target_topic.id}] '{target_topic.title}'")
        try:
            demo_app = create_application(
                applications=applications,
                topic=target_topic,
                student=target_student,
                app_date=date(2026, 9, 24),
            )
            if demo_app:
                print("\n[+] Объект Application успешно создан и связан с объектами Topic и Student:")
                print(f"    - Ссылка app.topic:   {demo_app.topic.title}")
                print(f"    - Ссылка app.student: {demo_app.student.name}")
                print(f"    - Свойство @property status: {demo_app.status}")
                print(f"    - Метод __str__: {demo_app}")
        except ValueError as err:
            print(f"[!] {err}")

    # Демонстрация валидации: студент с низким GPA
    invalid_student = find_student_by_id(students, 5)
    strict_topic = find_topic_by_id(topics, 4)
    if invalid_student and strict_topic:
        print(f"\nПопытка подачи соискателем '{invalid_student.name}' (GPA: {invalid_student.gpa}) "
              f"на строгую тему [{strict_topic.id}] '{strict_topic.title}' (Мин. GPA: {strict_topic.min_gpa}):")
        try:
            create_application(applications, strict_topic, invalid_student)
        except ValueError as err:
            print(f"[!] Ожидаемый отказ: {err}")

    print("\n4. Сводная статистика по объектам заявок:")
    stats = get_applications_statistics(applications)
    print(f"Всего заявок: {stats['total']} | Одобрено: {stats['approved']} | Средний GPA: {stats['avg_gpa']}")
    print("=======================================================\n")


def main() -> None:
    """Точка запуска приложения и обработка главного цикла меню."""
    topics = load_topics(TOPICS_FILE)
    students = load_students(STUDENTS_FILE)
    applications = load_applications(APPLICATIONS_FILE, topics, students)

    if "--demo" in sys.argv:
        run_demo_scenario(topics, students, applications)
        return

    while True:
        print("\n=== Сервис выбора тем курсовых работ (ООП) ===")
        print("1. Показать все темы курсовых работ")
        print("2. Найти тему по названию или руководителю")
        print("3. Отфильтровать темы по дисциплине")
        print("4. Показать список студентов")
        print("5. Зарегистрировать нового студента")
        print("6. Проверить доступность темы")
        print("7. Подать заявку на тему курсовой работы")
        print("8. Отменить заявку")
        print("9. Показать все заявки")
        print("10. Статистика по заявкам")
        print("11. Запустить демонстрационный сценарий (ООП)")
        print("0. Выход")

        choice = input_int("Выберите действие (0-11): ", min_val=0, max_val=11)

        if choice == 1:
            show_topics(topics)

        elif choice == 2:
            query = input_str("Введите поисковый запрос: ")
            found = find_topics(topics, query)
            if found:
                print(f"\nНайдено тем: {len(found)}")
                for t in found:
                    print(t)
            else:
                print("[-] По запросу ничего не найдено.")

        elif choice == 3:
            disc = input_str("Введите название дисциплины: ")
            filtered = filter_topics_by_discipline(topics, disc)
            if filtered:
                print(f"\nТемы по дисциплине '{disc}':")
                for t in filtered:
                    print(t)
            else:
                print("[-] Тем по заданной дисциплине не найдено.")

        elif choice == 4:
            show_students(students)

        elif choice == 5:
            name = input_str("ФИО студента: ")
            course = input_int("Курс (1-6): ", min_val=1, max_val=6)
            gpa = input_float("Средний балл GPA (2.0 - 5.0): ", min_val=2.0, max_val=5.0)
            budget_str = input_str("Форма обучения (б - бюджет / д - договор): ").lower()
            is_budget = budget_str.startswith("б")
            email = input_str("Email студента: ")

            new_student = add_student(students, name, course, gpa, is_budget, email)
            save_students(STUDENTS_FILE, students)
            print(f"[+] Студент успешно зарегистрирован: {new_student}")

        elif choice == 6:
            topic_id = input_int("Введите ID темы: ")
            topic = find_topic_by_id(topics, topic_id)
            if topic:
                status_text = "свободна для выбора" if (topic.is_available and topic.has_free_capacity()) else "занята"
                print(f"[i] Тема '{topic.title}' {status_text} (Квота: {topic.current_students}/{topic.capacity}).")
            else:
                print("[-] Тема с таким ID не найдена.")

        elif choice == 7:
            create_new_application(applications, topics, students)

        elif choice == 8:
            app_id = input_int("Введите номер заявки для отмены: ")
            if cancel_application(applications, app_id):
                save_topics(TOPICS_FILE, topics)
                save_applications(APPLICATIONS_FILE, applications)
                print(f"[+] Заявка №{app_id} успешно отменена, место на тему освобождено.")
            else:
                print(f"[-] Заявка №{app_id} не найдена или уже была отменена.")

        elif choice == 9:
            show_applications(applications)

        elif choice == 10:
            stats = get_applications_statistics(applications)
            print("\n" + "=" * 45)
            print("АНАЛИТИЧЕСКАЯ СТАТИСТИКА ПО ЗАЯВКАМ")
            print("=" * 45)
            print(f"Всего заявок в системе: {stats['total']}")
            print(f"Одобренных заявок:      {stats['approved']}")
            print(f"Отмененных заявок:      {stats['cancelled']}")
            print(f"Средний балл студентов: {stats['avg_gpa']}")
            print("=" * 45)

        elif choice == 11:
            run_demo_scenario(topics, students, applications)

        elif choice == 0:
            save_topics(TOPICS_FILE, topics)
            save_students(STUDENTS_FILE, students)
            save_applications(APPLICATIONS_FILE, applications)
            print("\nДанные сохранены. Завершение работы программы!")
            break


if __name__ == "__main__":
    main()
