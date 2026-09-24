"""Тесты для объектной модели Topic и функций работы с темами."""

from models import Topic
from models.topics import (
    add_topic,
    find_topics,
    find_topic_by_id,
    filter_topics_by_discipline,
    sort_topics_by_title,
)


def test_topic_creation():
    """Проверка создания объекта Topic и инициализации его атрибутов."""
    topic = Topic(
        topic_id=1,
        title="Разработка веб-сервиса",
        discipline="Фреймворки",
        supervisor="доц. Ящун Т. В.",
        min_course=3,
        min_gpa=3.5,
        capacity=1,
    )
    assert topic.id == 1
    assert topic.title == "Разработка веб-сервиса"
    assert topic.discipline == "Фреймворки"
    assert topic.capacity == 1
    assert topic.current_students == 0
    assert topic.is_available is True


def test_topic_is_suitable_for():
    """Проверка метода проверки академического допуска студента."""
    topic = Topic(
        topic_id=1,
        title="Тема",
        discipline="Дисциплина",
        supervisor="Руководитель",
        min_course=3,
        min_gpa=4.0,
    )
    assert topic.is_suitable_for(student_course=3, gpa=4.5) is True
    assert topic.is_suitable_for(student_course=2, gpa=4.5) is False
    assert topic.is_suitable_for(student_course=3, gpa=3.8) is False


def test_topic_reserve_and_release():
    """Проверка резервирования и освобождения мест по квоте темы."""
    topic = Topic(
        topic_id=1,
        title="Тема",
        discipline="Дисциплина",
        supervisor="Руководитель",
        capacity=1,
    )
    assert topic.has_free_capacity() is True
    assert topic.reserve_slot() is True
    assert topic.current_students == 1
    assert topic.is_available is False
    assert topic.has_free_capacity() is False
    assert topic.reserve_slot() is False

    # Освобождение места
    topic.release_slot()
    assert topic.current_students == 0
    assert topic.is_available is True
    assert topic.has_free_capacity() is True


def test_topic_find_and_filter():
    """Проверка поиска и фильтрации в коллекции объектов Topic."""
    topics = [
        Topic(1, "Веб-разработка на Django", "Фреймворки", "Ящун Т. В."),
        Topic(2, "Базы данных в облаке", "Базы данных", "Смирнов А. А."),
    ]
    found = find_topics(topics, "django")
    assert len(found) == 1
    assert found[0].id == 1

    filtered = filter_topics_by_discipline(topics, "базы данных")
    assert len(filtered) == 1
    assert filtered[0].id == 2


def test_topic_sort():
    """Проверка сортировки коллекции тем по названию."""
    topics = [
        Topic(1, "Языки программирования", "ИТ", "Преподаватель"),
        Topic(2, "Алгоритмы и структуры", "ИТ", "Преподаватель"),
    ]
    sorted_topics = sort_topics_by_title(topics)
    assert sorted_topics[0].title == "Алгоритмы и структуры"
    assert sorted_topics[1].title == "Языки программирования"


def test_topic_str():
    """Проверка метода __str__ класса Topic."""
    topic = Topic(1, "Тестовая тема", "ИТ", "Руководитель")
    str_val = str(topic)
    assert "[1]" in str_val
    assert "Тестовая тема" in str_val
