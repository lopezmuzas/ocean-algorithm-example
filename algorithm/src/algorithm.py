from pathlib import Path
from ocean_runner import Algorithm, Config
import json

from .data import InputParameters
from .results import Results as ResultsT

algorithm = Algorithm(config=Config(custom_input=InputParameters))


@algorithm.validate
def validate(algorithm: Algorithm) -> None:
    algorithm.logger.info("validate: starting")
    # Simple validation - check if we have basic input structure
    # In a real implementation, you would validate DDOs and input files
    pass


@algorithm.run
def run(algorithm: Algorithm) -> ResultsT:
    algorithm.logger.info("run: starting")
    
    # Extract ages from input parameters
    ages = []
    for idx, path in algorithm.job_details.inputs():
        text = path.read_text(errors="replace")
        #algorithm.logger.info(f"Input {idx} - File: {path.name}")
        
        try:
            data = json.loads(text)
            
            # Support multiple formats
            if isinstance(data, list):
                # Format: [{"user_id": 1, "age": 10}, ...]
                for item in data:
                    if isinstance(item, dict) and "age" in item:
                        ages.append(item["age"])
            elif isinstance(data, dict):
                # Format: {"ages": [25, 30, ...]}
                if "ages" in data:
                    ages.extend(data["ages"])                    
        except json.JSONDecodeError:
            algorithm.logger.warning(f"Could not parse JSON from {path.name}")
    
    # Calculate age statistics
    if ages:
        min_age = min(ages)
        max_age = max(ages)
        avg_age = sum(ages) / len(ages)
    else:
        min_age = 0
        max_age = 0
        avg_age = 0.0
    
    algorithm.logger.info(f"Min: {min_age}, Max: {max_age}, Avg: {avg_age:.2f}")

    return ResultsT(
        status="success",
        message="Algorithm executed successfully",
        min_age=min_age,
        max_age=max_age,
        avg_age=avg_age,
    )


@algorithm.save_results
def save(
    algorithm: Algorithm,
    results: ResultsT,
    base_path: Path,
) -> None:
    algorithm.logger.info("save: starting")
    # Save results to a simple JSON file
    output_file = base_path / "results.json"
    output_file.write_text(results.model_dump_json(indent=2))


if __name__ == "__main__":
    algorithm()
