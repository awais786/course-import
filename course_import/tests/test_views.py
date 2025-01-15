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
    Test suite for the plugin-based course import API.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test data and mock files for course import testing.
        """
        super().setUpClass()

        cls.course_id = "course-v1:edX+DemoX+Demo_Course"
        cls.password = "test_password"
        cls.staff_user = User.objects.create_user(
            username="staff", password=cls.password, is_staff=True
        )

        cls.content_dir = path(tempfile.mkdtemp())
        good_dir = tempfile.mkdtemp(dir=cls.content_dir)
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

    def get_url(self, course_id):
        """
        Construct the URL for the course import API endpoint.
        """
        return reverse(
            'course_import:course_templates_import',
            kwargs={'course_id': course_id}
        )

    @patch('course_import.views.makedir')
    def test_import_course_by_url_success(self, mock_isdir):
        """
        Test that a staff user can import a course using a valid file URL.
        """
        mock_isdir.return_value = True
        self.client.login(username=self.staff_user.username, password=self.password)

        file_url = "https://example.com/test-course.tar.gz"
        with open(self.good_tar_fullpath, 'rb') as fp:
            file_content = fp.read()

        with patch('requests.get') as mock_get, \
            patch('cms.djangoapps.contentstore.tasks.import_olx.delay') as mock_delay:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = (
                file_content[i:i + 1024] for i in range(0, len(file_content), 1024)
            )
            mock_get.return_value = mock_response

            mock_task_result = MagicMock()
            mock_task_result.task_id = "mocked-task-id"
            mock_delay.return_value = mock_task_result

            response = self.client.post(
                self.get_url(self.course_id),
                {'file_url': file_url},
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('task_id', response.data)
            self.assertIn('filename', response.data)

    def test_import_course_by_url_missing_file_url(self):
        """
        Test that a 400 error is raised when file_url is missing.
        """
        self.client.login(username=self.staff_user.username, password=self.password)
        response = self.client.post(self.get_url(self.course_id), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), 'file_url missing.')

    @patch('course_import.views.makedir')
    def test_import_course_by_url_invalid_file_type(self, mock_isdir):
        """
        Test that a 400 error is raised for an invalid file type.
        """
        mock_isdir.return_value = True
        self.client.login(username=self.staff_user.username, password=self.password)

        file_url = "https://example.com/test-course.tar.exe"
        response = self.client.post(
            self.get_url(self.course_id),
            {'file_url': file_url},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), 'Invalid file type.')

    @patch('course_import.views.makedir')
    def test_import_course_by_url_file_download_failure(self, mock_isdir):
        """
        Test that a 400 error is raised when file download fails.
        """
        mock_isdir.return_value = True
        self.client.login(username=self.staff_user.username, password=self.password)

        file_url = "https://example.com/test-course.tar.gz"
        with open(self.good_tar_fullpath, 'rb') as fp:
            file_content = fp.read()

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.iter_content.return_value = (
                file_content[i:i + 1024] for i in range(0, len(file_content), 1024)
            )
            mock_get.return_value = mock_response

            response = self.client.post(
                self.get_url(self.course_id),
                {'file_url': file_url},
                format='json'
            )

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.content.decode('utf-8'), 'failed to download a file.')

    @patch('course_import.views.makedir')
    def test_import_course_by_url_final_except_block(self, mock_isdir):
        """
        Test that a 400 error is raised when an unexpected exception occurs.
        """
        mock_isdir.return_value = True
        self.client.login(username=self.staff_user.username, password=self.password)

        file_url = "https://example.com/test-course.tar.gz"
        with patch('requests.get') as mock_get:
            # Raise a generic exception to simulate an unexpected error
            mock_get.side_effect = Exception("Unexpected error occurred.")

            response = self.client.post(
                self.get_url(self.course_id),
                {'file_url': file_url},
                format='json'
            )

            self.assertEqual(response.status_code, 400)
            breakpoint()
            self.assertEqual(response.content.decode('utf-8'), 'Unexpected error occurred.')
