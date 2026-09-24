"""Модуль описания класса Topic и функций работы с коллекциями тем."""

from typing import List, Dict, Any, Optional


class Topic:
    """Класс, представляющий тему курсовой работы."""

    def __init__(
        self,
        topic_id: int,
        title: str,
        discipline: str,
        supervisor: str,
        min_course: int = 3,
        min_gpa: float = 3.5,
        capacity: int = 1,
        current_students: int = 0,
        is_available: bool = True,
    ) -> None:
        """Создает объект темы курсовой работы."""
        self.id = topic_id
        self.title = title.strip()
        self.discipline = discipline.strip()
        self.supervisor = supervisor.strip()
        self.min_course = min_course
        self.min_gpa = min_gpa
        self.capacity = capacity
        self.current_students = current_students
        self.is_available = is_available

    def is_suitable_for(self, student_course: int, gpa: float) -> bool:
        """Проверяет, соответствует ли студент академическим требованиям темы."""
        return (student_course >= self.min_course) and (gpa >= self.min_gpa)

    def has_free_capacity(self) -> bool:
        """Проверяет, есть ли свободные места по установленной квоте."""
        return self.current_students < self.capacity

    def reserve_slot(self) -> bool:
        """Резервирует место на тему при подаче заявки."""
        if not self.has_free_capacity() or not self.is_available:
            return False
        self.current_students += 1
        if self.current_students >= self.capacity:
            self.is_available = False
        return True

    def release_slot(self) -> None:
        """Освобождает место при отмене заявки."""
        self.current_students = max(0, self.current_students - 1)
        self.is_available = True

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверяет корректность значения квоты мест."""
        return capacity > 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Topic":
        """Создает объект темы из словаря данных JSON."""
        return cls(
            topic_id=int(data["id"]),
            title=str(data["title"]),
            discipline=str(data["discipline"]),
            supervisor=str(data["supervisor"]),
            min_course=int(data.get("min_course", 3)),
            min_gpa=float(data.get("min_gpa", 3.5)),
            capacity=int(data.get("capacity", 1)),
            current_students=int(data.get("current_students", 0)),
            is_available=bool(data.get("is_available", True)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект темы в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "discipline": self.discipline,
            "supervisor": self.supervisor,
            "min_course": self.min_course,
            "min_gpa": self.min_gpa,
            "capacity": self.capacity,
            "current_students": self.current_students,
            "is_available": self.is_available,
        }

    def __str__(self) -> str:
        """Удобное строковое представление темы."""
        status_text = "Свободна" if (self.is_available and self.has_free_capacity()) else "Занята"
        return (
            f"[{self.id}] '{self.title}' | {self.discipline} | "
            f"Рук.: {self.supervisor} | Квота: {self.current_students}/{self.capacity} | Статус: {status_text}"
        )


def add_topic(
    topics: List[Topic],
    title: str,
    discipline: str,
    supervisor: str,
    min_course: int = 3,
    min_gpa: float = 3.5,
    capacity: int = 1,
) -> Topic:
    """Создает новый объект Topic и добавляет его в коллекцию."""
    new_id = max((t.id for t in topics), default=0) + 1
    new_topic = Topic(
        topic_id=new_id,
        title=title,
        discipline=discipline,
        supervisor=supervisor,
        min_course=min_course,
        min_gpa=min_gpa,
        capacity=capacity,
    )
    topics.append(new_topic)
    return new_topic


def find_topic_by_id(topics: List[Topic], topic_id: int) -> Optional[Topic]:
    """Находит объект темы по его идентификатору."""
    for topic in topics:
        if topic.id == topic_id:
            return topic
    return None


def find_topics(topics: List[Topic], query: str) -> List[Topic]:
    """Ищет объекты тем по подстроке в названии, дисциплине или руководителе."""
    lowered = query.lower().strip()
    return [
        topic for topic in topics
        if (
            lowered in topic.title.lower()
            or lowered in topic.discipline.lower()
            or lowered in topic.supervisor.lower()
        )
    ]


def filter_topics_by_discipline(topics: List[Topic], discipline: str) -> List[Topic]:
    """Отбирает объекты тем по указанной дисциплине."""
    lowered = discipline.lower().strip()
    return [topic for topic in topics if lowered in topic.discipline.lower()]


def sort_topics_by_title(topics: List[Topic]) -> List[Topic]:
    """Сортирует список объектов тем по названию с использованием lambda-функции."""
    return sorted(topics, key=lambda topic: topic.title.lower())


def show_topics(topics: List[Topic]) -> None:
    """Выводит список объектов тем в виде таблицы."""
    if not topics:
        print("\n[!] Список тем курсовых работ пуст.")
        return

    print("\n" + "=" * 90)
    print(f"{'ID':<4} | {'Название темы':<35} | {'Дисциплина':<25} | {'Квота':<6} | {'Статус':<15}")
    print("-" * 90)
    for topic in sort_topics_by_title(topics):
        quota_str = f"{topic.current_students}/{topic.capacity}"
        status_str = "Доступна" if (topic.is_available and topic.has_free_capacity()) else "Занята"
        title_truncated = topic.title[:32] + "..." if len(topic.title) > 35 else topic.title
        disc_truncated = topic.discipline[:22] + "..." if len(topic.discipline) > 25 else topic.discipline
        print(f"{topic.id:<4} | {title_truncated:<35} | {disc_truncated:<25} | {quota_str:<6} | {status_str:<15}")
    print("=" * 90)
