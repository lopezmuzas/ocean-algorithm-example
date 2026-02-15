"""Unit tests for Response wrapper."""

import pytest
from pathlib import Path
from unittest.mock import Mock

from shared.infrastructure.response import Response
from shared.domain.results import Results


class TestResponse:
    """Test suite for Response wrapper."""
    
    @pytest.fixture
    def mock_result_writer(self):
        """Create a mock ResultWriter instance."""
        return Mock()
    
    @pytest.fixture
    def response_wrapper(self, mock_result_writer):
        """Create a Response instance for testing with mocked services."""
        return Response(mock_result_writer)
    
    def test_write_results(self, response_wrapper, mock_result_writer):
        """Test write_results delegates to result_writer."""
        mock_results = Results(status="success", message="test")
        mock_path = Path("/tmp/output.json")
        
        # Call write_results
        response_wrapper.write_results(mock_results, mock_path)
        
        # Verify result_writer.write_json was called
        mock_result_writer.write_json.assert_called_once_with(mock_results, mock_path)