# sales-forecasting — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

Forecast the next sales point as the mean of the last three observations.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/salesfc/__init__.py"]
    M1["src/salesfc/forecast.py"]
    M2["src/salesfc/main.py"]
    M2 -->|imports| M1
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/salesfc/main.py`](src/salesfc/main.py) | HTTP handlers: `GET /healthz`, `POST /forecast` |
| [`src/salesfc/forecast.py`](src/salesfc/forecast.py) | Functions: `forecast` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/salesfc/__init__.py`](src/salesfc/__init__.py) | Implementation or supporting configuration |
| [`tests/test_forecast.py`](tests/test_forecast.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/salesfc/main.py`](src/salesfc/main.py#L8) |
| `POST /forecast` | `post_forecast` | [`src/salesfc/main.py`](src/salesfc/main.py#L13) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `forecast(series)`

Source: [`src/salesfc/forecast.py`](src/salesfc/forecast.py#L8).

Calls visible in this function: `InputError`, `float`, `isinstance`, `len`, `numbers.append`, `round`, `sum`.

```python
def forecast(series):
    if not isinstance(series, list) or len(series) < WINDOW:
        raise InputError(f"series must have at least {WINDOW} numbers")
    numbers = []
    for value in series:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise InputError("series must be numbers")
        numbers.append(float(value))
    last = numbers[-WINDOW:]
    next_value = sum(last) / WINDOW
    return {"next": round(next_value, 4), "window": WINDOW, "used": last}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `InputError(f'series must have at least {WINDOW} numbers')` | [`src/salesfc/forecast.py`](src/salesfc/forecast.py#L10) |
| `InputError('series must be numbers')` | [`src/salesfc/forecast.py`](src/salesfc/forecast.py#L14) |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/salesfc/main.py`](src/salesfc/main.py#L17) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data flow and design decisions

### What is the input-to-output contract of `forecast`

In [`src/salesfc/forecast.py`](src/salesfc/forecast.py#L8), `forecast(series)` receives the inputs. The function computes these intermediate values:

- `numbers = []`
- `last = numbers[-WINDOW:]`
- `next_value = sum(last) / WINDOW`

Its result is defined by:

- `{'next': round(next_value, 4), 'window': WINDOW, 'used': last}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/salesfc/forecast.py`](src/salesfc/forecast.py#L8) branches on:

- `not isinstance(series, list) or len(series) < WINDOW`
- `not isinstance(value, (int, float)) or isinstance(value, bool)`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_forecast.py`](tests/test_forecast.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.

## Request flow

The decision flow for `POST /forecast` is in [docs/PROCESS_FLOW.md](docs/PROCESS_FLOW.md).

```mermaid
flowchart LR
  C["Client JSON"] --> A["FastAPI src/salesfc/main.py"]
  A --> H["POST /forecast"]
  H --> D["forecast.py"]
  D --> R["JSON result or HTTP 422"]
```

