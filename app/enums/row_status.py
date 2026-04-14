from enum import Enum


class RowStatus(int, Enum):
    INACTIVE = 0
    ACTIVE = 1
    DELETED = 2 
    