"""Контекстные процессоры приложения topics.

Предоставляют глобальные переменные для шаблонов Django:
- site_name: название информационного сервиса
- site_short_name: сокращенное имя системы
- topics_total_count: общее количество тем курсовых работ
- active_topics_count: количество доступных для выбора тем
"""

from .models import Topic


def topic_context(request):
    """Возвращает контекст с глобальной информацией о сервисе курсовых работ."""
    try:
        topics_total = Topic.objects.count()
        active_topics = Topic.objects.filter(is_available=True).count()
    except Exception:
        topics_total = 0
        active_topics = 0

    return {
        "site_name": "Сервис выбора тем курсовых работ РТУ МИРЭА",
        "site_short_name": "CourseworkService",
        "topics_total_count": topics_total,
        "active_topics_count": active_topics,
    }
