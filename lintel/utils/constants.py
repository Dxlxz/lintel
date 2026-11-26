import re
from lintel.classes.templating.constants_container import ConstantsContainer
from lintel.classes.templating.namespace_template import NamespaceTemplate

# TODO: Move this to lintel/constants/__init__.py
# Singleton instance created on import/init
constants = ConstantsContainer()


# TODO: Consolidate this and lintel/utils/prompt_utils.py
#       into lintel/utils/templating_utils.py
def substitute_constants(text):
    """Substitute constants in the prompt."""
    # Substitute constants by reading the constants file.
    # Regex to extract all occurrences of ${gr.<constant_name>}
    matches = re.findall(r"\${gr\.(\w+)}", text)

    # Substitute all occurrences of ${gr.<constant_name>}
    #   with the value of the constant.
    for match in matches:
        template = NamespaceTemplate(text)
        mapping = {f"gr.{match}": constants[match]}
        text = template.safe_substitute(**mapping)

    return text
