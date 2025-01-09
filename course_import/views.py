# """
# APIs related to Course Import.
# """
#
#
# import base64
# import logging
# import os
# from urllib.parse import urlparse
#
# import requests
# # from cms.djangoapps.contentstore.storage import course_import_export_storage
# # from cms.djangoapps.contentstore.tasks import CourseImportTask, import_olx
# # from cms.djangoapps.contentstore.utils import IMPORTABLE_FILE_TYPES
# from django.conf import settings
# from django.core.files import File
# # from openedx.core.lib.api.view_utils import DeveloperErrorViewMixin, view_auth_classes
# from path import Path as path
# from rest_framework import status
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.generics import GenericAPIView
# from rest_framework.response import Response
# from user_tasks.models import UserTaskStatus
#
# # from cms.djangoapps.contentstore.api.views.utils import course_author_access_required
#
# log = logging.getLogger(__name__)
#
#
# # @view_auth_classes()
# # class CourseImportExportViewMixin(DeveloperErrorViewMixin):
# #     """
# #     Mixin class for course import/export related views.
# #     """
# #     def perform_authentication(self, request):
# #         """
# #         Ensures that the user is authenticated (e.g. not an AnonymousUser)
# #         """
# #         super().perform_authentication(request)
# #         if request.user.is_anonymous:
# #             raise AuthenticationFailed
#
#
# class CourseImportView():
#     exclude_from_schema = True
#
#     @course_author_access_required
#     def post(self, request, course_key):
#
#         try:
#             # Check for input source
#             if 'file_url' not in request.data:
#                 raise self.api_error(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     developer_message='Missing required parameter',
#                     error_code='internal_error',
#                 )
#
#             course_dir = path(settings.GITHUB_REPO_ROOT) / base64.urlsafe_b64encode(
#                 repr(course_key).encode('utf-8')
#             ).decode('utf-8')
#
#             if not course_dir.isdir():
#                 os.makedirs(course_dir)
#
#             if 'file_url' in request.data:
#                 file_url = request.data['file_url']
#                 filename = os.path.basename(urlparse(file_url).path)
#                 if not filename.endswith(IMPORTABLE_FILE_TYPES):
#                     raise self.api_error(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         developer_message=f'File type not supported: {filename}',
#                         error_code='invalid_file_type',
#                     )
#                 response = requests.get(file_url, stream=True)
#                 if response.status_code != 200:
#                     raise self.api_error(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         developer_message='Failed to download file from URL',
#                         error_code='download_error',
#                     )
#                 temp_filepath = course_dir / filename
#                 total_size = 0  # Track total size in bytes
#                 with open(temp_filepath, "wb") as temp_file:
#                     for chunk in response.iter_content(chunk_size=1024):
#                         if chunk:
#                             chunk_size = len(chunk)
#                             total_size += chunk_size
#                             temp_file.write(chunk)
#                 log.info(f"Course import {course_key}: File downloaded from URL, file: {filename}")
#
#             log.info("Course import %s: Upload complete", course_key)
#             with open(temp_filepath, 'rb') as local_file:
#                 django_file = File(local_file)
#                 storage_path = course_import_export_storage.save('olx_import/' + filename, django_file)
#
#             async_result = import_olx.delay(
#                 request.user.id, str(course_key), storage_path, filename, request.LANGUAGE_CODE)
#             return Response({
#                 'task_id': async_result.task_id
#             })
#         except Exception as e:
#             log.exception(f'Course import {course_key}: Unknown error in import')
#             raise self.api_error(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 developer_message=str(e),
#                 error_code='internal_error'
#             )
#
#     @course_author_access_required
#     def get(self, request, course_key):
#         """
#         Check the status of the specified task
#         """
#         try:
#             task_id = request.GET['task_id']
#             filename = request.GET['filename']
#             args = {'course_key_string': str(course_key), 'archive_name': filename}
#             name = CourseImportTask.generate_name(args)
#             task_status = UserTaskStatus.objects.filter(name=name, task_id=task_id).first()
#             return Response({
#                 'state': task_status.state
#             })
#         except Exception as e:
#             log.exception(str(e))
#             raise self.api_error(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 developer_message=str(e),
#                 error_code='internal_error'
#             )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class CourseTemplatesImportView(APIView):
    permission_classes = [IsAuthenticated]  # You can adjust permissions as needed

    def post(self, request, *args, **kwargs):
        """
        Endpoint to import a course from a URL.
        This endpoint expects a `file_url` in the request data.
        """
        file_url = request.data.get("file_url", None)

        if not file_url:
            return Response(
                {"error": "file_url parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Assume that 'import_course_from_url' is a function you have to import the course
        try:
            # Replace the following line with your actual import logic
            self.import_course_from_url(file_url)

            return Response(
                {"message": f"Course import started successfully from {file_url}"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
