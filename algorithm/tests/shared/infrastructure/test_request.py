"""Unit tests for Request wrapper."""

import logging
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from shared.infrastructure.request import Request
from shared.domain.exceptions.validation_error import ValidationError


class TestRequest:
    """Test suite for Request wrapper."""
    
    @pytest.fixture
    def logger(self):
        """Create a logger for testing."""
        return logging.getLogger("test")
    
    @pytest.fixture
    def mock_algorithm(self, logger):
        """Create a mock Algorithm instance."""
        algo = Mock()
        algo.logger = logger
        algo.job_details = Mock()
        return algo
    
    @pytest.fixture
    def mock_file_reader(self):
        """Create a mock FileReader instance."""
        return Mock()
    
    @pytest.fixture
    def request_wrapper(self, mock_algorithm, mock_file_reader):
        """Create a Request instance for testing."""
        return Request(mock_algorithm, mock_file_reader)
    
    def test_count_with_no_files(self, request_wrapper, mock_algorithm):
        """Test count returns zero when no input files."""
        mock_algorithm.job_details.inputs.return_value = iter([])
        
        count = request_wrapper.count()
        
        assert count == 0
    
    def test_count_with_multiple_files(self, request_wrapper, mock_algorithm):
        """Test count returns correct number of input files."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt")),
            (2, Path("/tmp/file3.txt"))
        ])
        
        count = request_wrapper.count()
        
        assert count == 3
    
    def test_get_content_valid_index(self, request_wrapper, mock_algorithm, mock_file_reader):
        """Test get_content returns file content for valid index."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt"))
        ])
        mock_file_reader.read_text.return_value = "File content"
        
        content = request_wrapper.get_content(0)
        
        assert content == "File content"
        mock_file_reader.read_text.assert_called_once()
    
    def test_get_content_invalid_index_negative(self, request_wrapper, mock_algorithm):
        """Test get_content raises ValidationError for negative index."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt"))
        ])
        
        with pytest.raises(ValidationError, match="Index -1 out of range"):
            request_wrapper.get_content(-1)
    
    def test_get_content_invalid_index_too_large(self, request_wrapper, mock_algorithm):
        """Test get_content raises ValidationError for index out of range."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt"))
        ])
        
        with pytest.raises(ValidationError, match="Index 5 out of range"):
            request_wrapper.get_content(5)
    
    def test_iter_files_yields_all_files(self, request_wrapper, mock_algorithm):
        """Test iter_files yields all input files."""
        files = [
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt")),
            (2, Path("/tmp/file3.txt"))
        ]
        mock_algorithm.job_details.inputs.return_value = iter(files)
        
        result = list(request_wrapper.iter_files())
        
        assert len(result) == 3
        assert result[0] == (0, Path("/tmp/file1.txt"))
        assert result[1] == (1, Path("/tmp/file2.txt"))
        assert result[2] == (2, Path("/tmp/file3.txt"))
    
    def test_merge_all_with_default_separator(self, request_wrapper, mock_algorithm, mock_file_reader):
        """Test merge_all combines all file contents with newline."""
        files = [
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt"))
        ]
        mock_algorithm.job_details.inputs.side_effect = lambda: iter(files)
        mock_file_reader.read_text.side_effect = ["Content 1", "Content 2"]
        
        result = request_wrapper.merge_all()
        
        assert result == "Content 1\nContent 2"
        assert mock_file_reader.read_text.call_count == 2
    
    def test_merge_all_with_custom_separator(self, request_wrapper, mock_algorithm, mock_file_reader):
        """Test merge_all with custom separator."""
        files = [
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt"))
        ]
        mock_algorithm.job_details.inputs.side_effect = lambda: iter(files)
        mock_file_reader.read_text.side_effect = ["Content 1", "Content 2"]
        
        result = request_wrapper.merge_all(separator=" | ")
        
        assert result == "Content 1 | Content 2"
    
    def test_merge_all_with_no_files(self, request_wrapper, mock_algorithm):
        """Test merge_all raises ValidationError when no input files."""
        mock_algorithm.job_details.inputs.side_effect = lambda: iter([])
        
        with pytest.raises(ValidationError, match="No input files to merge"):
            request_wrapper.merge_all()
    
    def test_batch_iter_single_batch(self, request_wrapper, mock_algorithm, mock_file_reader):
        """Test batch_iter with all files in one batch."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt"))
        ])
        mock_file_reader.read_text.side_effect = ["Content 1", "Content 2"]
        
        batches = list(request_wrapper.batch_iter(batch_size=5))
        
        assert len(batches) == 1
        assert batches[0] == ["Content 1", "Content 2"]
    
    def test_batch_iter_multiple_batches(self, request_wrapper, mock_algorithm, mock_file_reader):
        """Test batch_iter splits files into multiple batches."""
        mock_algorithm.job_details.inputs.return_value = iter([
            (0, Path("/tmp/file1.txt")),
            (1, Path("/tmp/file2.txt")),
            (2, Path("/tmp/file3.txt")),
            (3, Path("/tmp/file4.txt")),
            (4, Path("/tmp/file5.txt"))
        ])
        mock_file_reader.read_text.side_effect = ["C1", "C2", "C3", "C4", "C5"]
        
        batches = list(request_wrapper.batch_iter(batch_size=2))
        
        assert len(batches) == 3
        assert batches[0] == ["C1", "C2"]
        assert batches[1] == ["C3", "C4"]
        assert batches[2] == ["C5"]
    
    def test_batch_iter_invalid_batch_size_zero(self, request_wrapper, mock_algorithm):
        """Test batch_iter raises ValidationError for zero batch size."""
        mock_algorithm.job_details.inputs.return_value = iter([])
        
        with pytest.raises(ValidationError, match="Batch size must be positive"):
            list(request_wrapper.batch_iter(batch_size=0))
    
    def test_batch_iter_invalid_batch_size_negative(self, request_wrapper, mock_algorithm):
        """Test batch_iter raises ValidationError for negative batch size."""
        mock_algorithm.job_details.inputs.return_value = iter([])
        
        with pytest.raises(ValidationError, match="Batch size must be positive"):
            list(request_wrapper.batch_iter(batch_size=-1))
