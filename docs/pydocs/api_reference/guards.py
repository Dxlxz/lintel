from docspec_python import ParserOptions
from docs.pydocs.pydocs_markdown_impl import render_loader
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from docs.pydocs.helpers import write_to_file


export_map = {
    "lintel/guard.py": [
        "Guard",
        "lintel.guard",
        "guard",
        "__init__",
        "for_rail",
        "for_rail_string",
        "for_pydantic",
        "for_string",
        "configure",
        "use",
        "get_validators",
        "__call__",
        "parse",
        "validate",
        "error_spans_in_output",
        "json_function_calling_tool",
        "to_dict",
        "from_dict",
        "to_runnable",
    ],
    "lintel/async_guard.py": [
        "AsyncGuard",
        "lintel.async_guard",
        "async_guard",
        "__init__",
        "for_rail",
        "for_rail_string",
        "for_pydantic",
        "for_string",
        "configure",
        "use",
        "get_validators",
        "__call__",
        "parse",
        "validate",
        "error_spans_in_output",
        "json_function_calling_tool",
        "to_dict",
        "from_dict",
        "to_runnable",
    ],
    "lintel/classes/validation_outcome.py": [
        "lintel.classes.validation_outcome",
        "ValidationOutcome",
        "from_guard_history",
    ],
}


conditionals = []
for k, v in export_map.items():
    conditionals.append(
        f"((name in {v}) if ('{k}' in obj.location.filename) else False)"
    )

export_string = " or ".join(conditionals)

write_to_file(
    str="# Guards\n\n"
    + render_loader(
        PythonLoader(
            modules=[
                "lintel.guard",
                "lintel.async_guard",
                "lintel.classes.validation_outcome",
            ],
            parser=ParserOptions(print_function=False),
        ),
        processor=FilterProcessor(
            expression=f"({export_string})",
            skip_empty_modules=True,
        ),
    ),
    filename="docs/api_reference/guards.md",
)
