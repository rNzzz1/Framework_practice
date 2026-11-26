"""Формы веб-приложения сервиса выбора тем курсовых работ (ПР11: Формы в Django).

Включает:
- TopicFilterForm (forms.Form): форма фильтрации и поиска с передачей параметров через GET-запрос
- ApplicationForm (forms.ModelForm): форма подачи заявки с кросс-полевой валидацией
- ApplicationEditForm (forms.ModelForm): форма изменения заявки с учетом параметра instance
- TopicForm (forms.ModelForm): форма создания/редактирования тем курсовых работ с поддержкой ImageField
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Discipline, Student, Topic, Application


class TopicFilterForm(forms.Form):
    """Форма фильтрации и поиска каталога тем курсовых работ (GET-запросы)."""

    q = forms.CharField(
        required=False,
        label="Поисковый запрос",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по названию темы, руководителю...",
            }
        ),
    )
    discipline = forms.ModelChoiceField(
        queryset=Discipline.objects.all(),
        required=False,
        empty_label="Все дисциплины",
        label="Дисциплина",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    min_course = forms.ChoiceField(
        choices=[
            ("", "Любой курс"),
            ("1", "1 курс"),
            ("2", "2 курс"),
            ("3", "3 курс"),
            ("4", "4 курс"),
        ],
        required=False,
        label="Курс обучения",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        choices=[
            ("title", "По названию (А-Я)"),
            ("-title", "По названию (Я-А)"),
            ("min_gpa", "По минимальному GPA (по возрастанию)"),
            ("-min_gpa", "По минимальному GPA (по убыванию)"),
            ("capacity", "По квоте мест (по возрастанию)"),
            ("-capacity", "По квоте мест (по убыванию)"),
        ],
        required=False,
        label="Сортировка",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class ApplicationForm(forms.ModelForm):
    """Форма подачи новой заявки на закрепление темы (ModelForm)."""

    class Meta:
        model = Application
        fields = ["student", "topic"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "topic": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "student": "Студент-соискатель",
            "topic": "Тема курсовой работы",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Отображаем только доступные темы в выпадающем списке
        self.fields["topic"].queryset = Topic.objects.filter(is_available=True).order_by("title")
        self.fields["student"].queryset = Student.objects.all().order_by("name")

    def clean(self):
        """Комплексная бизнес-валидация подачи заявки."""
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        topic = cleaned_data.get("topic")

        if not student or not topic:
            return cleaned_data

        # 1. Проверка повторной подачи активной заявки
        existing_active = Application.objects.filter(
            student=student,
            topic=topic,
            status=Application.Status.ACTIVE,
        )
        if existing_active.exists():
            raise ValidationError(
                f"Студент «{student.name}» уже имеет активную утвержденную заявку на тему «{topic.title}»."
            )

        # 2. Проверка академического допуска студента (курс и средний балл GPA)
        if not topic.is_suitable_for(student.course, student.gpa):
            raise ValidationError(
                f"Студент {student.name} не соответствует академическим требованиям темы: "
                f"требуется курс >= {topic.min_course} (у студента {student.course}), "
                f"GPA >= {topic.min_gpa:.2f} (у студента {student.gpa:.2f})."
            )

        # 3. Проверка доступности квоты мест темы
        if not topic.has_free_capacity() or not topic.is_available:
            raise ValidationError(
                f"На тему «{topic.title}» исчерпана квота свободных мест ({topic.current_students}/{topic.capacity})."
            )

        return cleaned_data


class ApplicationEditForm(forms.ModelForm):
    """Форма редактирования существующей заявки с использованием instance."""

    class Meta:
        model = Application
        fields = ["student", "topic", "status"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "topic": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "student": "Студент-соискатель",
            "topic": "Тема курсовой работы",
            "status": "Статус заявки",
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        topic = cleaned_data.get("topic")
        status = cleaned_data.get("status")

        if not student or not topic:
            return cleaned_data

        # Исключаем текущую редактируемую запись из проверки дубликатов
        query = Application.objects.filter(
            student=student,
            topic=topic,
            status=Application.Status.ACTIVE,
        )
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if status == Application.Status.ACTIVE and query.exists():
            raise ValidationError(
                f"Студент «{student.name}» уже имеет другую активную заявку на тему «{topic.title}»."
            )

        # Проверка академических критериев
        if status == Application.Status.ACTIVE and not topic.is_suitable_for(student.course, student.gpa):
            raise ValidationError(
                f"Студент {student.name} не удовлетворяет требованиям темы: "
                f"курс {student.course} < {topic.min_course} или GPA {student.gpa:.2f} < {topic.min_gpa:.2f}."
            )

        return cleaned_data


class TopicForm(forms.ModelForm):
    """Форма создания и редактирования темы курсовой работы с поддержкой загрузки изображений."""

    class Meta:
        model = Topic
        fields = [
            "title",
            "discipline",
            "supervisor",
            "min_course",
            "min_gpa",
            "capacity",
            "is_available",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите название темы"}),
            "discipline": forms.Select(attrs={"class": "form-select"}),
            "supervisor": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "ФИО руководителя, должность"}
            ),
            "min_course": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 6}),
            "min_gpa": forms.NumberInput(attrs={"class": "form-control", "step": "0.1", "min": "2.0", "max": "5.0"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 10}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Название темы",
            "discipline": "Академическая дисциплина",
            "supervisor": "Научный руководитель",
            "min_course": "Минимальный курс",
            "min_gpa": "Минимальный средний балл (GPA)",
            "capacity": "Квота мест",
            "is_available": "Доступна для записи",
            "image": "Иллюстрация / схема темы",
        }

    def clean_capacity(self):
        capacity = self.cleaned_data.get("capacity")
        if capacity is not None and capacity < 1:
            raise ValidationError("Квота мест темы должна быть не менее 1.")
        return capacity

    def clean_min_gpa(self):
        min_gpa = self.cleaned_data.get("min_gpa")
        if min_gpa is not None and (min_gpa < 2.0 or min_gpa > 5.0):
            raise ValidationError("Минимальный средний балл должен быть в диапазоне от 2.0 до 5.0.")
        return min_gpa
