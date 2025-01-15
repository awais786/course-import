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

    This test class covers scenarios where staff users can import courses via the API
    and check the status of course import tasks. Mocking is used to isolate external
    dependencies like file downloads and task handling.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test data and mock files for course import testing.
        """
        super().setUpClass()

        # Test data
        cls.course_id = "course-v1:edX+DemoX+Demo_Course"
        cls.password = "test_password"
        cls.staff_user = User.objects.create_user(
            username="staff", password=cls.password, is_staff=True
        )

        cls.content_dir = path(tempfile.mkdtemp())

        # Create a valid tarball for testing course import
        good_dir = tempfile.mkdtemp(dir=cls.content_dir)
        embedded_dir = os.path.join(good_dir, "grandparent", "parent")
        os.makedirs(os.path.join(embedded_dir, "course"))

        # Create course XML files
        with open(os.path.join(embedded_dir, "course.xml"), "w+") as f:
            f.write('<course url_name="2013_Spring" org="EDx" course="0.00x"/>')

        with open(os.path.join(embedded_dir, "course", "2013_Spring.xml"), "w+") as f:
            f.write('<course></course>')

        # Compress the test directory into a tarball
        cls.good_tar_filename = "good.tar.gz"
        cls.good_tar_fullpath = os.path.join(cls.content_dir, cls.good_tar_filename)
        with tarfile.open(cls.good_tar_fullpath, "w:gz") as gtar:
            gtar.add(good_dir)

    @patch('course_import.views.makedir')
    def test_staff_with_access_import_course_by_url_succeeds(self, mock_isdir):
        """
        Test that a staff user can successfully import a course using a file URL.

        This test mocks external requests to download the file and the asynchronous
        task for course import.
        """
        mock_isdir.return_value = True
        # Log in as staff user
        self.client.login(username=self.staff_user.username, password=self.password)

        # Mocked file URL and content
        file_url = "https://example.com/test-course.tar.gz"
        with open(self.good_tar_fullpath, 'rb') as fp:
            file_content = fp.read()

        with patch('requests.get') as mock_get:
            # Mock the external file download
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = (file_content[i:i + 1024] for i in
                                                       range(0, len(file_content), 1024))
            mock_get.return_value = mock_response

            with patch('cms.djangoapps.contentstore.tasks.import_olx.delay') as mock_delay:
                # Mock the asynchronous import task
                mock_async_result = MagicMock()
                mock_async_result.task_id = "mocked-task-id"
                mock_delay.return_value = mock_async_result

                # Make the API request to import the course
                import_response = self.client.post(
                    self.get_url(self.course_id),
                    {'file_url': file_url},
                    format='json'
                )

                # Assert the response for course import
                self.assertEqual(import_response.status_code, status.HTTP_200_OK)
                self.assertIn('task_id', import_response.data, "Task ID should be returned")
                self.assertIn('filename', import_response.data, "Filename should be returned")

            with patch('course_import.views.CourseImportTask.generate_name') as mock_generate_name, \
                patch('user_tasks.models.UserTaskStatus.objects.filter') as mock_filter:
                # Mock task name generation
                mock_generate_name.return_value = "mocked_task_name"

                # Mock task status retrieval
                mock_task_status = MagicMock()
                mock_task_status.state = UserTaskStatus.SUCCEEDED
                mock_filter.return_value.first.return_value = mock_task_status

                # Simulate a request to check the task status
                status_response = self.client.get(
                    self.get_url(self.course_id),
                    {'task_id': "mocked-task-id", 'filename': "mocked-filename"}
                )

                # Assert the response for task status
                self.assertEqual(status_response.status_code, status.HTTP_200_OK)
                self.assertEqual(status_response.data['state'], UserTaskStatus.SUCCEEDED, "Task should be successful")

    def get_url(self, course_id):
        """
        Helper function to construct the URL for the course import API endpoint.

        Args:
            course_id (str): The ID of the course being imported.

        Returns:
            str: The constructed URL for the API endpoint.
        """
        return reverse(
            'course_import:course_templates_import',
            kwargs={'course_id': course_id}
        )

    def test_import_course_by_url_without_file(self):
        """
        This test without file_url it raises an error.
        """
        # Log in as staff user
        self.client.login(username=self.staff_user.username, password=self.password)
        import_response = self.client.post(self.get_url(self.course_id),format='json')
        self.assertEqual(import_response.status_code, 400)
        self.assertEqual(import_response.content.decode('utf-8'), 'file_url missing.')

    @patch('course_import.views.makedir')
    def test_import_course_by_url_invalid_file(self, mock_isdir):
        """
        This test without file_url it raises an error.
        """
        # Log in as staff user
        mock_isdir.return_value = True
        self.client.login(username=self.staff_user.username, password=self.password)
        # Mocked file URL and content
        file_url = "https://example.com/test-course.tar.exe"

        import_response = self.client.post(
            self.get_url(self.course_id),
            {'file_url': file_url},
            format='json'
        )
        self.assertEqual(import_response.status_code, 400)
        self.assertEqual(import_response.content.decode('utf-8'), 'Invalid file type.')
