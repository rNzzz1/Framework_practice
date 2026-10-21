"""Модели данных Django ORM для сервиса выбора тем курсовых работ.

Сущности:
- Discipline (Дисциплина)
- Student (Студент)
- Topic (Тема курсовой работы)
- Application (Заявка на тему)
"""

from django.db import models
from django.core.exceptions import ValidationError


class Discipline(models.Model):
    """Модель академической дисциплины кафедры."""

    name = models.CharField(
        max_length=200,
        verbose_name="Наименование дисциплины",
        unique=True,
    )
    code = models.CharField(
        max_length=50,
        verbose_name="Код дисциплины",
        blank=True,
    )
    department = models.CharField(
        max_length=200,
        verbose_name="Кафедра",
        default="Кафедра индустриального программирования",
    )

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Student(models.Model):
    """Модель студента — соискателя темы курсовой работы."""

    name = models.CharField(
        max_length=150,
        verbose_name="ФИО студента",
    )
    course = models.PositiveSmallIntegerField(
        verbose_name="Курс обучения",
        default=3,
    )
    gpa = models.FloatField(
        verbose_name="Средний балл (GPA)",
        default=4.0,
    )
    is_budget = models.BooleanField(
        verbose_name="Бюджетная форма обучения",
        default=True,
    )
    email = models.EmailField(
        verbose_name="Электронная почта",
        unique=True,
    )

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["name"]

    def calculate_priority(self) -> int:
        """Рассчитывает рейтинговый балл заявки на основе GPA и формы обучения."""
        base = int(float(self.gpa) * 20)
        bonus = 10 if self.is_budget else 0
        return base + bonus

    def __str__(self) -> str:
        budget_str = "Бюджет" if self.is_budget else "Договор"
        return f"{self.name} ({self.course} курс, GPA: {self.gpa:.2f}, {budget_str})"


class Topic(models.Model):
    """Модель темы курсовой работы."""

    title = models.CharField(
        max_length=255,
        verbose_name="Название темы",
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="Дисциплина",
    )
    supervisor = models.CharField(
        max_length=150,
        verbose_name="Научный руководитель",
    )
    min_course = models.PositiveSmallIntegerField(
        verbose_name="Минимальный курс",
        default=3,
    )
    min_gpa = models.FloatField(
        verbose_name="Минимальный балл GPA",
        default=3.5,
    )
    capacity = models.PositiveSmallIntegerField(
        verbose_name="Квота мест",
        default=1,
    )
    current_students = models.PositiveSmallIntegerField(
        verbose_name="Количество записанных студентов",
        default=0,
    )
    is_available = models.BooleanField(
        verbose_name="Доступна для выбора",
        default=True,
    )

    class Meta:
        verbose_name = "Тема курсовой работы"
        verbose_name_plural = "Темы курсовых работ"
        ordering = ["title"]

    def is_suitable_for(self, student_course: int, gpa: float) -> bool:
        """Проверяет соответствие студента требованиям темы."""
        return (student_course >= self.min_course) and (gpa >= self.min_gpa)

    def has_free_capacity(self) -> bool:
        """Проверяет наличие свободных мест по квоте."""
        return self.current_students < self.capacity

    def reserve_slot(self) -> bool:
        """Резервирует место на тему при подаче заявки."""
        if not self.has_free_capacity() or not self.is_available:
            return False
        self.current_students += 1
        if self.current_students >= self.capacity:
            self.is_available = False
        self.save()
        return True

    def release_slot(self) -> None:
        """Освобождает место при отмене заявки."""
        self.current_students = max(0, self.current_students - 1)
        self.is_available = True
        self.save()

    def clean(self) -> None:
        if self.current_students > self.capacity:
            raise ValidationError("Число записанных студентов не может превышать квоту темы.")

    def __str__(self) -> str:
        status_text = "Свободна" if (self.is_available and self.has_free_capacity()) else "Занята"
        return f"[{self.id}] {self.title} ({self.discipline.name}) — {status_text}"


class Application(models.Model):
    """Модель заявки студента на закрепление темы курсовой работы."""

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Тема курсовой работы",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Студент-соискатель",
    )
    application_date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата подачи заявки",
    )
    priority = models.IntegerField(
        verbose_name="Рейтинговый балл / приоритет",
        default=0,
    )
    is_cancelled = models.BooleanField(
        verbose_name="Заявка отменена",
        default=False,
    )

    class Meta:
        verbose_name = "Заявка на курсовую работу"
        verbose_name_plural = "Заявки на курсовые работы"
        ordering = ["-application_date", "-id"]

    @property
    def status(self) -> str:
        """Динамическое свойство статуса заявки."""
        return "ОТМЕНЕНА" if self.is_cancelled else "ОДОБРЕНА"

    def cancel(self) -> None:
        """Отменяет заявку и освобождает квоту на тему."""
        if not self.is_cancelled:
            self.is_cancelled = True
            self.save()
            self.topic.release_slot()

    def save(self, *args, **kwargs) -> None:
        if not self.priority and self.student_id:
            self.priority = self.student.calculate_priority()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Заявка №{self.id}: {self.student.name} -> [{self.topic.id}] {self.topic.title} ({self.status})"
