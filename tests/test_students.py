"""Тесты для объектной модели Student."""

import unittest
from models import Student
from models.students import add_student, find_students, find_student_by_id


class TestStudentModel(unittest.TestCase):
    """Набор тестов для сущности Student."""

    def test_student_creation(self):
        """Проверка инициализации атрибутов объекта Student."""
        student = Student(
            student_id=1,
            name="Узунян Овсеп Норайрович",
            course=3,
            gpa=4.75,
            is_budget=True,
            email="test@example.com",
        )
        self.assertEqual(student.id, 1)
        self.assertEqual(student.name, "Узунян Овсеп Норайрович")
        self.assertEqual(student.course, 3)
        self.assertEqual(student.gpa, 4.75)
        self.assertTrue(student.is_budget)
        self.assertEqual(student.email, "test@example.com")

    def test_student_priority(self):
        """Проверка расчета приоритета заявки студента."""
        student_budget = Student(1, "Студент 1", 3, 4.5, is_budget=True)
        student_contract = Student(2, "Студент 2", 3, 4.5, is_budget=False)

        # 4.5 * 20 = 90 + 10 = 100
        self.assertEqual(student_budget.calculate_priority(), 100)
        # 4.5 * 20 = 90 + 0 = 90
        self.assertEqual(student_contract.calculate_priority(), 90)

    def test_student_serialization(self):
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
        self.assertEqual(student.id, 10)
        self.assertEqual(student.name, "Иванов И. И.")
        self.assertEqual(student.to_dict(), data)

    def test_student_helpers(self):
        """Проверка вспомогательных функций add_student, find_students, find_student_by_id."""
        students = []
        new_s = add_student(students, "Тестов Т. Т.", 3, 4.0, True, "test@test.ru")
        self.assertEqual(len(students), 1)
        self.assertEqual(new_s.id, 1)

        found = find_students(students, "тестов")
        self.assertEqual(len(found), 1)

        by_id = find_student_by_id(students, 1)
        self.assertIsNotNone(by_id)
        self.assertEqual(by_id.name, "Тестов Т. Т.")


if __name__ == "__main__":
    unittest.main()
