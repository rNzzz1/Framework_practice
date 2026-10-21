"""Команда наполнения базы данных начальными демонстрационными данными.

Запуск: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from topics.models import Discipline, Student, Topic, Application


class Command(BaseCommand):
    help = "Наполняет базу данных начальными данными для сервиса курсовых работ"

    def handle(self, *args, **options):
        self.stdout.write("Очистка старых данных...")
        Application.objects.all().delete()
        Topic.objects.all().delete()
        Student.objects.all().delete()
        Discipline.objects.all().delete()

        self.stdout.write("Создание дисциплин...")
        d1 = Discipline.objects.create(
            name="Технологии разработки приложений на базе фреймворков",
            code="ТРПБФ-01",
            department="Кафедра индустриального программирования",
        )
        d2 = Discipline.objects.create(
            name="Базы данных и экспертные системы",
            code="БД-02",
            department="Кафедра индустриального программирования",
        )
        d3 = Discipline.objects.create(
            name="Интеллектуальные информационные системы",
            code="ИИС-03",
            department="Кафедра индустриального программирования",
        )
        d4 = Discipline.objects.create(
            name="Тестирование и верификация программного обеспечения",
            code="ТВПО-04",
            department="Кафедра индустриального программирования",
        )
        d5 = Discipline.objects.create(
            name="Архитектура корпоративных информационных систем",
            code="АКИС-05",
            department="Кафедра индустриального программирования",
        )

        self.stdout.write("Создание студентов...")
        s1 = Student.objects.create(
            name="Узунян Овсеп Норайрович",
            course=3,
            gpa=4.75,
            is_budget=True,
            email="uzunano85@gmail.com",
        )
        s2 = Student.objects.create(
            name="Иванов Иван Иванович",
            course=3,
            gpa=4.60,
            is_budget=True,
            email="ivanov.i@edu.mirea.ru",
        )
        s3 = Student.objects.create(
            name="Смирнова Анна Сергеевна",
            course=2,
            gpa=4.10,
            is_budget=False,
            email="smirnova.a@edu.mirea.ru",
        )
        s4 = Student.objects.create(
            name="Петров Дмитрий Алексеевич",
            course=4,
            gpa=4.85,
            is_budget=True,
            email="petrov.d@edu.mirea.ru",
        )
        s5 = Student.objects.create(
            name="Ковалева Мария Павловна",
            course=3,
            gpa=3.40,
            is_budget=False,
            email="kovaleva.m@edu.mirea.ru",
        )

        self.stdout.write("Создание тем курсовых работ...")
        t1 = Topic.objects.create(
            title="Разработка веб-сервиса распределения курсовых работ на Django",
            discipline=d1,
            supervisor="доц. Ящун Т. В.",
            min_course=3,
            min_gpa=3.5,
            capacity=1,
            current_students=1,
            is_available=False,
        )
        t2 = Topic.objects.create(
            title="Проектирование микросервисной архитектуры корпоративного портала",
            discipline=d1,
            supervisor="доц. Ящун Т. В.",
            min_course=3,
            min_gpa=4.0,
            capacity=1,
            current_students=1,
            is_available=False,
        )
        t3 = Topic.objects.create(
            title="Разработка аналитической подсистемы учета успеваемости студентов",
            discipline=d2,
            supervisor="проф. Смирнов А. А.",
            min_course=2,
            min_gpa=3.2,
            capacity=2,
            current_students=0,
            is_available=True,
        )
        t4 = Topic.objects.create(
            title="Интеллектуальный рекомендательный модуль выбора курсовых проектов",
            discipline=d3,
            supervisor="доц. Петров И. С.",
            min_course=3,
            min_gpa=4.2,
            capacity=1,
            current_students=0,
            is_available=True,
        )
        t5 = Topic.objects.create(
            title="Система автоматизированного регрессионного тестирования веб-приложений",
            discipline=d4,
            supervisor="ст. преп. Кузнецова Е. В.",
            min_course=3,
            min_gpa=3.8,
            capacity=2,
            current_students=0,
            is_available=True,
        )
        t6 = Topic.objects.create(
            title="Разработка распределенного кэширования для высоконагруженных сервисов",
            discipline=d5,
            supervisor="проф. Смирнов А. А.",
            min_course=4,
            min_gpa=4.5,
            capacity=1,
            current_students=0,
            is_available=True,
        )

        self.stdout.write("Создание заявок...")
        Application.objects.create(
            topic=t1,
            student=s1,
            priority=s1.calculate_priority(),
            is_cancelled=False,
        )
        Application.objects.create(
            topic=t2,
            student=s4,
            priority=s4.calculate_priority(),
            is_cancelled=False,
        )
        Application.objects.create(
            topic=t3,
            student=s3,
            priority=s3.calculate_priority(),
            is_cancelled=True,
        )

        self.stdout.write(self.style.SUCCESS("База данных успешно наполнена начальными данными!"))
