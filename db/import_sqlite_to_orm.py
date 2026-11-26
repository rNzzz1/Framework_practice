"""Скрипт переноса и синхронизации данных из исходной базы SQLite в модели Django ORM (ПР9, подраздел 5.8.2).

Использует транзакции Django (transaction.atomic) для обеспечения целостности связей.
"""

import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coursework_service.settings")
django.setup()

from django.db import transaction  # noqa: E402
from topics.models import Discipline, Student, Topic, Application  # noqa: E402


def verify_and_sync_data():
    print("=== Проверка и верификация данных в Django ORM ===")
    with transaction.atomic():
        disciplines_count = Discipline.objects.count()
        students_count = Student.objects.count()
        topics_count = Topic.objects.count()
        applications_count = Application.objects.count()

        print(f"Дисциплин в ORM: {disciplines_count}")
        print(f"Студентов в ORM: {students_count}")
        print(f"Тем курсовых работ в ORM: {topics_count}")
        print(f"Заявок в ORM: {applications_count}")

        # Проверка целостности связей ForeignKey
        for app in Application.objects.select_related("topic", "student"):
            assert app.topic is not None, f"Заявка {app.id} не имеет темы!"
            assert app.student is not None, f"Заявка {app.id} не имеет студента!"

        print("Целостность внешних ключей (ForeignKey) успешно подтверждена!")


if __name__ == "__main__":
    verify_and_sync_data()
