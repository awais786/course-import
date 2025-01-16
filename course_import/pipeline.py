"""
Pipeline steps for course templates. These will be move to some where else.
"""

import requests

from openedx_filters import PipelineStep


class GithubTemplatesPipeline(PipelineStep):
    """
    A single-step pipeline to fetch templates from various sources such as GitHub or S3.
    """

    def run_filter(self, source_type, **kwargs):     # pylint: disable=arguments-differ
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
        if source_type == "github":
            return {"result": self.fetch_from_github(**kwargs)}
        else:
            return {}

    def fetch_from_github(self, **kwargs):
        """
        Fetches and processes raw file data directly from raw GitHub URL.
        """
        try:
            source_config = kwargs.get('source_config')
            headers = kwargs.get('headers', {})
            if not source_config:
                return {"error": "Source config not provided", "status": 400}

            response = requests.get(source_config, headers=headers)    # pylint: disable=missing-timeout
            if response.status_code == 200:
                if response.content.strip():  # Ensure the response content is not empty
                    try:
                        data = response.json()  # Attempt to parse JSON
                        if data:  # Check if the JSON is not empty
                            active_courses = [course for course in data if course['metadata'].get('active') is True]
                            return active_courses
                        else:
                            return []
                    except ValueError as e:
                        raise ValueError(f"Failed to parse JSON: {e}") from e
                else:
                    return []
            else:
                raise Exception(f"Failed to fetch from URL. Status code: {response.status_code}")

        except Exception as err:    # pylint: disable=broad-except
            return {"error": f"Error fetching: {err}", "status": 500}
