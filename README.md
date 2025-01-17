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

## Course Thumbnails

The following section showcases how thumbnails can be rendered using the `thumbnail` URLs provided in the JSON response.

### Example Thumbnails

1. **AI Courses**
   - **Title**: Introduction to Open edX  
   - **Description**: Learn the fundamentals of the Open edX platform, including how to create and manage courses.  
### AI Courses Thumbnail
<img src="https://discover.ilmx.org/wp-content/uploads/2024/01/Course-image-2.webp" alt="AI Courses Thumbnail" width="300"/>


