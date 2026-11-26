from typing import Dict, List, Union

from lintel.prompt.prompt import Prompt

"""List[Dict[str, Union[Prompt, str]]]"""
MessageHistory = List[Dict[str, Union[Prompt, str]]]
