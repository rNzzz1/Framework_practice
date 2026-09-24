"""Тесты для объектной модели Student."""

from models import Student
from models.students import add_student, find_students, find_student_by_id


def test_student_creation():
    """Проверка инициализации атрибутов объекта Student."""
    student = Student(
        student_id=1,
        name="Узунян Осип",
        course=3,
        gpa=4.75,
        is_budget=True,
        email="test@example.com",
    )
    assert student.id == 1
    assert student.name == "Узунян Осип"
    assert student.course == 3
    assert student.gpa == 4.75
    assert student.is_budget is True
    assert student.email == "test@example.com"


def test_student_priority():
    """Проверка расчета приоритета заявки студента."""
    student_budget = Student(1, "Студент 1", 3, 4.5, is_budget=True)
    student_contract = Student(2, "Студент 2", 3, 4.5, is_budget=False)

    # 4.5 * 20 = 90 + 10 = 100
    assert student_budget.calculate_priority() == 100
    # 4.5 * 20 = 90 + 0 = 90
    assert student_contract.calculate_priority() == 90


def test_student_serialization():
    """Проверка сериализации to_dict и десериализации from_dict."""
    data = {
        "id": 10,
        "name": "Иванов И. И.",
        "course": 4,
        "gpa": 4.2,
        "is_budget": False,
        "email": "ivanov@test.ru",
    }
    student = Student.from_dict(data)
    assert student.id == 10
    assert student.name == "Иванов И. И."
    assert student.to_dict() == data


def test_student_str():
    """Проверка метода __str__ класса Student."""
    student = Student(1, "Петров П. П.", 2, 4.0, True)
    assert "[1]" in str(student)
    assert "Петров П. П." in str(student)
    assert "Бюджет" in str(student)
