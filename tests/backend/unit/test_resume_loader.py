"""
Test Suite: Resume Loader - JSON Import Tests

Regression tests for JSON resume import, specifically verifying that
achievements/bullet points in experience entries are fully preserved
during the load pipeline.

Bug context: SchemaEngine.extract_list_fields() converts the achievements
array to a Python string representation because the EXPERIENCE schema
defines achievements as type: str. The subsequent isinstance() check
then fails, causing all bullet points to be silently dropped.
"""
import json
import os
import pytest
import tempfile

from backend.core.infrastructure.adapters.resume_loader import ResumeLoader
from backend.core.utils.constants import UIConstants


@pytest.fixture
def sample_resume_with_achievements():
    """Resume JSON with multiple experience entries and achievements."""
    return {
        "personal_info": {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "555-0100",
            "location": "Houston, TX",
            "summary": "A test resume for validating achievements parsing."
        },
        "education": [],
        "experience": [
            {
                "company": "Acme Corp",
                "position": "Senior Engineer",
                "location": "Houston, TX",
                "start_date": "2020",
                "end_date": "2024",
                "description": "Led engineering projects.",
                "achievements": [
                    "Designed and deployed a distributed pipeline processing system.",
                    "Reduced production downtime by 40% through predictive maintenance.",
                    "Mentored a team of 5 junior engineers."
                ]
            },
            {
                "company": "Beta Inc",
                "position": "Engineer",
                "location": "Dallas, TX",
                "start_date": "2017",
                "end_date": "2020",
                "description": "Worked on process optimization.",
                "achievements": [
                    "Implemented a real-time monitoring dashboard.",
                    "Optimized reactor throughput by 25%."
                ]
            }
        ],
        "skills": [],
        "projects": [],
        "certifications": [],
        "others": {}
    }


@pytest.fixture
def resume_json_file(sample_resume_with_achievements):
    """Write sample resume to a temp JSON file and return the path."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_resume_with_achievements, f)
        path = f.name
    yield path
    os.unlink(path)


class TestAchievementsParsing:
    """Regression tests for achievements parsing during JSON import."""

    def test_achievements_are_preserved_in_form_output(self, resume_json_file):
        """All achievement bullet points must survive the JSON -> form conversion."""
        form_values = ResumeLoader.load_from_json(resume_json_file)
        experience_table = form_values[UIConstants.WORK_TABLE_INDEX]

        assert len(experience_table) == 2, "Expected 2 experience entries"

        # First entry: 3 achievements
        achievements_text = experience_table[0][6]
        bullets = [line for line in achievements_text.split('\n') if line.strip()]
        assert len(bullets) == 3, f"Expected 3 bullets for Acme Corp, got {len(bullets)}"

        # Second entry: 2 achievements
        achievements_text = experience_table[1][6]
        bullets = [line for line in achievements_text.split('\n') if line.strip()]
        assert len(bullets) == 2, f"Expected 2 bullets for Beta Inc, got {len(bullets)}"

    def test_achievement_content_is_not_truncated(self, resume_json_file):
        """Achievement text content must not be truncated or mangled."""
        form_values = ResumeLoader.load_from_json(resume_json_file)
        experience_table = form_values[UIConstants.WORK_TABLE_INDEX]

        achievements_text = experience_table[0][6]
        assert "distributed pipeline processing system" in achievements_text
        assert "predictive maintenance" in achievements_text
        assert "junior engineers" in achievements_text

    def test_achievements_formatted_as_bullet_list(self, resume_json_file):
        """Achievements should be formatted as '- item' bullet lines."""
        form_values = ResumeLoader.load_from_json(resume_json_file)
        experience_table = form_values[UIConstants.WORK_TABLE_INDEX]

        achievements_text = experience_table[0][6]
        lines = [line for line in achievements_text.split('\n') if line.strip()]
        for line in lines:
            assert line.startswith('- '), f"Bullet line should start with '- ', got: {line[:40]}"

    def test_empty_achievements_handled(self):
        """Experience with no achievements should produce empty string."""
        data = {
            "personal_info": {"full_name": "Test", "email": "t@t.com"},
            "education": [],
            "experience": [
                {
                    "company": "NoAch Corp",
                    "position": "Role",
                    "location": "",
                    "start_date": "2020",
                    "end_date": "2024",
                    "description": "Did things.",
                    "achievements": []
                }
            ],
            "skills": [], "projects": [], "certifications": [], "others": {}
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            path = f.name
        try:
            form_values = ResumeLoader.load_from_json(path)
            experience_table = form_values[UIConstants.WORK_TABLE_INDEX]
            assert experience_table[0][6] == ''
        finally:
            os.unlink(path)

    def test_achievements_missing_key_handled(self):
        """Experience without achievements key should not crash."""
        data = {
            "personal_info": {"full_name": "Test", "email": "t@t.com"},
            "education": [],
            "experience": [
                {
                    "company": "NoKey Corp",
                    "position": "Role",
                    "location": "",
                    "start_date": "2020",
                    "end_date": "2024",
                    "description": "Did things."
                }
            ],
            "skills": [], "projects": [], "certifications": [], "others": {}
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f)
            path = f.name
        try:
            form_values = ResumeLoader.load_from_json(path)
            experience_table = form_values[UIConstants.WORK_TABLE_INDEX]
            assert experience_table[0][6] == ''
        finally:
            os.unlink(path)
