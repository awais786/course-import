"""
Test cases for import course api.
"""
import sys
from unittest.mock import Mock

# Mock the entire 'cms' module
cms_mock = Mock()

# Assign mocked submodules to the 'cms' module
cms_mock.djangoapps.contentstore.storage.course_import_export_storage = Mock()
cms_mock.djangoapps.contentstore.tasks.CourseImportTask = Mock()
cms_mock.djangoapps.contentstore.tasks.import_olx = Mock()
cms_mock.djangoapps.contentstore.views = Mock()

# Add the 'cms' mock to sys.modules
sys.modules['cms'] = cms_mock
sys.modules['cms.djangoapps'] = cms_mock.djangoapps
sys.modules['cms.djangoapps.contentstore'] = cms_mock.djangoapps.contentstore
sys.modules['cms.djangoapps.contentstore.storage'] = cms_mock.djangoapps.contentstore.storage
sys.modules['cms.djangoapps.contentstore.tasks'] = cms_mock.djangoapps.contentstore.tasks
sys.modules['cms.djangoapps.contentstore.views'] = cms_mock.djangoapps.contentstore.views
