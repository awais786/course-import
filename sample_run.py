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


# ***************** with Authorization **********

headers = {
    "Authorization": "Bearer 123",  # pass valid token here and valid source-config below.
    "Content-Type": "application/json",
}

resp = CourseTemplateRequested.run_filter(
    source_type='github', **{
        'source_config': "https://raw.githubusercontent.com/awais786/courses/refs/heads/main/edly_courses.json",
        'headers': headers
})

print('-----------------')
print(resp)
print('-----------------')
