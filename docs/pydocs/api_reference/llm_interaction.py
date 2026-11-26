from docspec_python import ParserOptions
from docs.pydocs.pydocs_markdown_impl import render_loader
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from docs.pydocs.helpers import write_to_file


export_map = {
    "lintel/prompt/base_prompt.py": [
        "lintel.prompt.base_prompt",
        "BasePrompt",
        "__init__",
        "format",
        "substitute_constants",
        "get_prompt_variables",
        "escape",
    ],
    "lintel/prompt/prompt.py": [
        "lintel.prompt.prompt",
        "Prompt",
        "format",
    ],
    "lintel/prompt/instructions.py": [
        "lintel.prompt.instructions",
        "Instructions",
        "format",
    ],
    "lintel/llm_providers.py": [
        "lintel.llm_providers",
        "PromptCallableBase",
        "_invoke_llm",
        "__call__",
    ],
    "lintel/classes/llm/llm_response.py": [
        "lintel.classes.llm.llm_response",
        "LLMResponse",
    ],
}


conditionals = []
for k, v in export_map.items():
    conditionals.append(
        f"((name in {v}) if ('{k}' in obj.location.filename) else False)"
    )

export_string = " or ".join(conditionals)

write_to_file(
    str="# Helpers for LLM Interactions\n\n"
    + render_loader(
        PythonLoader(
            modules=[
                "lintel.prompt.base_prompt",
                "lintel.prompt.prompt",
                "lintel.prompt.instructions",
                "lintel.llm_providers",
                "lintel.classes.llm.llm_response",
            ],
            parser=ParserOptions(print_function=False),
        ),
        processor=FilterProcessor(
            expression=f"({export_string})",  # noqa
            skip_empty_modules=True,
        ),
    ),
    filename="docs/api_reference/llm_interaction.md",
)
