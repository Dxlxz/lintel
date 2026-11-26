# Migration guide: Hub install → public PyPI

As of Lintel **0.11.0**, Lintel-AI-owned validators have moved from the private Lintel registry
(`pypi.https://github.com/Dxlxz/lintel`, installed via `guardrails hub install`) to **public
PyPI**. Each validator is now published as a `lintel-<name>` distribution
and imported from the PEP 420 `lintel_ai` namespace.

## What changed

| Before | After |
|---|---|
| `guardrails hub install hub://lintel/detect_pii` | `pip install lintel-detect-pii` |
| `from lintel.hub import DetectPII` | `from lintel_ai.detect_pii import DetectPII` |
| Private registry `pypi.https://github.com/Dxlxz/lintel` (token required) | Public PyPI (no token) |
| Dist name `guardrails-grhub-detect-pii` | `lintel-detect-pii` |

The registered validator name is **unchanged** — `@register_validator(name="lintel/detect_pii")`
still resolves, so `Guard().use(...)` and existing guards keep working.

## Deprecation timeline (back-compat is preserved for now)

Nothing breaks today. During the deprecation window:

- **`guardrails hub install hub://lintel/<name>`** still works — it now
  installs `lintel-<name>` from public PyPI and prints a
  `DeprecationWarning` pointing at the equivalent `pip install` command. The
  same warning is emitted by `uninstall`, `list`, `submit`, and
  `create-validator`.
- **`from lintel.hub import X`** still works — if an export isn't found in
  the local hub registry, it falls back to scanning installed `lintel_ai.*`
  packages and emits a one-time `DeprecationWarning` recommending the direct
  `from lintel_ai.<name> import X` import.

Both the `guardrails hub` CLI and the `lintel.hub` import shim are scheduled
for **removal in the next major release**. Update install commands and imports
to the public-PyPI form at your convenience before then.

## How to migrate

1. Replace `guardrails hub install hub://lintel/<name>` with
   `pip install lintel-<name>` (underscores in `<name>` become dashes in
   the dist name).
2. Replace `from lintel.hub import <Export>` with
   `from lintel_ai.<name> import <Export>`.
3. For validators that ship local models, run the post-install step after
   installing — see the package's README on PyPI.

Browse the full catalog of validators and their new package names in the
[`guardrails-hub` repo's `VALIDATORS.md`](https://github.com/Dxlxz/lintel-hub).

---

## Related: RAIL (`.rail`) removal — next major

The `.rail` XML spec format and the `Guard.for_rail` / `Guard.for_rail_string`
APIs are being removed in the next major release (this also drops the `lxml`
dependency). Migrate RAIL-defined guards to Pydantic or JSON-schema guards:

- `Guard.for_rail("spec.rail")` / `Guard.for_rail_string(...)` →
  `Guard.for_pydantic(MyModel)` or a JSON-schema-based guard plus plain
  `messages`.
- The `guardrails validate` CLI command (which parsed `.rail`) is removed.

Validator quality criteria expressed in RAIL map directly onto
`Guard().use(<Validator>, ...)` calls.
