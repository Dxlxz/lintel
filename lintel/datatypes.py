from typing import List

from lintel.types.simple import SimpleTypes
from lintel.types.rail import RailTypes


types_registry: List[str] = [
    *[st.value for st in SimpleTypes],
    *[rt.value for rt in RailTypes],
]
