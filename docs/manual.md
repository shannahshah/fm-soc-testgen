# SOC FM Test Framework Manual

This manual explains how to use the foundation model test framework for generating synthetic security events and running drift scenarios against SOC pipelines. The goal is to help engineers reveal brittle parsing, schema issues, and detection regressions by testing how their environment reacts to realistic log variation.

---

## 1. Overview

This framework uses a foundation model to create synthetic security logs from real seed data. It then applies controlled drift scenarios to test how stable a SOC pipeline is when timestamps shift, identities change, or fields evolve. All scenarios are defined in small YAML files to keep tests repeatable and easy to extend.

The system contains five core parts:

1. Log loading  
2. FM synthetic event generation  
3. Drift and perturbation scenarios  
4. Schema validation  
5. Reporting

---

## 2. Installation

```bash
python3 -m pip install -e .
python3 -m pip install jsonschema pyyaml
```

## 3. Loading Seed Logs

Seed logs should be in JSON format. The loader accepts JSON arrays or NDJSON:

```python
from fm_soc_testgen import JsonLoader

events = JsonLoader.load("sample_data/windows_logs_sample.json")
```
These events become the basis for FM generation.

## 4. Generating Synthetic Events With a Foundation Model

Example with the placeholder generator:

```python
from fm_soc_testgen import FmGenerator, echo_prompt_fn

fm = FmGenerator(model="echo", prompt_fn=echo_prompt_fn)
synthetic = fm.generate_from_seeds(events, num=20)
```
---

## 5. Running Drift Scenarios

Scenarios are defined in YAML files under `config/scenarios`. Each file lists the perturbations to apply.

Example:

```yaml
name: windows_signin_drift
perturbations:
  - name: timestamp_drift
    params:
      max_offset_minutes: 15
  - name: identity_shift
    params:
      fields: ["user"]
```

To run the scenario:

```python
from fm_soc_testgen import run_scenario_from_yaml

result = run_scenario_from_yaml(
    synthetic,
    "config/scenarios/windows_signin.yaml"
)

print(result.events[:3])  # preview first few events
```
## 6. Schema Validation

Schemas are stored in `config/schemas` and checked with the `SchemaValidator`.

```python
from fm_soc_testgen import SchemaValidator

validator = SchemaValidator("config/schemas/windows.json")
errors = validator.validate(result.events)
print(errors)
```
Any schema mismatch is reported so SOC teams can identify weak points in parsers or ingestion paths.

## 7. Reporting

The framework provides a basic reporting utility to summarize the generated or transformed events.

```python
from fm_soc_testgen import basic_report

report = basic_report(result.events)
print(report)
```
This report displays event counts, missing timestamps, unique event types, and a small sample of events for quick inspection.

## 8. Smoke Test

A simple end-to-end check to confirm the framework is working:

1. Load the sample logs.  
2. Generate synthetic events with the FM generator.  
3. Run the drift scenario.  
4. Validate the output using the schema.  
5. Print the report.

## 9. Extending the System

The framework is modular and easy to extend. You can add:

- New perturbation functions  
- New schemas  
- New scenarios  
- New FM generator adapters  
- New reporting modules  

Each component is isolated so you can modify or expand one part without affecting the others.

## 10. When To Use This Framework

Use this framework when you want to evaluate:

- Parser stability  
- Detection rule robustness  
- SOC regression behavior  
- Pipeline drift  
- Schema enforcement  
- Ingestion tolerance to log variation  

It is well suited for pre-deployment validation, daily smoke tests, and controlled change analysis in a SOC environment.

If all steps complete without errors, the test environment is set up correctly.

