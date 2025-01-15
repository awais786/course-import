"""
APIs related to Course Import.
"""

import base64
import logging
import os
from urllib.parse import urlparse

import requests
from cms.djangoapps.contentstore.storage import course_import_export_storage
from cms.djangoapps.contentstore.tasks import CourseImportTask, import_olx
from django.conf import settings
from django.core.files import File
from django.http import HttpResponseBadRequest, HttpResponse
from path import Path as path
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from user_tasks.models import UserTaskStatus

log = logging.getLogger(__name__)

IMPORTABLE_FILE_TYPES = ('.tar.gz', '.zip')


class CourseImportView(GenericAPIView):
    exclude_from_schema = True

    def post(self, request, course_id):

        try:
            course_key = course_id
            # Check for input source
            if 'file_url' not in request.data:
                return HttpResponseBadRequest("file_url missing.")

            course_dir = path(settings.GITHUB_REPO_ROOT) / base64.urlsafe_b64encode(
                repr(course_key).encode('utf-8')
            ).decode('utf-8')

            # moving this into method. They were causing issues in mocking in tests.
            makedir(course_dir)

            if 'file_url' in request.data:
                file_url = request.data['file_url']
                filename = os.path.basename(urlparse(file_url).path)

                if not filename.endswith(IMPORTABLE_FILE_TYPES):
                    return HttpResponseBadRequest("Invalid file type.")

                response = requests.get(file_url, stream=True)
                if response.status_code != 200:
                    return HttpResponseBadRequest("failed to download a file.")

                temp_filepath = course_dir / filename
                total_size = 0  # Track total size in bytes
                with open(temp_filepath, "wb") as temp_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            chunk_size = len(chunk)
                            total_size += chunk_size
                            temp_file.write(chunk)
                log.info(f"Course import {course_key}: File downloaded from URL, file: {filename}")

            log.info("Course import %s: Upload complete", course_key)

            with open(temp_filepath, 'rb') as local_file:
                django_file = File(local_file)
                storage_path = course_import_export_storage.save('olx_import/' + filename, django_file)

            async_result = import_olx.delay(
                request.user.id, str(course_key), storage_path, filename, request.LANGUAGE_CODE)

            resp = Response({
                'task_id': async_result.task_id,
                'filename': filename
            })

            return resp
        except Exception as err:
            return HttpResponse(str(err), status=400)

    def get(self, request, course_id):
        """
        Check the status of the specified task
        """
        course_key = course_id
        try:
            task_id = request.GET['task_id']
            filename = request.GET['filename']
            args = {'course_key_string': str(course_key), 'archive_name': filename}
            name = CourseImportTask.generate_name(args)
            task_status = UserTaskStatus.objects.filter(name=name, task_id=task_id).first()
            return Response({
                'state': task_status.state
            })
        except Exception as err:
            return HttpResponse(str(err), status=400)


def makedir(course_dir):
    """
    Create the specified directory if it does not already exist.
    Args:
        course_dir (path.Path or str): The path of the directory to create.
    """

    if not course_dir.isdir():
        os.makedirs(course_dir)

