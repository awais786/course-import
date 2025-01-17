# CourseTemplates Plugin

A Python pipeline to fetch and filter templates from GitHub. This project provides a reusable class, `GithubTemplatesPipeline`, that validates source configurations, fetches data from GitHub repositories, and filters active templates for use in other applications.

---

### Features

- **Openedx-Filters Integration**  
  Leverages the openedx-filters package to enable custom filtering capabilities for template selection.

- **Pipeline Step Integration**  
  Fetches data efficiently from GitHub URLs with robust mechanisms to handle variations in repository structures.

- **Metadata-Based Filtering**  
  Filters templates based on metadata attributes, such as filtering only "active" templates or those matching specific criteria.

- **Extensible Design**  
  Supports adding other data sources (e.g., S3) in the future, providing a flexible architecture for scaling the pipeline.

- **Import Course API**
    It enables asynchronous import of course files from a provided URL, allowing for background processing without blocking other operations.

- **Error Handling**  
  Implements comprehensive validation and error management for source configurations, data integrity, and API calls to ensure reliability.

- **Reusable Components**  
  Modular structure allows the class to be reused or extended in multiple Open edX applications or beyond.

---

## Usage
```python

# define pipeline setting

OPEN_EDX_FILTERS_CONFIG = {
    "org.edly.templates.fetch.requested.v1": {
        "pipeline": [
            "course_import.pipeline.GithubTemplatesPipeline",
        ],
        "fail_silently": False,
    },
}


from course_import.filters import CourseTemplateRequested

resp = CourseTemplateRequested.run_filter(
    source_type='github', **{
        'source_config': "https://raw.githubusercontent.com/awais786/courses/refs/heads/main/edly_courses.json"
})

response will be list of contains all courses.
[
    {
      "source_type": "github",
      "source_config": "https://raw.githubusercontent.com/awais786/courses/refs/heads/main/edly_courses.json",
      "result": [
        {
          "courses_name": "AI Courses",
          "zip_url": "https://raw.githubusercontent.com/awais786/courses/main/edly/AI%20Courses/course.2jyd4n_5.tar.gz",
          "metadata": {
            "title": "Introduction to Open edX",
            "description": "Learn the fundamentals of the Open edX platform, including how to create and manage courses.",
            "thumbnail": "https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp",
            "active": true
          }
        }
    }
]
```

## Rendering Frontend Using JSON

You can use the provided JSON response to dynamically render your frontend. The data includes essential fields like `courses_name`, `zip_url`, and metadata attributes (`title`, `description`, `thumbnail`, and `active`). These can be used to display course information in a structured and user-friendly way.

## Course Templates

The following section showcases how thumbnails can be rendered using the `thumbnail` URLs provided in the JSON response.

1. **AI Courses**
   - **Title**: Introduction to Open edX  
   - **Description**: Learn the fundamentals of the Open edX platform, including how to create and manage courses.  
<img src="https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp" alt="AI Courses Thumbnail" width="300"/>

To import a course, use the link below: [Import AI Courses](https://raw.githubusercontent.com/awais786/courses/main/edly/AI%20Courses/course.2jyd4n_5.tar.gz)


### Example Python Code to Import a Course via POST Request inside edx-platform

This example demonstrates how to use Python and the `requests` library to send a POST request to the course import API.

```python
import requests

# The API URL for importing the course

course_id = "your_course_id_here"
api_url = f"/course_import_api/import/{course_id}/"

# The file URL to be imported coming from above json response
file_url = "https://raw.githubusercontent.com/awais786/courses/main/edly/AI%20Courses/course.2jyd4n_5.tar.gz"

# CSRF token (usually retrieved from a session or cookie)
csrf_token = 'your_csrf_token_here'

headers = {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrf_token
}

data = {
    'file_url': file_url
}

# Send the POST request
response = requests.post(api_url, json=data, headers=headers)

if response.status_code == 200:
    print('Import started successfully:', response.json())

Out looks like
{"task_id":"e264cb4e-ea1f-4884-ab01-a374eb1ddc4c", "filename": "course.2jyd4n_5.tar.gz" }


Get the upload file status

response = requests.get(api_url, json={'task_id': 'e264cb4e-ea1f-4884-ab01-a374eb1ddc4c'}, headers=headers)

{"state":"Succeeded"}

```

### Test using curl command

```
curl --location 'http://localhost:18010/api/courses/v0/import/course-v1:edX+DemoX+Demo_Course/' \
--header 'Authorization: JWT token' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'X-CSRFToken: awtUGVlYyMwLWaaS' \
--data-raw '{
    "file_url": "https://raw.githubusercontent.com/awais786/courses/main/edly/AI%20Courses/course.v2_c3p0f.tar.gz"
}'

output 
{"task_id":"e264cb4e-ea1f-4884-ab01-a374eb1ddc4c", "filename": "course.2jyd4n_5.tar.gz" }
````
