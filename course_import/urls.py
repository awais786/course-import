"""
URLs for course_import.
"""
from django.urls import re_path, path, include  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from course_import import views
from django.conf import settings

app_name = 'course_import'  # Define the namespace here

app_url_patterns = (
    [
        re_path(r'import/$',  # Correct URL pattern
            views.CourseTemplatesImportView.as_view(),
                name='course_templates_import'),  # URL name for reverse lookup
    ]
    , "course_import",
)

urlpatterns = [
    path("", include(app_url_patterns)),
]
