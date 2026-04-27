# Risk Reporting Engine

A lightweight Python project that converts operational, infrastructure, or security risk data into an executive-ready Markdown report.

## Why this exists

Senior technical programs often need a repeatable way to turn scattered risk data into clear leadership decisions. This project demonstrates:

- Risk scoring logic
- Security/control evaluation
- Executive summary generation
- CSV-driven reporting
- Testable Python code structure

## Example use cases

- Security control review
- Infrastructure readiness reporting
- Operational risk review
- Program status reporting
- Executive escalation prep

## Input format

See `examples/sample_risks.csv`.

Required columns:

```csv
id,title,domain,likelihood,impact,control_status,owner,due_date
```

## Run locally

```bash
python src/report_generator.py examples/sample_risks.csv examples/sample_report.md
```

## Scoring model

```text
risk_score = likelihood * impact
```

Severity:

- 16–25: Critical
- 9–15: High
- 4–8: Medium
- 1–3: Low

## Project structure

```text
src/
  risk_engine.py       Core scoring logic
  controls.py          Control/compliance checks
  report_generator.py  CSV to Markdown report
examples/
  sample_risks.csv     Example input
  sample_report.md     Example output
tests/
  test_risk_engine.py  Unit tests
```

## Notes

This is a demonstration portfolio project. It contains no real company data, secrets, or credentials.
