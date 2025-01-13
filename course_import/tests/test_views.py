from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from user_tasks.models import UserTaskStatus

class PluginCourseImportViewTest(APITestCase):
    """
    Test importing courses via a plugin-based API (POST method only)
    """
    @patch('cms.djangoapps.contentstore.tasks.import_olx')
    def test_staff_import_succeeds_with_mock(self, mock_import_olx):
        """
        Test that a staff user can import a course via the plugin API
        """
        # Setup mocks
        mock_import_olx.return_value = MagicMock(task_id="1234")

        # Simulate logged-in staff
        self.client.login(username="staff", password="test_password")

        # Make a mocked API call
        with patch("cms.djangoapps.contentstore.storage.course_import_export_storage") as mock_storage:
            mock_storage.return_value.save.return_value = "mocked_path"
            breakpoint()
            response = self.client.post(
            reverse("course_import:course_templates_import", kwargs={"course_id": "course-v1:edX+DemoX+Demo_Course"}),
                {"course_data": "mocked_course_file.tar.gz"},
                format="multipart"
            )

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("task_id", response.data)
        self.assertEqual(response.data["task_id"], "1234")

    @patch('cms.djangoapps.contentstore.tasks.import_olx')
    def test_staff_import_fails_without_auth(self, mock_import_olx):
        """
        Test that an unauthorized user cannot access the API
        """
        mock_import_olx.return_value = MagicMock(task_id="1234")

        response = self.client.post(
            reverse("course_import:course_templates_import", kwargs={"course_id": "course-v1:edX+DemoX+Demo_Course"}),
            {"course_data": "mocked_course_file.tar.gz"},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
