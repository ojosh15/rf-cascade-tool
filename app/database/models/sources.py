from enum import Enum

class SourceEnum(str, Enum):
    SIMULATED = 'simulated'
    MEASURED = 'measured'