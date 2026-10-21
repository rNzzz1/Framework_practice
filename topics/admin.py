"""Настройка панели администратора Django для сервиса выбора тем курсовых работ."""

from django.contrib import admin
from .models import Discipline, Student, Topic, Application


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department")
    search_fields = ("name", "code")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "gpa", "is_budget", "email")
    list_filter = ("course", "is_budget")
    search_fields = ("name", "email")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "discipline", "supervisor", "min_course", "min_gpa", "capacity", "current_students", "is_available")
    list_filter = ("discipline", "min_course", "is_available")
    search_fields = ("title", "supervisor")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "topic", "application_date", "priority", "status", "is_cancelled")
    list_filter = ("is_cancelled", "application_date")
    search_fields = ("student__name", "topic__title")
