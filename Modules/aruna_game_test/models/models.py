# -*- coding: utf-8 -*-

from odoo import models, fields, api
from enum import Enum, auto

from odoo.exceptions import ValidationError

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


# Move modifier value, origin coordinate / (0,0) coordinate is on most South West position
MOVE_MODIFIER = {
    eObjectFacing.north.name: eMoveModifier(x_pos=0, y_pos=1),
    eObjectFacing.south.name: eMoveModifier(x_pos=0, y_pos=-1),
    eObjectFacing.east.name: eMoveModifier(x_pos=1, y_pos=0),
    eObjectFacing.west.name: eMoveModifier(x_pos=-1, y_pos=0)
}


class aruna_game_test(models.Model):
    _name = 'aruna_game_test.aruna_game_test'
    _description = 'Aruna Odoo Interview Test'

    x_pos = fields.Integer(string='X Coordinate', default=0)
    y_pos = fields.Integer(string='Y Coordinate', default=0)
    facing = fields.Selection(
        selection=[
            (eObjectFacing.north.name, 'NORTH'),
            (eObjectFacing.east.name, 'EAST'),
            (eObjectFacing.south.name, 'SOUTH'),
            (eObjectFacing.west.name, 'WEST')
        ],
        string="Object Facing / Direction",
        default=eObjectFacing.north.name
    )
    report = fields.Text(string='Position Report', compute='_compute_report')

    @api.depends('x_pos', 'y_pos', 'facing')
    def _compute_report(self):
        for record in self:
            report_value = '{},{},{}'.format(
                record.x_pos, record.y_pos,
                record.facing.upper()
            )
            record.report = report_value

    
    @api.constrains('x_pos', 'y_pos')
    def _restrict_out_of_bound_coordinate(self):
        """" Avoid robot to move to out of bound area. """
        for record in self:
            if record.x_pos > 5 or record.x_pos < 0:
                raise ValidationError('X Coordinate is out of bound, object would fall.')
            if record.y_pos > 5 or record.y_pos < 0:
                raise ValidationError('Y Coordinate is out of bound, object would fall.')
    
    def place_robot(self):
        self.ensure_one()
        self.write({})
    
    def move_robot(self):
        self.ensure_one()
        # Get position modifer data, which position that needs to be modified when moving
        move_modifier_data : eMoveModifier = MOVE_MODIFIER.get(self.facing)
        x_pos_modifier = move_modifier_data.x_pos
        y_pos_modifier = move_modifier_data.y_pos
        
        # Apply to data
        self.x_pos = self.x_pos + x_pos_modifier
        self.y_pos = self.y_pos + y_pos_modifier
    
    def turn_robot(self):
        self.ensure_one()
        # Validate direction
        direction = self.env.context.get('turn_direction', False)
        
        if direction not in [eObjectTurnDirection.left.name, eObjectTurnDirection.right.name]:
            raise ValidationError('Unknown turning direction.')
        
        # Get turn value to get correct heading when robot is turning,
        # example when current heading is to West, if we move right the heading should be the North.
        # Notes that OBJECT_TURNING_POS list is specifically aranged to handle moving from left to right according to the index.
        # Example if current position is West and we are moving to the right, so the next correct heading will be the list after the current heading index.
        current_facing_index = OBJECT_TURNING_POS.index(self.facing)
        turn_value = -1
        if direction == eObjectTurnDirection.right.name:
            turn_value = 1
        
        # Write correct new facing direction
        new_facing_index = current_facing_index + turn_value
        if new_facing_index > len(OBJECT_TURNING_POS) - 1:
            new_facing_index = 0
        new_facing_direction = OBJECT_TURNING_POS[new_facing_index]
        self.facing = new_facing_direction
