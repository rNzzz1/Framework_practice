"""Модуль загрузки и сохранения объектов предметной области в формате JSON."""

import json
import os
from typing import Any, List

from models import Topic, Student, Application
from models.topics import find_topic_by_id
from models.students import find_student_by_id


def load_json_file(filename: str, default_data: Any) -> Any:
    """Безопасно загружает сырые данные из JSON-файла с обработкой исключений."""
    if not os.path.exists(filename):
        return default_data

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Предупреждение] Ошибка при чтении файла {filename}: {error}")
        return default_data


def save_json_file(filename: str, data: Any) -> None:
    """Сохраняет переданные данные в JSON-файл через контекстный менеджер with."""
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"[Ошибка] Не удалось записать данные в файл {filename}: {error}")


def load_topics(filename: str) -> List[Topic]:
    """Загружает темы курсовых работ и преобразует их в список объектов Topic."""
    raw_list = load_json_file(filename, default_data=[])
    return [Topic.from_dict(item) for item in raw_list]


def save_topics(filename: str, topics: List[Topic]) -> None:
    """Сериализует список объектов Topic в JSON-файл."""
    data = [topic.to_dict() for topic in topics]
    save_json_file(filename, data)


def load_students(filename: str) -> List[Student]:
    """Загружает студентов и преобразует их в список объектов Student."""
    raw_list = load_json_file(filename, default_data=[])
    return [Student.from_dict(item) for item in raw_list]


def save_students(filename: str, students: List[Student]) -> None:
    """Сериализует список объектов Student в JSON-файл."""
    data = [student.to_dict() for student in students]
    save_json_file(filename, data)


def load_applications(
    filename: str,
    topics: List[Topic],
    students: List[Student],
) -> List[Application]:
    """Загружает заявки из JSON и восстанавливает объектные связи с Topic и Student."""
    raw_list = load_json_file(filename, default_data=[])
    applications: List[Application] = []

    for item in raw_list:
        topic_id = int(item["topic_id"])
        student_id = int(item["student_id"])

        matched_topic = find_topic_by_id(topics, topic_id)
        matched_student = find_student_by_id(students, student_id)

        if matched_topic and matched_student:
            app = Application(
                app_id=int(item["id"]),
                topic=matched_topic,
                student=matched_student,
                application_date=str(item.get("application_date", "")),
                priority=int(item.get("priority", matched_student.calculate_priority())),
                is_cancelled=bool(item.get("is_cancelled", False)),
            )
            applications.append(app)
        else:
            print(
                f"[Предупреждение] Пропуск заявки №{item.get('id')}: "
                f"не найден связанный объект Topic({topic_id}) или Student({student_id})."
            )

    return applications


def save_applications(filename: str, applications: List[Application]) -> None:
    """Сериализует список объектов Application в JSON-файл с сохранением ID связей."""
    data = [app.to_dict() for app in applications]
    save_json_file(filename, data)
