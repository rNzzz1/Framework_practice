"""Модели данных Django ORM для сервиса выбора тем курсовых работ.

Сущности:
- Discipline (Дисциплина)
- Student (Студент)
- Topic (Тема курсовой работы)
- Application (Заявка на тему)
"""

from datetime import date
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode


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
    is_honor_student = models.GeneratedField(
        expression=models.Case(
            models.When(gpa__gte=4.5, then=models.Value(True)),
            default=models.Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Студент-отличник",
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
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="URL-слаг темы",
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.PROTECT,
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
    image = models.ImageField(
        upload_to="topics/",
        blank=True,
        null=True,
        verbose_name="Иллюстрация темы",
    )
    is_competitive = models.GeneratedField(
        expression=models.Case(
            models.When(capacity__gt=1, then=models.Value(True)),
            default=models.Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Командная/Конкурсная тема",
    )

    class Meta:
        verbose_name = "Тема курсовой работы"
        verbose_name_plural = "Темы курсовых работ"
        ordering = ["title"]

    def is_suitable_for(self, student_course: int, gpa: float) -> bool:
        """Проверяет соответствие студента академическим требованиям темы."""
        return (student_course >= self.min_course) and (gpa >= self.min_gpa)

    def has_free_capacity(self) -> bool:
        """Проверяет наличие свободных мест по квоте с учетом активных заявок."""
        active_apps_count = self.applications.filter(status=Application.Status.ACTIVE).count()
        return active_apps_count < self.capacity

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

    def get_absolute_url(self) -> str:
        """Возвращает канонический URL темы по слагу."""
        if self.slug:
            return reverse("topic_detail_slug", kwargs={"slug": self.slug})
        return reverse("topic_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs) -> None:
        """Автоматическая генерация уникального слага из названия темы."""
        if not self.slug:
            transliterated = unidecode(self.title)
            base_slug = slugify(transliterated)[:200]
            if not base_slug:
                base_slug = "topic"
            candidate = base_slug
            counter = 1
            while Topic.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        status_text = "Свободна" if (self.is_available and self.has_free_capacity()) else "Занята"
        return f"[{self.id}] {self.title} ({self.discipline.name}) — {status_text}"


class ApplicationQuerySet(models.QuerySet):
    """Кастомный QuerySet для заявок на темы курсовых работ."""

    def active(self):
        """Возвращает только активные (утвержденные) заявки."""
        return self.filter(status=Application.Status.ACTIVE)

    def cancelled(self):
        """Возвращает аннулированные заявки."""
        return self.filter(status=Application.Status.CANCELLED)

    def completed(self):
        """Возвращает успешно защищенные/завершенные заявки."""
        return self.filter(status=Application.Status.COMPLETED)

    def for_date(self, target_date):
        """Фильтрует заявки по заданной дате подачи."""
        return self.filter(application_date=target_date)


class ApplicationManager(models.Manager.from_queryset(ApplicationQuerySet)):
    """Менеджер записей заявок с методами фильтрации по статусам."""
    pass


class Application(models.Model):
    """Модель заявки студента на закрепление темы курсовой работы."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Активна"
        CANCELLED = "cancelled", "Отменена"
        COMPLETED = "completed", "Завершена"

    topic = models.ForeignKey(
        Topic,
        on_delete=models.PROTECT,
        related_name="applications",
        verbose_name="Тема курсовой работы",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="applications",
        verbose_name="Студент-соискатель",
    )
    application_date = models.DateField(
        default=date.today,
        verbose_name="Дата подачи заявки",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус заявки",
    )
    priority = models.IntegerField(
        verbose_name="Рейтинговый балл / приоритет",
        default=0,
    )

    objects = ApplicationManager()

    class Meta:
        verbose_name = "Заявка на курсовую работу"
        verbose_name_plural = "Заявки на курсовые работы"
        ordering = ["-application_date", "-id"]

    @property
    def is_cancelled(self) -> bool:
        """Обратная совместимость со старым булевым флагом."""
        return self.status == self.Status.CANCELLED

    @is_cancelled.setter
    def is_cancelled(self, value: bool) -> None:
        self.status = self.Status.CANCELLED if value else self.Status.ACTIVE

    def cancel(self) -> None:
        """Отменяет заявку и освобождает квоту на тему."""
        if self.status != self.Status.CANCELLED:
            self.status = self.Status.CANCELLED
            self.save(update_fields=["status"])
            self.topic.release_slot()

    def save(self, *args, **kwargs) -> None:
        if not self.priority and self.student_id:
            self.priority = self.student.calculate_priority()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"Заявка №{self.id}: {self.student.name} -> "
            f"[{self.topic.id}] {self.topic.title} ({self.get_status_display()})"
        )
