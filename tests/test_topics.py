"""Тесты для объектной модели Topic и функций работы с темами."""

import unittest
from models import Topic
from models.topics import (
    add_topic,
    find_topics,
    find_topic_by_id,
    filter_topics_by_discipline,
    sort_topics_by_title,
)


class TestTopicModel(unittest.TestCase):
    """Набор тестов для сущности Topic."""

    def test_topic_creation(self):
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
        self.assertEqual(topic.id, 1)
        self.assertEqual(topic.title, "Разработка веб-сервиса")
        self.assertEqual(topic.discipline, "Фреймворки")
        self.assertEqual(topic.capacity, 1)
        self.assertEqual(topic.current_students, 0)
        self.assertTrue(topic.is_available)

    def test_topic_is_suitable_for(self):
        """Проверка метода проверки академического допуска студента."""
        topic = Topic(
            topic_id=1,
            title="Тема",
            discipline="Дисциплина",
            supervisor="Руководитель",
            min_course=3,
            min_gpa=4.0,
        )
        self.assertTrue(topic.is_suitable_for(student_course=3, gpa=4.5))
        self.assertFalse(topic.is_suitable_for(student_course=2, gpa=4.5))
        self.assertFalse(topic.is_suitable_for(student_course=3, gpa=3.8))

    def test_topic_reserve_and_release(self):
        """Проверка резервирования и освобождения мест по квоте темы."""
        topic = Topic(
            topic_id=1,
            title="Тема",
            discipline="Дисциплина",
            supervisor="Руководитель",
            capacity=1,
        )
        self.assertTrue(topic.has_free_capacity())
        self.assertTrue(topic.reserve_slot())
        self.assertEqual(topic.current_students, 1)
        self.assertFalse(topic.is_available)
        self.assertFalse(topic.has_free_capacity())
        self.assertFalse(topic.reserve_slot())

        # Освобождение места
        topic.release_slot()
        self.assertEqual(topic.current_students, 0)
        self.assertTrue(topic.is_available)
        self.assertTrue(topic.has_free_capacity())

    def test_topic_find_and_filter(self):
        """Проверка поиска и фильтрации в коллекции объектов Topic."""
        topics = [
            Topic(1, "Веб-разработка на Django", "Фреймворки", "Ящун Т. В."),
            Topic(2, "Базы данных в облаке", "Базы данных", "Смирнов А. А."),
        ]
        found = find_topics(topics, "django")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].id, 1)

        filtered = filter_topics_by_discipline(topics, "базы данных")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, 2)

    def test_topic_sort(self):
        """Проверка сортировки коллекции тем по названию."""
        topics = [
            Topic(1, "Языки программирования", "ИТ", "Преподаватель"),
            Topic(2, "Алгоритмы и структуры", "ИТ", "Преподаватель"),
        ]
        sorted_topics = sort_topics_by_title(topics)
        self.assertEqual(sorted_topics[0].title, "Алгоритмы и структуры")
        self.assertEqual(sorted_topics[1].title, "Языки программирования")

    def test_topic_helpers(self):
        """Проверка вспомогательных функций add_topic и find_topic_by_id."""
        topics = []
        new_t = add_topic(topics, "Новая тема", "ИТ", "Руководитель", 3, 3.5, 1)
        self.assertEqual(len(topics), 1)
        self.assertEqual(new_t.id, 1)

        found_by_id = find_topic_by_id(topics, 1)
        self.assertIsNotNone(found_by_id)
        self.assertEqual(found_by_id.title, "Новая тема")


if __name__ == "__main__":
    unittest.main()
