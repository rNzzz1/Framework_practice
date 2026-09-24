"""Модуль описания класса Application и функций управления заявками."""

from datetime import date
from typing import List, Dict, Any, Optional

from .topics import Topic
from .students import Student


class Application:
    """Класс, представляющий заявку студента на закрепление темы курсовой работы.

    Связывает объекты Topic и Student (композиция / ассоциация сущностей).
    """

    def __init__(
        self,
        app_id: int,
        topic: Topic,
        student: Student,
        application_date: str,
        priority: Optional[int] = None,
        is_cancelled: bool = False,
    ) -> None:
        """Создает объект заявки с прямыми ссылками на Topic и Student."""
        self.id = app_id
        self.topic = topic
        self.student = student
        self.application_date = application_date
        self.priority = priority if priority is not None else student.calculate_priority()
        self.is_cancelled = is_cancelled

    def cancel(self) -> None:
        """Отменяет заявку и освобождает закрепленное место на тему."""
        if not self.is_cancelled:
            self.is_cancelled = True
            self.topic.release_slot()

    @property
    def status(self) -> str:
        """Возвращает текстовый статус заявки с использованием свойства @property."""
        return "ОТМЕНЕНА" if self.is_cancelled else "ОДОБРЕНА"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует заявку в формат словаря для сохранения в JSON (внешние ключи)."""
        return {
            "id": self.id,
            "topic_id": self.topic.id,
            "student_id": self.student.id,
            "application_date": self.application_date,
            "priority": self.priority,
            "is_cancelled": self.is_cancelled,
        }

    def __str__(self) -> str:
        """Строковое представление заявки."""
        return (
            f"Заявка №{self.id} от {self.application_date} | "
            f"Студент: {self.student.name} -> Тема [{self.topic.id}] '{self.topic.title}' | "
            f"Приоритет: {self.priority} | Статус: {self.status}"
        )


def is_student_applied(
    applications: List[Application],
    student: Student,
    topic: Topic,
) -> bool:
    """Проверяет, имеется ли уже активная заявка от данного студента на эту тему."""
    for app in applications:
        if (
            app.student.id == student.id
            and app.topic.id == topic.id
            and not app.is_cancelled
        ):
            return True
    return False


def create_application(
    applications: List[Application],
    topic: Topic,
    student: Student,
    app_date: Optional[date] = None,
) -> Optional[Application]:
    """Создает новую заявку на тему курсовой работы при соблюдении условий.

    Raises:
        ValueError: если студент не соответствует требованиям или уже подавал заявку.
    """
    if is_student_applied(applications, student, topic):
        raise ValueError(
            f"Студент {student.name} уже подал активную заявку на тему №{topic.id}."
        )

    if not topic.is_suitable_for(student.course, student.gpa):
        raise ValueError(
            f"Студент не соответствует требованиям темы (требуется курс >= {topic.min_course}, "
            f"GPA >= {topic.min_gpa})."
        )

    if not topic.reserve_slot():
        return None

    new_id = max((app.id for app in applications), default=100) + 1
    current_date_str = (app_date or date.today()).isoformat()

    new_app = Application(
        app_id=new_id,
        topic=topic,
        student=student,
        application_date=current_date_str,
        priority=student.calculate_priority(),
        is_cancelled=False,
    )
    applications.append(new_app)
    return new_app


def cancel_application(
    applications: List[Application],
    app_id: int,
) -> bool:
    """Находит заявку по идентификатору и вызывает метод cancel()."""
    for app in applications:
        if app.id == app_id:
            if app.is_cancelled:
                return False
            app.cancel()
            return True
    return False


def get_applications_statistics(
    applications: List[Application],
) -> Dict[str, Any]:
    """Вычисляет сводную статистику по заявкам."""
    total = len(applications)
    approved = sum(1 for app in applications if not app.is_cancelled)
    cancelled = sum(1 for app in applications if app.is_cancelled)
    avg_gpa = (
        round(sum(app.student.gpa for app in applications) / total, 2)
        if total > 0 else 0.0
    )
    return {
        "total": total,
        "approved": approved,
        "cancelled": cancelled,
        "avg_gpa": avg_gpa,
    }


def show_applications(applications: List[Application]) -> None:
    """Выводит список поданных заявок с детализацией."""
    if not applications:
        print("\n[!] Список поданных заявок пуст.")
        return

    print("\n" + "=" * 95)
    print(f"{'№':<5} | {'Студент':<22} | {'Тема ID':<8} | {'GPA':<5} | {'Приоритет':<10} | {'Статус':<12} | {'Дата':<10}")
    print("-" * 95)
    for app in applications:
        print(
            f"{app.id:<5} | {app.student.name:<22} | {app.topic.id:<8} | "
            f"{app.student.gpa:<5.2f} | {app.priority:<10} | {app.status:<12} | {app.application_date:<10}"
        )
    print("=" * 95)


def format_application_summary(app: Application) -> str:
    """Формирует текстовую карточку заявки (преемственность ПР1-ПР2)."""
    return (
        "==================================================\n"
        f"КАРТОЧКА ЗАЯВКИ № {app.id}\n"
        "==================================================\n"
        f"Дата подачи:     {app.application_date}\n"
        f"Студент:         {app.student.name} ({app.student.course} курс)\n"
        f"Дисциплина:      {app.topic.discipline}\n"
        f"Тема работы:     {app.topic.title}\n"
        f"Науч. рук.:      {app.topic.supervisor}\n"
        f"Приоритет:       {app.priority}\n"
        f"Статус заявки:   {app.status}\n"
        "=================================================="
    )
