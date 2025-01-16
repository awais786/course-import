"""
Tests for authoring subdomain filters.
"""
from unittest.mock import MagicMock, patch

from django.test import TestCase

from course_import.filters import CourseTemplateRequested


class TestCourseTemplateRequested(TestCase):
    """
    Test pipeline step definition for the hooks execution mechanism.
    """
    def test_github_template_without_config(self):
        """
        Test successful fetching of templates from GitHub.
        """
        result = CourseTemplateRequested.run_filter(
            source_type="github", **{'test': ''}
        )
        self.assertEqual(result['result']['error'], 'Source config not provided')

    def test_github_template_fetch(self):
        """
        Test successful fetching of templates from GitHub.
        """
        # Set the mock return value
        expected_result = [
            {
                "courses_name": "AI Courses",
                "zip_url":
                    "https://raw.githubusercontent.com/awais786/courses/main/edly/AI%20Courses/course.2jyd4n_5.tar.gz",
                "metadata": {
                    "title": "Introduction to Open edX",
                    "description":
                        "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                    "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp",
                    "active": True
                }
            },
            {
                "courses_name": "Digital Marketing",
                "zip_url":
                    "https://raw.githubusercontent.com/awais786/courses/main/edly/Digital%20Marketing/course.tar.gz",
                "metadata": {
                    "title": "Introduction to Open edX",
                    "description":
                        "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
                    "thumbnail":
                        "https://discover.ilmx.org/wp-content/uploads/2024/08/Screenshot-2024-08-22-at-4.38.09-PM.png",
                    "active": True
                }
            }
        ]

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = expected_result
            mock_get.return_value = mock_response

            resp = CourseTemplateRequested.run_filter(
                source_type="github",
                **{
                    'source_config': "https://test/awais786/courses/refs/heads/main/edly_courses.json"}
            )

            self.assertEqual(resp['result'], expected_result)
