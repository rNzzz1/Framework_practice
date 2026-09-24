"""Модуль описания класса Student и функций работы с коллекциями студентов."""

from typing import List, Dict, Any, Optional


class Student:
    """Класс, представляющий студента — соискателя темы курсовой работы."""

    def __init__(
        self,
        student_id: int,
        name: str,
        course: int,
        gpa: float,
        is_budget: bool = True,
        email: str = "",
    ) -> None:
        """Создает объект студента."""
        self.id = student_id
        self.name = name.strip()
        self.course = course
        self.gpa = round(gpa, 2)
        self.is_budget = is_budget
        self.email = email.strip()

    def calculate_priority(self) -> int:
        """Рассчитывает рейтинг/приоритет заявки студента."""
        base = int(self.gpa * 20)
        bonus = 10 if self.is_budget else 0
        return base + bonus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Создает объект студента из словаря данных JSON."""
        return cls(
            student_id=int(data["id"]),
            name=str(data["name"]),
            course=int(data["course"]),
            gpa=float(data["gpa"]),
            is_budget=bool(data.get("is_budget", True)),
            email=str(data.get("email", "")),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект студента в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "course": self.course,
            "gpa": self.gpa,
            "is_budget": self.is_budget,
            "email": self.email,
        }

    def __str__(self) -> str:
        """Строковое представление студента."""
        budget_str = "Бюджет" if self.is_budget else "Договор"
        return f"[{self.id}] {self.name} ({self.course} курс, GPA: {self.gpa}, {budget_str})"


def add_student(
    students: List[Student],
    name: str,
    course: int,
    gpa: float,
    is_budget: bool = True,
    email: str = "",
) -> Student:
    """Создает новый объект Student и добавляет его в коллекцию."""
    new_id = max((s.id for s in students), default=0) + 1
    student = Student(
        student_id=new_id,
        name=name,
        course=course,
        gpa=gpa,
        is_budget=is_budget,
        email=email,
    )
    students.append(student)
    return student


def find_student_by_id(students: List[Student], student_id: int) -> Optional[Student]:
    """Находит объект студента по идентификатору."""
    for student in students:
        if student.id == student_id:
            return student
    return None


def find_students(students: List[Student], query: str) -> List[Student]:
    """Ищет студентов по подстроке в ФИО или email."""
    lowered = query.lower().strip()
    return [
        s for s in students
        if lowered in s.name.lower() or lowered in s.email.lower()
    ]


def show_students(students: List[Student]) -> None:
    """Выводит список студентов в виде таблицы."""
    if not students:
        print("\n[!] Список студентов пуст.")
        return

    print("\n" + "=" * 75)
    print(f"{'ID':<4} | {'ФИО студента':<25} | {'Курс':<5} | {'GPA':<5} | {'Форма':<10} | {'Email':<20}")
    print("-" * 75)
    for s in students:
        b_str = "Бюджет" if s.is_budget else "Договор"
        print(f"{s.id:<4} | {s.name:<25} | {s.course:<5} | {s.gpa:<5.2f} | {b_str:<10} | {s.email:<20}")
    print("=" * 75)
