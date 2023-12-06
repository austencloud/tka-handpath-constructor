from typing import Dict, List, Optional, Tuple, TypedDict, Literal
from .Letters import Letters
from .SpecificPositions import SpecificPositions


Colors = Literal["red", "blue"]
MotionTypes = Literal["shift", "dash", "static"]
Locations = Literal["n", "e", "s", "w", "ne", "se", "sw", "nw"]

### HAND ATTRIBUTES ###

HandAttributes = Literal["color", "location"]
RotationAngles = Literal[0, 90, 180, 270]
RotationDirections = Literal["cw", "ccw"]
Positions = Literal["alpha", "beta", "gamma"]
Direction = Literal["right", "left", "down", "up"]
ColorsHex = Literal["#ED1C24", "#2E3192"]
LetterType = Literal[
    "Dual-Shift", "Shift", "Cross-Shift", "Dash", "Dual-Dash", "Static"
]

class SpecificStartEndPositionsDicts(TypedDict):
    start_position: SpecificPositions
    end_position: SpecificPositions

class HandAttributesDicts(TypedDict):
    color: Colors
    hand_location: Locations


### MOTION ATTRIBUTES ###

class MotionAttributesDicts(TypedDict):
    color: Colors
    motion_type: MotionTypes
    arrow_location: Locations
    start_location: Locations
    end_location: Locations


class ArrowAttributesDicts(TypedDict):
    color: Colors
    arrow_location: Locations


MotionAttributes = Literal[
    "color",
    "motion_type",
    
    "handpath_rotation_direction"
    
    "arrow_location",
    "start_location",
    "end_location",
]

StartEndLocationsTuple = Tuple[Locations, Locations]
PreprocessedStartEndCombinations = Dict[
    SpecificStartEndPositionsDicts,
    List[Tuple[Letters, List[MotionAttributesDicts]]],
]
DictVariants = MotionAttributesDicts | SpecificStartEndPositionsDicts
DictVariantsLists = List[DictVariants]
LetterDictionary = Dict[Letters, List[List[DictVariants]]]

HandpathMode = Optional[Literal["TS", "TO", "SS", "SO", "QTS", "QTO"]]


class PictographAttributesDict(TypedDict):
    start_position: Positions
    end_position: Positions
    letter_type: LetterType
    handpath_mode: HandpathMode



