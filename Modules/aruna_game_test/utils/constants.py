from odoo.exceptions import ValidationError
from enum import Enum, auto


class ProperPositionException(ValidationError):
    pass


class eObjectFacing(str, Enum):
    north = auto()
    east = auto()
    south = auto()
    west = auto()


class eObjectTurnDirection(str, Enum):
    left = auto()
    right = auto()


class eMoveModifier:
    def __init__(self, x_pos, y_pos) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos


# Object turning sequence, from left to right
OBJECT_TURNING_POS = [eObjectFacing.north.name, eObjectFacing.east.name,
                      eObjectFacing.south.name, eObjectFacing.west.name]


# Move modifier value, origin coordinate / (0,0) coordinate is on most
# South West position
MOVE_MODIFIER = {
    eObjectFacing.north.name: eMoveModifier(x_pos=0, y_pos=1),
    eObjectFacing.south.name: eMoveModifier(x_pos=0, y_pos=-1),
    eObjectFacing.east.name: eMoveModifier(x_pos=1, y_pos=0),
    eObjectFacing.west.name: eMoveModifier(x_pos=-1, y_pos=0)
}

# Command List
COMMAND_MAP = {
    'LEFT': {
        'func': 'turn_robot',
        'context': {
            'turn_direction': 'left'
        }
    },
    'RIGHT': {
        'func': 'turn_robot',
        'context': {
            'turn_direction': 'right'
        }
    },
    'MOVE': {
        'func': 'move_robot',
        'context': {}
    },
    'REPORT': {
        'func': 'report_location',
        'context': {}
    }
}


def check_table_pos(func):
    """Decorator to check whether command should be ignored or not.
    Command will only executed if the robot is properly placed in the table
    """

    def inner(self):
        if not self.is_properly_placed:
            return None
        else:
            # Execute function first, then check whether the function execution is valid
            # (within the table boundary area)
            func(self)
            return self._check_out_of_bound()

    return inner
