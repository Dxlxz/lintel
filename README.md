<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./docs/assets/lintel_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="./docs/assets/lintel.svg">
    <img alt="Lintel" src="./docs/assets/lintel.svg" width="40%">
  </picture>
</p>

<h3 align="center">Guardrails, policy and decision records for LLM applications</h3>

<p align="center">
  <a href="https://github.com/Dxlxz/lintel/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Dxlxz/lintel/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-blue">
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776ab">
  <img alt="Telemetry" src="https://img.shields.io/badge/telemetry-off%20by%20default-0d9488">
</p>

---

**Lintel** is the beam a request passes under before it reaches your application, and the beam it passes under
again on the way out. Every input and every output goes through a chain of validators; a failure is repaired,
retried against the model, or raised — and each decision is written down.

It is the sibling of [Tessera](https://github.com/Dxlxz/tessera): Tessera assembles the pipeline, Lintel guards
what flows through it.

## What it does

| | |
|---|---|
| **Input and output guards** | Validate user prompts and model responses against validators you compose into a `Guard` |
| **Repair, don't just complain** | `FIX` rewrites the value, `REASK` sends the failure back to the model, `EXCEPTION` / `FILTER` / `NOOP` when you want control |
| **Structured output** | `Guard.for_pydantic(Model)` — function calling where the model supports it, schema-in-prompt where it does not |
| **Policy as a spec** | The same guard as a `.rail` file or a Pydantic model, so policy is reviewed, diffed and versioned like code |
| **Every decision recorded** | Each validation carries validator name, status, failure reason and error spans — the record your audit needs |
| **Local by default** | No account, no key, no telemetry unless you set `LINTEL_TELEMETRY_ENDPOINT` |

## Install

Requires Python 3.10 – 3.13.

```shell
git clone https://github.com/Dxlxz/lintel.git
cd lintel
uv sync                      # or: pip install -e .
```

## A guard in twenty lines

A validator is a class with a `validate` method. Register it once, use it anywhere:

```python
from typing import Any, Dict

from lintel import Guard, Validator, register_validator
from lintel.classes.validation.validation_result import FailResult, PassResult
from lintel.types.on_fail import OnFailAction


@register_validator(name="no-pii-in-output", data_type="string")
class NoPiiInOutput(Validator):
    """Flags email addresses and replaces them with a stable token."""

    def validate(self, value: Any, metadata: Dict[str, Any]) -> Any:
        text = str(value)
        if "@" not in text:
            return PassResult()
        return FailResult(
            error_message="Output contained an email address.",
            fix_value=text.replace("dana@acme.example", "[[email-1]]"),
        )


guard = Guard().use(NoPiiInOutput(on_fail=OnFailAction.FIX))
```

```console
>>> guard.validate("The invoice was approved in March.")
ValidationOutcome(validation_passed=True, validated_output='The invoice was approved in March.')

>>> guard.validate("Contact dana@acme.example for the signed PO.")
ValidationOutcome(validation_passed=True, validated_output='Contact [[email-1]] for the signed PO.')
```

The second call *passed* — the validator found a problem and repaired it, and the outcome still records that
`no-pii-in-output` fired. That distinction (was it clean, or was it fixed?) is the difference between a boolean
and an audit trail.

Swap `on_fail=OnFailAction.REASK` and the failure goes back to the model as a re-ask prompt, with your error
message and the offending spans, up to `num_reasks` times.

## Structured output

```python
from pydantic import BaseModel, Field
from lintel import Guard


class Pet(BaseModel):
    pet_type: str = Field(description="Species of pet")
    name: str = Field(description="a unique pet name")


guard = Guard.for_pydantic(Pet)
result = guard(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Generate a random pet."}],
)
```

Use `Guard.from_rail("policy.rail")` when policy lives in a file rather than Python — same validators, same
outcomes, reviewable by people who don't read Python.

## Validators

Validators are ordinary packages. A validator ships as `lintel-<name>` and imports from the `lintel_ai.<name>`
namespace, so a guard is just a list of imports you can read:

```python
from lintel import Guard
from lintel_ai.regex_match import RegexMatch
from lintel_ai.toxic_language import ToxicLanguage

guard = Guard().use(
    RegexMatch(regex=r"\(?\d{3}\)?-? *\d{3}-? *-?\d{4}", on_fail=OnFailAction.EXCEPTION),
    ToxicLanguage(threshold=0.5, validation_method="sentence", on_fail=OnFailAction.REASK),
)
```

Roughly 60 validators exist across these families:

| Family | Examples |
|---|---|
| PII and privacy | `detect_pii`, `guardrails_pii`, `provenance_llm` |
| Safety and tone | `toxic_language`, `bias_check`, `restrict_to_topic`, `ban_list` |
| Groundedness | `provenance_embeddings`, `provenance_vlm`, `endpoint_is_valid` |
| Format and structure | `regex_match`, `one_line`, `valid_json`, `sql_column_presence`, `reading_time` |
| Domain | `competitor_check`, `lowercase`, `upper_case`, `exclude_sql_predicates` |

Write the one your domain needs — a validator is a class, not a plugin system.

## CLI

```shell
lintel configure                        # write ~/.lintelrc: hub token, metrics off by default
lintel hub install hub://lintel/regex_match
lintel validate policy.rail             # validate a guard spec without writing code
lintel start                            # REST server for /guards/{name}/validate
lintel watch                            # re-run a guard on file change
```

## Layout

```
lintel/
  guard.py, async_guard.py    the Guard: call, validate, parse, reask
  validator_base.py           Validator, ValidationResult, register_validator
  validators/                 built-in validators
  prompt/, schema/            prompt construction, JSON schema + RAIL parsing
  classes/history/            call and iteration records (the decision trail)
  cli/                        configure, hub, validate, start, watch, db
  telemetry/                  opt-in OTel tracing of validation events
  hub/                        validator registry, namespace shim, install
tests/                        unit, integration and application tests
```

## Where this is going

- [ ] Decision records over HTTP: `GET /records?since=...`, so an auditor reads what the guard blocked
- [ ] Policy bundles: one YAML declaring guards, thresholds and fail actions per route
- [ ] Redaction pipeline shipped as a built-in: detect → mask → record, no model call
- [ ] Trace a guard run as OTel spans so it lands next to the LLM call it belongs to

## See also

**[Tessera](https://github.com/Dxlxz/tessera)** — the pipeline side: RAG built from MCP servers.
**[Quorum](https://github.com/Dxlxz/quorum)** — the domain application: LLM investor agents under a risk desk,
with every decision appended to a hash-chained ledger.

## License and lineage

Apache-2.0 — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).

Lintel is developed from the Guardrails AI codebase (Apache-2.0), with the package, CLI, env prefix, telemetry
defaults, branding and product surface rebuilt. Shared schema types and the optional REST server remain the
upstream `guardrails-ai-types` and `guardrails-api` packages. Upstream copyright is retained in the license and
notice files.
