from enum import Enum, auto


class eObjectFacing(str, Enum):
    """
    Enum for object facing.
    """
    north = auto()
    east = auto()
    south = auto()
    west = auto()


class eObjectTurnDirection(str, Enum):
    """
    Enum for object turning direction.
    """
    left = auto()
    right = auto()


# Object turning sequence, from left to right
OBJECT_TURNING_POS = [eObjectFacing.north.name, eObjectFacing.east.name,
                      eObjectFacing.south.name, eObjectFacing.west.name]


class eMoveModifier:
    """ Custom class to store x and y pos, so that calling the x and y pos value will be easier."""

    def __init__(self, x_pos, y_pos) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos


# Move modifier value, origin coordinate / (0,0) coordinate is on most
# South West position
MOVE_MODIFIER = {
    eObjectFacing.north.name: eMoveModifier(x_pos=0, y_pos=1),
    eObjectFacing.south.name: eMoveModifier(x_pos=0, y_pos=-1),
    eObjectFacing.east.name: eMoveModifier(x_pos=1, y_pos=0),
    eObjectFacing.west.name: eMoveModifier(x_pos=-1, y_pos=0)
}

# Command List for Command Input
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


# Arrow symbol mapping, used to render html data to visualize object
# position in the table.
DIRECTION_ARROW = {
    eObjectFacing.north.name: '↑',
    eObjectFacing.east.name: '→',
    eObjectFacing.south.name: '↓',
    eObjectFacing.west.name: '←'
}
