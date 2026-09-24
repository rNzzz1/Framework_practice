"""Модуль загрузки и сохранения данных проекта в формате JSON."""

import json
import os
from typing import Any, List, Dict


def load_json_file(filename: str, default_data: Any) -> Any:
    """Безопасно загружает данные из JSON-файла.

    При отсутствии файла или некорректной структуре JSON возвращает
    значение по умолчанию и перехватывает исключения.
    """
    if not os.path.exists(filename):
        return default_data

    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Предупреждение] Ошибка при чтении файла {filename}: {error}")
        return default_data


def save_json_file(filename: str, data: Any) -> None:
    """Сохраняет переданные данные в JSON-файл с форматированием.

    Использует контекстный менеджер with и гарантирует закрытие файла.
    """
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print(f"[Ошибка] Не удалось записать данные в файл {filename}: {error}")


def load_topics(filename: str) -> Dict[int, Dict[str, Any]]:
    """Загружает темы курсовых работ из JSON-файла и возвращает словарь по id."""
    raw_list = load_json_file(filename, default_data=[])
    topics: Dict[int, Dict[str, Any]] = {}
    for item in raw_list:
        topic_id = int(item["id"])
        topics[topic_id] = item
    return topics


def save_topics(filename: str, topics: Dict[int, Dict[str, Any]]) -> None:
    """Сохраняет словарь тем курсовых работ в JSON-файл как список."""
    topic_list = list(topics.values())
    save_json_file(filename, topic_list)


def load_applications(filename: str) -> List[Dict[str, Any]]:
    """Загружает список заявок студентов из JSON-файла."""
    raw_list = load_json_file(filename, default_data=[])
    return list(raw_list)


def save_applications(
    filename: str,
    applications: List[Dict[str, Any]],
) -> None:
    """Сохраняет список заявок студентов в JSON-файл."""
    save_json_file(filename, applications)
