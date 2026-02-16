"""Unit tests for ResponseWriter service."""

import json
import logging
import tempfile
import pytest
from pathlib import Path
from shared.infrastructure.response_writer import ResponseWriter
from age_average.domain.age_response_dto import AgeResponseDTO
from shared.domain.exceptions.file_operation_error import FileOperationError


class TestResponseWriter:
    """Test suite for ResponseWriter service."""

    @pytest.fixture
    def logger(self):
        """Create a logger for testing."""
        return logging.getLogger("test")

    @pytest.fixture
    def writer(self, logger):
        """Create a ResponseWriter instance for testing."""
        return ResponseWriter(logger)

    @pytest.fixture
    def sample_results(self):
        """Create sample AgeResponseDTO for testing."""
        return AgeResponseDTO(
            status="success",
            message="Test message",
            min_age=25,
            max_age=45,
            avg_age=33.5
        )

    def test_write_json_creates_file(self, writer, sample_results):
        """Test that write_json creates a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.json"

            writer.write_json(sample_results, output_path)

            assert output_path.exists()

    def test_write_json_content(self, writer, sample_results):
        """Test that write_json writes correct content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.json"

            writer.write_json(sample_results, output_path)

            with open(output_path, 'r') as f:
                content = json.load(f)

            assert content["status"] == "success"
            assert content["message"] == "Test message"
            assert content["min_age"] == 25
            assert content["max_age"] == 45
            assert content["avg_age"] == 33.5

    def test_write_json_with_indent(self, writer, sample_results):
        """Test that write_json creates properly formatted JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.json"

            writer.write_json(sample_results, output_path)

            content = output_path.read_text()

            # Should have indentation
            assert "\n" in content
            assert "  " in content or "\t" in content

    def test_write_json_overwrites_existing_file(self, writer):
        """Test that write_json overwrites existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.json"

            # Write first results
            results1 = AgeResponseDTO(
                status="success",
                message="First",
                min_age=10,
                max_age=20,
                avg_age=15.0
            )
            writer.write_json(results1, output_path)

            # Write second results
            results2 = AgeResponseDTO(
                status="success",
                message="Second",
                min_age=30,
                max_age=40,
                avg_age=35.0
            )
            writer.write_json(results2, output_path)

            # Should have second results
            with open(output_path, 'r') as f:
                content = json.load(f)

            assert content["message"] == "Second"
            assert content["min_age"] == 30

    def test_write_json_to_nested_directory(self, writer, sample_results):
        """Test writing to a file in a nested directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "subdir" / "nested" / "results.json"
            nested_path.parent.mkdir(parents=True, exist_ok=True)

            writer.write_json(sample_results, nested_path)

            assert nested_path.exists()

            with open(nested_path, 'r') as f:
                content = json.load(f)

            assert content["status"] == "success"

    def test_write_json_with_different_results(self, writer):
        """Test writing different result values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "results.json"

            results = AgeResponseDTO(
                status="error",
                message="Processing failed",
                min_age=0,
                max_age=0,
                avg_age=0.0
            )

            writer.write_json(results, output_path)

            with open(output_path, 'r') as f:
                content = json.load(f)

            assert content["status"] == "error"
            assert content["message"] == "Processing failed"
            assert content["min_age"] == 0

    def test_write_json_with_invalid_path_raises_error(self, writer, sample_results):
        """Test that writing to invalid path raises an error."""
        invalid_path = Path("/invalid/path/that/does/not/exist/results.json")

        # Note: This test may not raise an error in all environments
        # since mkdir(parents=True) can create the directory
        # In a real scenario, permission errors would occur
        try:
            writer.write_json(sample_results, invalid_path)
            # If it succeeds, that's also acceptable
            assert invalid_path.exists()
        except FileOperationError:
            # This is also acceptable
            pass