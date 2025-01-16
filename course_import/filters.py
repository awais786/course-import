"""
A custom OpenEdx filter for fetching course templates from dynamic sources.
"""
from openedx_filters.tooling import OpenEdxPublicFilter


class CourseTemplateRequested(OpenEdxPublicFilter):
    """
    This filter is designed to fetch course templates from various sources such as GitHub or S3.
    It utilizes the OpenEdx filter pipeline to handle dynamic and configurable template-fetching logic
    based on the source type and configuration provided.

    Attributes:
        filter_type (str): Specifies the unique identifier for this filter,
            allowing it to be used in the OpenEdx filter pipeline. The filter type
            is set to 'org.edly.templates.fetch.requested.v1'.
    """

    filter_type = "org.edly.templates.fetch.requested.v1"

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
