"""
Package where filters related to the Course Authoring architectural.
"""
from openedx_filters.tooling import OpenEdxPublicFilter

class CourseTemplateRequested(OpenEdxPublicFilter):
    """
    Custom class for fetching templates from dynamic sources.
    """
    filter_type = "org.openedx.templates.fetch.requested.v1"

    @classmethod
    def run_filter(cls, source_type, **kwargs):
        """
        Fetch templates from a specified source.
        Arguments:
            source_type (str): The type of source ('github' or 's3').
            source_config (dict): Configuration for the source (e.g., URL for GitHub, bucket/key for S3).
        Returns:
            dict: Templates fetched from the source.
        Raises:
            TemplateFetchException: If fetching templates fails.
        """

        result = super().run_pipeline(source_type=source_type, **kwargs)
        return result
