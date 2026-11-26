"""Настройка полнофункциональной административной панели Django для сервиса выбора тем курсовых работ.

Включает:
- Стилизованные заголовки панели управления РТУ МИРЭА
- ModelAdmin с list_display, list_display_links, list_filter, search_fields, ordering
- Inlines (табличное отображение заявок внутри карточек студентов и тем)
- Autocomplete поля и date_hierarchy
- list_select_related для исключения N+1 SQL-запросов
- Пользовательские групповые действия (Admin Actions)
- Безопасное инлайн-редактирование и ссылки перехода на сайт (view_on_site)
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Discipline, Student, Topic, Application

# Кастомизация заголовков административного интерфейса РТУ МИРЭА
admin.site.site_header = "Панель управления сервисом курсовых работ РТУ МИРЭА"
admin.site.site_title = "Курсовые работы ИПТИП"
admin.site.index_title = "Администрирование учебного процесса и тем курсовых работ"


class ApplicationTabularInline(admin.TabularInline):
    """Встроенное табличное отображение заявок."""
    model = Application
    extra = 0
    fields = ("student", "topic", "application_date", "status", "priority")
    readonly_fields = ("application_date", "priority")
    show_change_link = True
    can_delete = False


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    """Администрирование академических дисциплин."""
    list_display = ("id", "name", "code", "department", "topics_count")
    list_display_links = ("id", "name")
    search_fields = ("name", "code", "department")
    ordering = ("name",)
    list_per_page = 20

    @admin.display(description="Кол-во тем")
    def topics_count(self, obj: Discipline) -> int:
        return obj.topics.count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Администрирование студентов-соискателей."""
    list_display = (
        "id",
        "name",
        "course",
        "gpa",
        "is_honor_student",
        "is_budget",
        "email",
        "applications_count",
    )
    list_display_links = ("id", "name")
    list_filter = ("course", "is_budget")
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("id", "is_honor_student")
    inlines = [ApplicationTabularInline]

    @admin.display(description="Подано заявок")
    def applications_count(self, obj: Student) -> int:
        return obj.applications.count()


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Администрирование тем курсовых работ."""
    list_display = (
        "id",
        "title",
        "discipline",
        "supervisor",
        "capacity",
        "current_students",
        "is_available",
        "is_competitive",
        "site_link",
    )
    list_display_links = ("id", "title")
    list_filter = ("discipline", "min_course", "is_available")
    search_fields = ("title", "supervisor", "discipline__name")
    list_editable = ("capacity",)
    ordering = ("title",)
    list_per_page = 20
    readonly_fields = ("id", "slug", "current_students", "is_competitive")
    autocomplete_fields = ("discipline",)
    inlines = [ApplicationTabularInline]
    view_on_site = True

    @admin.display(description="Ссылка на сайте")
    def site_link(self, obj: Topic) -> str:
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank">Просмотр ↗</a>', url)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Администрирование заявок на закрепление тем."""
    list_display = (
        "id",
        "student",
        "topic",
        "application_date",
        "status",
        "priority",
        "status_badge",
    )
    list_display_links = ("id", "student")
    list_filter = ("status", "application_date", "topic__discipline")
    search_fields = ("student__name", "topic__title", "student__email")
    ordering = ("-application_date", "-id")
    date_hierarchy = "application_date"
    list_select_related = ("student", "topic", "topic__discipline")
    autocomplete_fields = ("student", "topic")
    readonly_fields = ("id", "priority")
    list_per_page = 20
    actions = ["cancel_applications", "restore_applications"]

    @admin.action(description="Отменить выбранные заявки")
    def cancel_applications(self, request, queryset):
        """Пакетное действие отмены заявок с освобождением квот тем."""
        count = 0
        for app in queryset:
            if app.status != Application.Status.CANCELLED:
                app.cancel()
                count += 1
        self.message_user(request, f"Успешно аннулировано {count} заявок с освобождением квот.")

    @admin.action(description="Восстановить (активировать) выбранные заявки")
    def restore_applications(self, request, queryset):
        """Пакетное действие восстановления заявок в статус активных."""
        count = 0
        for app in queryset:
            if app.status != Application.Status.ACTIVE:
                app.status = Application.Status.ACTIVE
                app.save(update_fields=["status"])
                app.topic.reserve_slot()
                count += 1
        self.message_user(request, f"Восстановлено в статус активных: {count} заявок.")

    @admin.display(description="Индикатор статуса")
    def status_badge(self, obj: Application) -> str:
        colors = {
            Application.Status.ACTIVE: "#2ea44f",
            Application.Status.CANCELLED: "#cf222e",
            Application.Status.COMPLETED: "#0969da",
        }
        color = colors.get(obj.status, "#656d76")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )
