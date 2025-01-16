import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_utils.test_settings')  # Replace with your actual settings module

from course_import.filters import CourseTemplateRequested

resp = CourseTemplateRequested.run_filter(
    source_type='github', **{
        'source_config': "https://raw.githubusercontent.com/awais786/courses/refs/heads/main/edly_courses.json"
    })

print('-----------------')
print(resp)
print('-----------------')
