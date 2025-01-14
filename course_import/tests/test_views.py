import os
import tarfile
import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.urls import reverse
from path import Path as path
from rest_framework import status
from rest_framework.test import APITestCase
from user_tasks.models import UserTaskStatus


class PluginCourseImportViewTest(APITestCase):
    """
    Test importing courses via a plugin-based API (POST method only)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.course_id = "course-v1:edX+DemoX+Demo_Course"
        cls.password = "test_password"  # Set the password here
        cls.staff_user = User.objects.create_user(username="staff", password=cls.password, is_staff=True)

        cls.course_key = cls.course_id
        cls.password = 'test'
        cls.content_dir = path(tempfile.mkdtemp())

        # Create tar test files -----------------------------------------------
        # OK course:
        good_dir = tempfile.mkdtemp(dir=cls.content_dir)
        # test course being deeper down than top of tar file
        embedded_dir = os.path.join(good_dir, "grandparent", "parent")
        os.makedirs(os.path.join(embedded_dir, "course"))

        with open(os.path.join(embedded_dir, "course.xml"), "w+") as f:
            f.write('<course url_name="2013_Spring" org="EDx" course="0.00x"/>')

        with open(os.path.join(embedded_dir, "course", "2013_Spring.xml"), "w+") as f:
            f.write('<course></course>')

        cls.good_tar_filename = "good.tar.gz"
        cls.good_tar_fullpath = os.path.join(cls.content_dir, cls.good_tar_filename)
        with tarfile.open(cls.good_tar_fullpath, "w:gz") as gtar:
            gtar.add(good_dir)

    def test_staff_with_access_import_course_by_url_succeeds(self):
        """
        Test that a staff user can access the API and successfully import a course using a URL
        """
        # Login as staff user
        self.client.login(username=self.staff_user.username, password=self.password)

        # Mocked URL and file content
        file_url = "https://example.com/test-course.tar.gz"
        with open(self.good_tar_fullpath, 'rb') as fp:
            file_content = fp.read()

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = (file_content[i:i + 1024] for i in
                                                       range(0, len(file_content), 1024))
            mock_get.return_value = mock_response

            with patch('cms.djangoapps.contentstore.tasks.import_olx.delay') as mock_delay:
                # Make the API request for course import
                mock_async_result = MagicMock()
                mock_async_result.task_id = "mocked-task-id"
                mock_delay.return_value = mock_async_result

                import_response = self.client.post(
                    self.get_url(self.course_id),
                    {'file_url': file_url},
                    format='json'
                )

                self.assertEqual(import_response.status_code, status.HTTP_200_OK)
                self.assertIn('task_id', import_response.data, "Task ID should be returned")

    def get_url(self, course_id):
        """
        Helper function to create the url for the import API endpoint
        """
        url = reverse(
            'course_import:course_templates_import',  # Ensure this is correct in your URLs
            kwargs={'course_id': course_id}
        )
        return url
