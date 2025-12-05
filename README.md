# fm soc testgen

Foundation Model Test Generation for SOC Pipelines

`fm soc testgen` is a lightweight framework that uses foundation models to generate structured test cases and controlled perturbation scenarios for Security Operations Center analytics. It helps engineers understand how their pipelines behave when log data shifts in small but meaningful ways.

## Why this project exists

SOC pipelines usually work well when logs match historical patterns. In real environments, small variations in timestamps, identity formatting, event order, and field structure often cause unexpected behavior. Traditional testing based on replayed historical logs or hand written cases does not reveal these weaknesses.

This framework provides a simple and repeatable way to:

- Create realistic synthetic events based on seed data  
- Apply controlled perturbations that reflect common operational drift  
- Produce test datasets that can be used with any SOC platform  

## Features

- Generate synthetic events with a foundation model that respects your schema  
- Apply drift scenarios such as timestamp offsets, identity format changes, missing fields, and reordered events  
- Use YAML files to define reproducible scenarios  
- Save synthetic logs along with a manifest describing the generation process  
- Run basic validation checks on output  

## Getting started

### Requirements

- Python 3.9 or newer  
- Standard Python packages such as `openai`, `pyyaml`, and `pydantic`  
- Access to a foundation model API or a local model  


```markdown
### Quick example

```python
from fm_soc_testgen.data import JsonLoader
from fm_soc_testgen.fm import FmGenerator
from fm_soc_testgen.scenarios import ScenarioRunner

# Load seed logs
logs = JsonLoader.load("sample_data/windows_logs_sample.json")

# Generate synthetic events
fm = FmGenerator(model="openai gpt 4")
synthetic = fm.generate_from_seeds(logs, num=1000)

# Apply a drift scenario
runner = ScenarioRunner(schema="config/schemas/windows.json")
scenario = runner.run(
    events=synthetic,
    perturbations=["timestamp_drift", "identity_shift"]
)

# Save output
scenario.to_json("output/synthetic_logs.json")
scenario.to_manifest("output/manifest.json")
