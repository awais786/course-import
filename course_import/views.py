"""
APIs related to Course Import.
"""

import base64
import logging
import os
from urllib.parse import urlparse

import requests
from cms.djangoapps.contentstore.storage import course_import_export_storage  # pylint: disable=import-error
from cms.djangoapps.contentstore.tasks import CourseImportTask, import_olx  # pylint: disable=import-error
from django.conf import settings
from django.core.files import File
from django.http import HttpResponse, HttpResponseBadRequest
from path import Path as path
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated  # lint-amnesty, pylint: disable=wrong-import-order
from rest_framework.response import Response
from user_tasks.models import UserTaskStatus

log = logging.getLogger(__name__)

IMPORTABLE_FILE_TYPES = ('.tar.gz', '.zip')


class CourseImportView(GenericAPIView):
    """
    API View for managing course import operations.

    This view provides endpoints to:
    - Import a course by downloading a file from a specified URL.
    - Retrieve the status of the import task.

    Attributes:
        permission_classes (tuple): Permissions required to access this API.
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    def post(self, request, course_id):
        """
        Handles the POST request for importing a course.

        Downloads a file from the provided URL, stores it, and triggers the course import task.

        Args:
            request (Request): The HTTP request object.
            course_id (str): The ID of the course to import.

        Returns:
            Response: Contains the task ID and filename if successful.
            HttpResponseBadRequest: If required parameters are missing or invalid.
            HttpResponse: In case of any exceptions, an error message is returned.
        """
        course_key = course_id
        # Check for input source
        if 'file_url' not in request.data:
            return HttpResponseBadRequest("file_url missing.")

        course_dir = path(settings.GITHUB_REPO_ROOT) / base64.urlsafe_b64encode(
            repr(course_key).encode('utf-8')
        ).decode('utf-8')

        file_url = request.data['file_url']
        filename = os.path.basename(urlparse(file_url).path)

        if not filename.endswith(IMPORTABLE_FILE_TYPES):
            return HttpResponseBadRequest("Invalid file type.")

        # moving this into method. They were causing issues in mocking in tests.
        makedir(course_dir)

        try:
            storage_path = download_file(course_key, file_url, filename, course_dir)
            async_result = import_olx.delay(
                request.user.id, str(course_key), storage_path, filename, request.LANGUAGE_CODE)

            resp = Response({
                'task_id': async_result.task_id,
                'filename': filename
            })

            return resp
        except Exception as err:  # pylint: disable=broad-except
            return HttpResponse(str(err), status=400)

    def get(self, request, course_id):
        """
        Handles the GET request to check the status of a course import task.

        Args:
            request (Request): The HTTP request object.
            course_id (str): The ID of the course.

        Returns:
            Response: Contains the state of the task if found.
            HttpResponse: If required parameters are missing or task is not found.
        """
        course_key = course_id
        task_id = request.GET.get('task_id')
        filename = request.GET.get('filename')

        if not task_id or not filename:
            return HttpResponse('Missing required parameters.', status=400)

        try:
            args = {'course_key_string': str(course_key), 'archive_name': filename}
            name = CourseImportTask.generate_name(args)
            task_status = UserTaskStatus.objects.filter(name=name, task_id=task_id).first()
            if not task_status:
                return HttpResponse('Task not found.', status=400)

            return Response({
                'state': task_status.state
            })
        except Exception as err:  # pylint: disable=broad-except
            return HttpResponse(str(err), status=400)


def download_file(course_key, file_url, filename, course_dir):
    """
    Downloads a file from a given URL and saves it to the specified directory.

    Args:
        course_key (str): The key of the course being imported.
        file_url (str): The URL of the file to download.
        filename (str): The name of the file.
        course_dir (path.Path): The directory to save the file.

    Returns:
        str: The storage path where the file is saved.

    Raises:
        HttpResponseBadRequest: If the download fails or is invalid.
    """
    response = requests.get(file_url, stream=True)  # pylint: disable=missing-timeout

    if response.status_code != 200:
        return HttpResponseBadRequest("Failed to download a file.")

    temp_filepath = course_dir / filename
    total_size = 0  # Track total size in bytes

    with open(temp_filepath, "wb") as temp_file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                chunk_size = len(chunk)
                total_size += chunk_size
                temp_file.write(chunk)

    log.info(f"Course import {course_key}: File downloaded from URL, file: {filename}")

    with open(temp_filepath, 'rb') as local_file:
        django_file = File(local_file)
        storage_path = course_import_export_storage.save('olx_import/' + filename, django_file)

    return storage_path


def makedir(course_dir):
    """
    Creates a directory if it does not already exist.

    Args:
        course_dir (path.Path or str): The path of the directory to create.
    """

    if not course_dir.isdir():
        os.makedirs(course_dir)
