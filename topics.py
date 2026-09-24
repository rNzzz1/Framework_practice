"""Модуль управления темами курсовых работ."""

from typing import Dict, Any, List


def add_topic(
    topics: Dict[int, Dict[str, Any]],
    title: str,
    discipline: str,
    supervisor: str,
    min_course: int = 3,
    min_gpa: float = 3.5,
    capacity: int = 1,
) -> Dict[str, Any]:
    """Добавляет новую тему курсовой работы в словарь topics."""
    new_id = max(topics.keys(), default=0) + 1
    topic_data: Dict[str, Any] = {
        "id": new_id,
        "title": title.strip(),
        "discipline": discipline.strip(),
        "supervisor": supervisor.strip(),
        "min_course": min_course,
        "min_gpa": min_gpa,
        "capacity": capacity,
        "current_students": 0,
        "is_available": True,
    }
    topics[new_id] = topic_data
    return topic_data


def find_topics(
    topics: Dict[int, Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Находит темы по подстроке в названии, дисциплине или руководителе."""
    lowered_query = query.lower().strip()
    result = [
        topic for topic in topics.values()
        if (
            lowered_query in topic["title"].lower()
            or lowered_query in topic["supervisor"].lower()
            or lowered_query in topic["discipline"].lower()
        )
    ]
    return result


def check_topic_capacity(topics: Dict[int, Dict[str, Any]], topic_id: int) -> bool:
    """Проверяет, остались ли свободные места на тему по установленной квоте."""
    topic = topics.get(topic_id)
    if not topic:
        return False
    return topic["current_students"] < topic["capacity"]


def is_topic_available(topics: Dict[int, Dict[str, Any]], topic_id: int) -> bool:
    """Проверяет, доступна ли тема для подачи новой заявки."""
    topic = topics.get(topic_id)
    if not topic:
        return False
    return topic["is_available"] and check_topic_capacity(topics, topic_id)


def filter_topics_by_discipline(
    topics: Dict[int, Dict[str, Any]],
    discipline: str,
) -> List[Dict[str, Any]]:
    """Отбирает темы по заданной дисциплине (использует генераторное выражение)."""
    target = discipline.lower().strip()
    matching_topics = (
        topic for topic in topics.values()
        if target in topic["discipline"].lower()
    )
    return list(matching_topics)


def sort_topics_by_title(
    topics: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Сортирует темы по алфавиту с помощью lambda-функции."""
    return sorted(topics.values(), key=lambda item: item["title"].lower())


def sort_topics_by_gpa(
    topics: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Сортирует темы по требуемому минимальному баллу GPA (по возрастанию)."""
    return sorted(topics.values(), key=lambda item: item["min_gpa"])


def get_topic_status(is_available: bool) -> str:
    """Возвращает текстовый статус доступности темы (функция преемственности из ПР1)."""
    if is_available:
        return "Тема свободна для выбора"
    return "Тема уже закреплена за другим студентом"
