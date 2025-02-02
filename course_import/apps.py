"""
course_import Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins import PluginURLs


class CourseImportConfig(AppConfig):
    name = 'course_import'
    verbose_name = "Course Import API"

    plugin_app = {
        PluginURLs.CONFIG: {
            "cms.djangoapp": {
                PluginURLs.NAMESPACE: "course_import_api",  # Define namesp
                PluginURLs.REGEX: r"^course_import_api/",
                PluginURLs.RELATIVE_PATH: "urls",
            },
        },
    }
