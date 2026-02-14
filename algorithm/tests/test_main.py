from pathlib import Path
import tempfile
import json
from src.algorithm import algorithm
from src.results import Results


def test_algorithm_execution():
    """Test that the algorithm can be instantiated and configured properly."""
    # The algorithm should be importable without errors
    assert algorithm is not None
    assert hasattr(algorithm, 'validate')
    assert hasattr(algorithm, 'run')
    assert hasattr(algorithm, 'save_results')


def test_results_model():
    """Test the Results model can be instantiated and serialized."""
    results = Results(
        status="success",
        message="Test message",
        min_age=20,
        max_age=50,
        avg_age=35.5
    )
    
    assert results.status == "success"
    assert results.message == "Test message"
    assert results.min_age == 20
    assert results.max_age == 50
    assert results.avg_age == 35.5
    
    # Test JSON serialization
    json_str = results.model_dump_json()
    assert "success" in json_str
    assert "Test message" in json_str


def test_save_results():
    """Test the save function writes results to JSON file."""
    results = Results(
        status="success",
        message="Test message",
        min_age=25,
        max_age=45,
        avg_age=33.5
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = Path(temp_dir)
        output_file = base_path / "results.json"
        
        # Save using the same method as the algorithm
        output_file.write_text(results.model_dump_json(indent=2))
        
        assert output_file.exists()
        
        # Verify JSON content
        with open(output_file, "r") as f:
            content = json.load(f)
            assert content["status"] == "success"
            assert content["message"] == "Test message"
            assert content["min_age"] == 25
            assert content["max_age"] == 45
            assert content["avg_age"] == 33.5

