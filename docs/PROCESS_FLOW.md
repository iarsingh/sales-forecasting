# Sales Forecasting: process flows

## Domain request

Endpoint: `POST /forecast`. Stages summarize [src/salesfc/forecast.py](../src/salesfc/forecast.py). This is in-process Python, not a hosted model or production apply.

```mermaid
flowchart TD
  A["POST /forecast"] --> B{"Valid input?"}
  B -->|"No"| E["HTTP 422"]
  B -->|"Yes: At least 3 numbers"| C["Domain function in forecast.py"]
  C --> O["mean of last 3; window 3"]
  O --> X["No production side effect"]
```

See [INTERVIEW_QA.md](../INTERVIEW_QA.md) for fixture walkthroughs and [PROJECT_ARCHITECTURE.md](../PROJECT_ARCHITECTURE.md) for the component map.
