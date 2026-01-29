"""
Test Suite: Template Rendering Tests

Tests for the resume template rendering, specifically the contact line separator logic.
These tests verify:
- Contact line separators render correctly with various field combinations
- Empty fields don't cause extra separators
- All fields display with proper formatting
"""
import pytest
from jinja2 import Environment, FileSystemLoader
import os


@pytest.fixture(scope="module")
def template_env():
    """Create Jinja2 environment with the templates directory."""
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
        "backend", "core", "infrastructure", "generators", "templates"
    )
    return Environment(loader=FileSystemLoader(template_dir))


@pytest.fixture(scope="module")
def resume_template(template_env):
    """Load the classic resume template."""
    return template_env.get_template("classic_template.html")


class TestContactLineSeparators:
    """Test contact line separator logic in resume template."""

    def test_all_fields_present(self, resume_template):
        """Test separator when all contact fields are present."""
        html = resume_template.render(
            name_prefix="Dr.",
            full_name="Sarah Chen",
            current_address="456 Industrial Parkway",
            location="Houston, TX",
            citizenship="US Citizen",
            phone="555-123-6789",
            email="dr.chen@email.com",
            linkedin_url="linkedin.com/in/sarahchen",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Normalize whitespace for testing (template has newlines/indentation)
        import re
        normalized = re.sub(r'\s+', ' ', html)

        # All separators should be present
        assert "456 Industrial Parkway" in html
        assert "Houston, TX" in html
        assert "| US Citizen" in normalized
        assert "| 555-123-6789" in normalized
        assert "| dr.chen@email.com" in normalized

    def test_no_address_no_location_has_citizenship_phone(self, resume_template):
        """Test separator between citizenship and phone when no address/location."""
        html = resume_template.render(
            name_prefix="",
            full_name="Sarah Chen",
            current_address="",
            location="",
            citizenship="US Citizen",
            phone="555-123-6789",
            email="dr.chen@email.com",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Should have separator between citizenship and phone
        assert "US Citizen" in html
        assert "| 555-123-6789" in html
        # Should NOT have separator before citizenship (nothing before it)
        assert html.count("| US Citizen") == 0

    def test_only_citizenship_and_email(self, resume_template):
        """Test with only citizenship and email."""
        html = resume_template.render(
            name_prefix="",
            full_name="John Doe",
            current_address="",
            location="",
            citizenship="US Citizen",
            phone="",
            email="john@example.com",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Email should have separator (citizenship exists before it)
        assert "US Citizen" in html
        assert "| john@example.com" in html

    def test_only_phone_and_email(self, resume_template):
        """Test with only phone and email (no address, location, citizenship)."""
        html = resume_template.render(
            name_prefix="",
            full_name="John Doe",
            current_address="",
            location="",
            citizenship="",
            phone="555-1234",
            email="john@example.com",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Phone should NOT have separator (nothing before it)
        # Email should have separator (phone before it)
        assert "555-1234" in html
        assert "| john@example.com" in html

    def test_location_and_phone_no_address_no_citizenship(self, resume_template):
        """Test with location and phone but no address or citizenship."""
        html = resume_template.render(
            name_prefix="",
            full_name="Jane Smith",
            current_address="",
            location="New York, NY",
            citizenship="",
            phone="555-9999",
            email="",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Location should not have comma before (no address)
        assert "New York, NY" in html
        # Phone should have separator (location exists)
        assert "| 555-9999" in html

    def test_address_and_location_comma_separator(self, resume_template):
        """Test comma separator between address and location."""
        html = resume_template.render(
            name_prefix="",
            full_name="Jane Smith",
            current_address="123 Main St",
            location="Boston, MA",
            citizenship="",
            phone="",
            email="",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Should have comma between address and location
        assert "123 Main St" in html
        assert ", Boston, MA" in html

    def test_only_email(self, resume_template):
        """Test with only email (no other contact fields)."""
        html = resume_template.render(
            name_prefix="",
            full_name="Test User",
            current_address="",
            location="",
            citizenship="",
            phone="",
            email="test@example.com",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Email should NOT have separator (nothing before it)
        assert "test@example.com" in html
        # Make sure there's no stray separator before email
        assert "| test@example.com" not in html

    def test_linkedin_github_portfolio_separators(self, resume_template):
        """Test separators in the second contact line (URLs)."""
        html = resume_template.render(
            name_prefix="",
            full_name="Dev User",
            current_address="",
            location="",
            citizenship="",
            phone="",
            email="",
            linkedin_url="linkedin.com/in/devuser",
            github_url="github.com/devuser",
            portfolio_url="devuser.com",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        assert "linkedin.com/in/devuser" in html
        assert "| github.com/devuser" in html
        assert "| devuser.com" in html

    def test_only_github_url(self, resume_template):
        """Test with only GitHub URL (no LinkedIn)."""
        html = resume_template.render(
            name_prefix="",
            full_name="Dev User",
            current_address="",
            location="",
            citizenship="",
            phone="",
            email="",
            linkedin_url="",
            github_url="github.com/devuser",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # GitHub should NOT have separator (no LinkedIn before it)
        assert "github.com/devuser" in html
        assert "| github.com/devuser" not in html

    def test_name_prefix_rendering(self, resume_template):
        """Test name prefix renders correctly."""
        html = resume_template.render(
            name_prefix="Dr.",
            full_name="Sarah Chen",
            current_address="",
            location="",
            citizenship="",
            phone="",
            email="",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        assert "Dr. Sarah Chen" in html

    def test_no_name_prefix(self, resume_template):
        """Test rendering without name prefix."""
        html = resume_template.render(
            name_prefix="",
            full_name="John Doe",
            current_address="",
            location="",
            citizenship="",
            phone="",
            email="",
            linkedin_url="",
            github_url="",
            portfolio_url="",
            summary="",
            education=[],
            experience=[],
            skills={},
            projects=[],
            certifications=[],
            others={}
        )
        # Should just have the name without extra space
        assert ">John Doe<" in html or "John Doe</h1>" in html
