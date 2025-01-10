"""
course_import Django application initialization.
"""

from django.apps import AppConfig
from django.urls import path, include
from edx_django_utils.plugins import PluginSettings, PluginSignals, PluginURLs


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

    def ready(self):
        """Load modules of Aspects."""
        super().ready()

