"""
URLs for course_import.
"""
from django.urls import re_path, path, include  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from course_import import views
from django.conf import settings

app_name = 'course_import'  # Define the namespace here


# endpoint will be accessible like this /course_import_api/import/course-v1:edX+DemoX+Demo_Course/
app_url_patterns = (
    [
        # reverse("course_import:course_templates_import")
        re_path(fr'^import/{settings.COURSE_ID_PATTERN}/$', views.CourseImportView.as_view(),
                name='course_templates_import'),

    ]
    , "course_import",
)

urlpatterns = [
    path("", include(app_url_patterns)),
]
