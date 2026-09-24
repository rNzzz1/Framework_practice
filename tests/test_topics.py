"""Тесты для модуля topics.py."""

from topics import (
    add_topic,
    find_topics,
    check_topic_capacity,
    is_topic_available,
    sort_topics_by_title,
    get_topic_status,
)


def test_add_topic():
    """Проверка добавления новой темы курсовой работы."""
    topics = {}
    topic = add_topic(
        topics=topics,
        title="Разработка Telegram-бота",
        discipline="Информационные системы",
        supervisor="Иванов И. И.",
        min_course=2,
        min_gpa=3.5,
        capacity=1,
    )
    assert len(topics) == 1
    assert topic["id"] == 1
    assert topic["current_students"] == 0
    assert topic["is_available"] is True


def test_find_topics():
    """Проверка поиска тем по ключевым словам."""
    topics = {
        1: {
            "id": 1,
            "title": "Разработка веб-сервиса",
            "discipline": "Фреймворки",
            "supervisor": "Ящун Т. В.",
        },
        2: {
            "id": 2,
            "title": "Анализ алгоритмов",
            "discipline": "Алгоритмы",
            "supervisor": "Петров П. П.",
        },
    }
    found = find_topics(topics, "веб-сервис")
    assert len(found) == 1
    assert found[0]["id"] == 1

    not_found = find_topics(topics, "несуществующая тема")
    assert len(not_found) == 0


def test_check_topic_capacity():
    """Проверка контроля свободных мест по квоте темы."""
    topics = {
        1: {"id": 1, "capacity": 2, "current_students": 1},
        2: {"id": 2, "capacity": 1, "current_students": 1},
    }
    assert check_topic_capacity(topics, 1) is True
    assert check_topic_capacity(topics, 2) is False
    assert check_topic_capacity(topics, 999) is False


def test_sort_topics_by_title():
    """Проверка сортировки тем по алфавиту."""
    topics = {
        1: {"id": 1, "title": "Языки программирования"},
        2: {"id": 2, "title": "Архитектура ЭВМ"},
    }
    sorted_list = sort_topics_by_title(topics)
    assert sorted_list[0]["title"] == "Архитектура ЭВМ"
    assert sorted_list[1]["title"] == "Языки программирования"


def test_get_topic_status():
    """Проверка текстового статуса доступности темы."""
    assert "свободна" in get_topic_status(True).lower()
    assert "закреплена" in get_topic_status(False).lower()
