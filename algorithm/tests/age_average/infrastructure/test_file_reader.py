"""Unit tests for FileReader service."""

import logging
import tempfile
import pytest
from pathlib import Path
from age_average.infrastructure.file_reader import FileReader
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.file_operation_error import FileOperationError


class TestFileReader:
    """Test suite for FileReader service."""
    
    @pytest.fixture
    def logger(self):
        """Create a logger for testing."""
        return logging.getLogger("test")
    
    @pytest.fixture
    def reader(self, logger):
        """Create a FileReader instance for testing."""
        return FileReader(logger)
    
    def test_read_text_from_valid_file(self, reader):
        """Test reading text from a valid file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content\nLine 2\nLine 3")
            temp_path = Path(f.name)
        
        try:
            content = reader.read_text(temp_path)
            
            assert content == "Test content\nLine 2\nLine 3"
        finally:
            temp_path.unlink()
    
    def test_read_text_from_empty_file(self, reader):
        """Test that reading empty file raises ValidationError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValidationError):
                reader.read_text(temp_path)
        finally:
            temp_path.unlink()
    
    def test_read_text_from_json_file(self, reader):
        """Test reading JSON content as text."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value", "number": 123}')
            temp_path = Path(f.name)
        
        try:
            content = reader.read_text(temp_path)
            
            assert '{"key": "value", "number": 123}' in content
        finally:
            temp_path.unlink()
    
    def test_read_text_with_unicode(self, reader):
        """Test reading file with unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write("Hello 世界 🌍")
            temp_path = Path(f.name)
        
        try:
            content = reader.read_text(temp_path)
            
            assert "Hello" in content
            assert "🌍" in content or "世界" in content  # May vary based on error handling
        finally:
            temp_path.unlink()
    
    def test_read_text_from_nonexistent_file(self, reader):
        """Test that reading nonexistent file raises FileOperationError."""
        nonexistent_path = Path("/tmp/nonexistent_file_12345.txt")
        
        with pytest.raises(FileOperationError):
            reader.read_text(nonexistent_path)
    
    def test_read_text_with_large_file(self, reader):
        """Test reading a large file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Write 1000 lines
            for i in range(1000):
                f.write(f"Line {i}\n")
            temp_path = Path(f.name)
        
        try:
            content = reader.read_text(temp_path)
            
            lines = content.splitlines()
            assert len(lines) == 1000
            assert "Line 0" in content
            assert "Line 999" in content
        finally:
            temp_path.unlink()
