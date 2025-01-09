"""
URLs for course_import.
"""
from django.urls import re_path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from course_import import views

app_name = 'course_import'

urlpatterns = [
    re_path(fr'^v0/import/{settings.COURSE_ID_PATTERN}/$',
            views.CourseImportView.as_view(), name='course_import'),
]
