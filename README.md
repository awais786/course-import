# CourseTemplates Plugin

A Python pipeline to fetch and filter templates from GitHub. This project provides a reusable class, `GithubTemplatesPipeline`, that validates source configurations, fetches data from GitHub repositories, and filters active templates for use in other applications.

---

## Features

- Filters Integration: Uses openedx-filters to add custom filtering capabilities.
- Pipelinestep Integration: To fetch data from github urls.
- Filter templates based on metadata (e.g., only include "active" templates).
- Flexible architecture to support other sources like S3 in the future.
- Comprehensive error handling and input validation.

---

## Usage
```python
from course_import.filters import CourseTemplateRequested

resp = CourseTemplateRequested.run_filter(
    source_type='github', **{
        'source_config': "https://raw.githubusercontent.com/awais786/courses/refs/heads/main/edly_courses.json"
})
```
