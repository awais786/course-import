"""
Tests for pipeline and filter.
"""
import json
from unittest.mock import Mock, patch

from django.test import TestCase
from course_import.filters import CourseTemplateRequested


class TestPipelineStepDefinition(TestCase):
    """
    Test cases for pipeline step definitions in the Open edX filters.
    These tests cover scenarios for fetching course templates from GitHub.
    """

    def test_github_template_no_url(self):
        """
        Test that an error is returned if no source URL is provided.
        """
        expected_result = {"error": "Source config not provided", "status": 400}
        resp = CourseTemplateRequested.run_filter(
            source_type="github",
            **{'source_config': ""}
        )

        self.assertEqual(resp['result'], expected_result)

    @patch('course_import.pipeline.requests.get')
    def test_github_template_fetch(self, mock_get):
        """
        Test successful fetching of templates from GitHub.
        Verifies that a valid JSON response from the GitHub API is parsed correctly.
        """
        expected_result = b"""[
                        {
                            "courses_name": "AI Courses",
                            "zip_url": "https://course.2jyd4n_5.tar.gz",
                            "metadata": {
                                "title": "Introduction to Open edX",
                                "description": "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                                "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp",
                                "active": true
                            }
                        },
                        {
                            "courses_name": "Digital Marketing",
                            "zip_url": "https://course.2jyd4n_5.tar.gz",
                            "metadata": {
                                "title": "Introduction to Open edX",
                                "description": "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                                "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/08/Screenshot-2024-08-22-at-4.38.09-PM.png",
                                "active": true
                            }
                        }
            ]"""

        decoded_result = expected_result.decode('utf-8')
        parsed_json = json.loads(decoded_result)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = expected_result
        mock_response.json.return_value = parsed_json

        mock_get.return_value = mock_response

        resp = CourseTemplateRequested.run_filter(
            source_type="github",
            **{'source_config': "https://edly_courses.json"}
        )

        # Assert the expected result
        self.assertEqual(resp['result'], parsed_json)

    @patch('course_import.pipeline.requests.get')
    def test_github_template_fetch_empty_data(self, mock_get):
        """
        Test that an empty JSON response from GitHub is handled correctly.
        """
        expected_result = ""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = expected_result
        mock_response.json.return_value = ""

        mock_get.return_value = mock_response

        resp = CourseTemplateRequested.run_filter(
            source_type="github",
            **{'source_config': "https://no_data.json"}
        )

        self.assertEqual(resp['result']['error'], "Response content is empty")

    @patch('course_import.pipeline.requests.get')
    def test_github_template_fetch_invalid_url(self, mock_get):
        """
        Test that an error is returned when the GitHub API responds with a non-200 status code.
        """
        expected_result = b"""[]"""
        decoded_result = expected_result.decode('utf-8')
        parsed_json = json.loads(decoded_result)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = expected_result
        mock_response.json.return_value = parsed_json

        mock_get.return_value = mock_response

        resp = CourseTemplateRequested.run_filter(
            source_type="github",
            **{'source_config': "https://404.json"}
        )

        self.assertEqual(
            resp.get('result', {}).get('error'),
            "Failed to fetch from URL. Status code: 404"
        )

    @patch('course_import.pipeline.requests.get')
    def test_github_template_fetch_inactive_templates(self, mock_get):
        """
        Test filtering of inactive templates from GitHub.

        Ensures that only templates with `active` set to `True` are included
        in the result after processing a valid JSON response.
        """
        expected_result = b"""[
                           {
                               "courses_name": "AI Courses",
                               "zip_url": "https://course.2jyd4n_5.tar.gz",
                               "metadata": {
                                   "title": "Introduction to Open edX",
                                   "description": "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                                   "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp",
                                   "active": false
                               }
                           },
                           {
                               "courses_name": "Digital Marketing",
                               "zip_url": "https://course.2jyd4n_5.tar.gz",
                               "metadata": {
                                   "title": "Introduction to Open edX",
                                   "description": "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                                   "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/08/Screenshot-2024-08-22-at-4.38.09-PM.png",
                                   "active": true
                               }
                           }
               ]"""

        decoded_result = expected_result.decode('utf-8')
        parsed_json = json.loads(decoded_result)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = expected_result
        mock_response.json.return_value = parsed_json

        mock_get.return_value = mock_response

        resp = CourseTemplateRequested.run_filter(
            source_type="github",
            **{'source_config': "https://edly_courses.json"}
        )

        # Assert the expected result
        self.assertEqual(resp['result'][0], parsed_json[1])
        self.assertEqual(len(resp['result']), 1)
