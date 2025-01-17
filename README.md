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
```
