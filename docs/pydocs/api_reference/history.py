from docspec_python import ParserOptions
from docs.pydocs.pydocs_markdown_impl import render_loader
from pydoc_markdown.contrib.loaders.python import PythonLoader
from docs.pydocs.helpers import write_to_file


write_to_file(
    str="# History and Logs\n\n"
    + render_loader(
        loader=PythonLoader(
            modules=[
                "lintel.classes.history.call",
                "lintel.classes.history.iteration",
                "lintel.classes.history.inputs",
                "lintel.classes.history.outputs",
                "lintel.classes.history.call_inputs",
            ],
            parser=ParserOptions(print_function=False),
        ),
    ),
    filename="docs/api_reference/history_and_logs.md",
)
