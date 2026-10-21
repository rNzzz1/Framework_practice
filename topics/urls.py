"""Маршрутизация URL для приложения topics."""

from django.urls import path
from . import views

urlpatterns = [
    # Веб-страницы (UI)
    path("", views.index_view, name="index"),
    path("topic/<int:pk>/", views.topic_detail_view, name="topic_detail"),
    path("students/", views.students_list_view, name="students_list"),
    path("applications/", views.applications_list_view, name="applications_list"),
    path("apply/", views.apply_view, name="apply"),
    path("applications/<int:pk>/cancel/", views.cancel_application_view, name="cancel_application"),
    path("statistics/", views.statistics_view, name="statistics"),

    # RESTful API эндпоинты
    path("api/topics/", views.api_topics_list, name="api_topics_list"),
    path("api/topics/<int:pk>/", views.api_topic_detail, name="api_topic_detail"),
    path("api/applications/create/", views.api_create_application, name="api_create_application"),
    path("api/statistics/", views.api_statistics, name="api_statistics"),
    path("api/health/", views.api_health, name="api_health"),
]
