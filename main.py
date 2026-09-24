"""Главный модуль запуска консольного приложения 'Сервис выбора тем курсовых работ'.

Реализует интерактивное меню пользователя, координацию работы модулей,
загрузку и сохранение данных в формате JSON.
"""

import sys
from datetime import date
from typing import Dict, Any, List

from storage import (
    load_topics,
    save_topics,
    load_applications,
    save_applications,
)
from topics import (
    find_topics,
    is_topic_available,
    filter_topics_by_discipline,
    sort_topics_by_title,
    get_topic_status,
)
from applications import (
    create_application,
    cancel_application,
    get_applications_statistics,
    format_application_summary,
)
from utils import (
    input_int,
    input_float,
    input_date,
    input_str,
)

TOPICS_FILE = "data/topics.json"
APPLICATIONS_FILE = "data/applications.json"


def show_topics(topics: Dict[int, Dict[str, Any]]) -> None:
    """Выводит список тем курсовых работ в виде форматированной таблицы."""
    if not topics:
        print("\n[!] Список тем курсовых работ пуст.")
        return

    print("\n" + "=" * 90)
    print(f"{'ID':<4} | {'Название темы':<35} | {'Дисциплина':<25} | {'Квота':<6} | {'Статус':<15}")
    print("-" * 90)
    for topic in sort_topics_by_title(topics):
        quota_str = f"{topic['current_students']}/{topic['capacity']}"
        status_str = "Доступна" if topic["is_available"] else "Занята"
        title_truncated = (
            topic['title'][:32] + "..." if len(topic['title']) > 35 else topic['title']
        )
        disc_truncated = (
            topic['discipline'][:22] + "..." if len(topic['discipline']) > 25 else topic['discipline']
        )
        print(f"{topic['id']:<4} | {title_truncated:<35} | {disc_truncated:<25} | {quota_str:<6} | {status_str:<15}")
    print("=" * 90)


def show_applications(
    applications: List[Dict[str, Any]],
    topics: Dict[int, Dict[str, Any]],
) -> None:
    """Выводит список поданных заявок с детализацией."""
    if not applications:
        print("\n[!] Список поданных заявок пуст.")
        return

    print("\n" + "=" * 90)
    print(f"{'№':<5} | {'Студент':<20} | {'Тема ID':<8} | {'GPA':<5} | {'Приоритет':<10} | {'Статус':<12}")
    print("-" * 90)
    for app in applications:
        print(
            f"{app['id']:<5} | {app['student_name']:<20} | {app['topic_id']:<8} | "
            f"{app['gpa']:<5.2f} | {app['priority']:<10} | {app['status']:<12}"
        )
    print("=" * 90)


def run_demo_scenario(topics: Dict[int, Dict[str, Any]], applications: List[Dict[str, Any]]) -> None:
    """Демонстрационный запуск без блокировки консоли (для тестов и отладки)."""
    print("\n--- ДЕМОНСТРАЦИОННЫЙ ЗАПУСК СЕРВИСА ---")
    show_topics(topics)

    print("\n[Демо] Поиск темы по ключевому слову 'микросервис':")
    found = find_topics(topics, "микросервис")
    for t in found:
        print(f"-> Найдено: [{t['id']}] {t['title']} (Рук.: {t['supervisor']})")

    print("\n[Демо] Проверка доступности темы №2:")
    avail = is_topic_available(topics, 2)
    print(f"Статус темы №2: {get_topic_status(avail)}")

    print("\n[Демо] Подача заявки на тему №2:")
    try:
        new_app = create_application(
            applications=applications,
            topics=topics,
            topic_id=2,
            student_name="Иванов Иван",
            student_course=3,
            gpa=4.6,
            is_budget=True,
            app_date=date(2026, 9, 24),
        )
        print(format_application_summary(
            app_id=new_app["id"],
            student_name=new_app["student_name"],
            topic_title=topics[2]["title"],
            discipline_name=topics[2]["discipline"],
            app_date_str=new_app["application_date"],
            status_text=new_app["status"],
        ))
    except ValueError as err:
        print(f"[!] Ошибка при подаче заявки: {err}")

    stats = get_applications_statistics(applications)
    print(f"\n[Демо] Статистика: Всего заявок: {stats['total']}, Одобрено: {stats['approved']}, Средний GPA: {stats['avg_gpa']}")


def main() -> None:
    """Точка запуска приложения и обработка главного цикла меню."""
    topics = load_topics(TOPICS_FILE)
    applications = load_applications(APPLICATIONS_FILE)

    if "--demo" in sys.argv:
        run_demo_scenario(topics, applications)
        return

    while True:
        print("\n=== Сервис выбора тем курсовых работ ===")
        print("1. Показать все темы курсовых работ")
        print("2. Найти тему по названию или руководителю")
        print("3. Отфильтровать темы по дисциплине")
        print("4. Проверить доступность темы")
        print("5. Подать заявку на тему курсовой работы")
        print("6. Отменить заявку")
        print("7. Показать все заявки")
        print("8. Статистика по заявкам")
        print("9. Запустить демонстрационный сценарий")
        print("0. Выход")

        choice = input_int("Выберите действие (0-9): ", min_val=0, max_val=9)

        if choice == 1:
            show_topics(topics)

        elif choice == 2:
            query = input_str("Введите строку для поиска: ")
            found = find_topics(topics, query)
            if found:
                print(f"\nНайдено тем: {len(found)}")
                for t in found:
                    print(f"[{t['id']}] {t['title']} | Рук.: {t['supervisor']} | Дисциплина: {t['discipline']}")
            else:
                print("[-] По данному запросу ничего не найдено.")

        elif choice == 3:
            discipline = input_str("Введите название дисциплины: ")
            filtered = filter_topics_by_discipline(topics, discipline)
            if filtered:
                print(f"\nТемы по дисциплине '{discipline}':")
                for t in filtered:
                    print(f"[{t['id']}] {t['title']} (Курс >= {t['min_course']}, GPA >= {t['min_gpa']})")
            else:
                print("[-] Тем по данной дисциплине не найдено.")

        elif choice == 4:
            topic_id = input_int("Введите ID темы: ")
            if topic_id not in topics:
                print("[-] Тема с таким ID не существует.")
            else:
                avail = is_topic_available(topics, topic_id)
                print(f"[i] {get_topic_status(avail)}")

        elif choice == 5:
            topic_id = input_int("Введите ID темы: ")
            student_name = input_str("ФИО студента: ")
            student_course = input_int("Курс обучения: ", min_val=1, max_val=6)
            gpa = input_float("Средний балл (GPA, от 2.0 до 5.0): ", min_val=2.0, max_val=5.0)
            budget_choice = input_str("Форма обучения (б - бюджет / д - договор): ").lower()
            is_budget = budget_choice.startswith("б")

            try:
                app = create_application(
                    applications=applications,
                    topics=topics,
                    topic_id=topic_id,
                    student_name=student_name,
                    student_course=student_course,
                    gpa=gpa,
                    is_budget=is_budget,
                    app_date=date.today(),
                )
                save_topics(TOPICS_FILE, topics)
                save_applications(APPLICATIONS_FILE, applications)

                topic_info = topics[topic_id]
                print("\n[+] Заявка успешно создана и сохранена!")
                print(format_application_summary(
                    app_id=app["id"],
                    student_name=app["student_name"],
                    topic_title=topic_info["title"],
                    discipline_name=topic_info["discipline"],
                    app_date_str=app["application_date"],
                    status_text=app["status"],
                ))
            except ValueError as error:
                print(f"\n[-] Ошибка: {error}")

        elif choice == 6:
            app_id = input_int("Введите номер заявки для отмены: ")
            if cancel_application(applications, topics, app_id):
                save_topics(TOPICS_FILE, topics)
                save_applications(APPLICATIONS_FILE, applications)
                print(f"[+] Заявка №{app_id} успешно отменена, место на тему освобождено.")
            else:
                print(f"[-] Заявка №{app_id} не найдена или уже была отменена.")

        elif choice == 7:
            show_applications(applications, topics)

        elif choice == 8:
            stats = get_applications_statistics(applications)
            print("\n" + "=" * 40)
            print("СТАТИСТИКА ПО ЗАЯВКАМ")
            print("=" * 40)
            print(f"Всего заявок в системе: {stats['total']}")
            print(f"Одобренных заявок:      {stats['approved']}")
            print(f"Отмененных заявок:      {stats['cancelled']}")
            print(f"Средний балл студентов: {stats['avg_gpa']}")
            print("=" * 40)

        elif choice == 9:
            run_demo_scenario(topics, applications)

        elif choice == 0:
            print("\nЗавершение работы программы. До свидания!")
            break


if __name__ == "__main__":
    main()
