# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ..utils.constants import eObjectFacing, OBJECT_TURNING_POS, COMMAND_MAP, ProperPositionException, \
    eMoveModifier, eObjectTurnDirection, MOVE_MODIFIER, check_table_pos

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
    is_placed = fields.Boolean(string='Is robot placed?', default=False)
    is_properly_placed = fields.Boolean(string='Is properly placed (On Table)?', default=False)
    is_reported = fields.Boolean(string='Is report requested', default=False)
    input_cmd = fields.Text(string="Input Command")
    
    @api.depends('x_pos', 'y_pos', 'facing')
    def _compute_report(self):
        for record in self:
            report_value = ""
            # Only report is robot is properly placed on the table
            if record.is_placed and record.is_properly_placed and record.is_reported:
                report_value = '{},{},{}'.format(
                    record.x_pos, record.y_pos,
                    record.facing.upper()
                )

            if record.is_placed and not record.is_properly_placed:
                report_value = '(Robot Position is Outside the Table, Report Ignored)'
                
            record.report = report_value
    
    ########################################################################
    # Movement Function
    ########################################################################
    
    def place_robot(self, is_from_command_input: bool = False, command_place_data : dict = dict()):
        """Place robot on the given location.

        Args:
            is_from_command_input (bool, optional): mark if the command is called from
            text input. Defaults to False.
            command_place_data (dict, optional): position and facing data from
            parsed from text input. Defaults to dict().
        """        
        self.ensure_one()
        self.write({
            'is_placed': True
        })
        # If not from text input / from form input, write inputted position and facing data
        if not is_from_command_input:
            self.write({
                'x_pos': self.x_pos,
                'y_pos': self.y_pos,
                'facing': self.facing
            })
        else:
            self.write(command_place_data)
        
        # Check whether the robot is properly placed on the table or outside the table
        self.write({
            'is_properly_placed': self.check_is_properly_placed()
        })
    
    @check_table_pos
    def move_robot(self):
        """Move robot command.
        First, get the move modifier data, this will contains data to determine
        which coordinate point that needs to be increased or decreased.
        Example :
            Facing is to the North, current pos is 0, 0. If we move north 1 pos
            the coordinate point that needs to be modified is the y_point (add 1 point),
        """        
        self.ensure_one()
        # Get position modifer data, which position that needs to be modified when moving
        move_modifier_data : eMoveModifier = MOVE_MODIFIER.get(self.facing)
        x_pos_modifier = move_modifier_data.x_pos
        y_pos_modifier = move_modifier_data.y_pos
        
        # Apply to data
        self.x_pos = self.x_pos + x_pos_modifier
        self.y_pos = self.y_pos + y_pos_modifier
    
    @check_table_pos
    def turn_robot(self):
        """Turn the robot according to the given turn command, to the left or to the right.

        Raises:
            ValidationError: _description_
        """        
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
    
    @check_table_pos
    def report_location(self):
        """Set report flag to true, this will trigger position and facing data report to be computed.
        """        
        self.ensure_one()
        self.write({
            'is_reported': True
        })
    
    ########################################################################
    # Utils
    ########################################################################
    
    def _check_out_of_bound(self):
        """"
        Avoid robot to move to out of bound area.
        Since the board is 5x5 and coordinate start from 0, so the limit is 4.
        """
        self.ensure_one()
        if self.is_placed and self.is_properly_placed:
            if self.x_pos > 4 or self.x_pos < 0:
                raise ProperPositionException('X Coordinate is out of bound, object would fall.')
            if self.y_pos > 4 or self.y_pos < 0:
                raise ProperPositionException('Y Coordinate is out of bound, object would fall.')
    
    def check_is_properly_placed(self):
        self.ensure_one()
        if self.is_placed:
            if self.x_pos > 4 or self.x_pos < 0:
                return False
            if self.y_pos > 4 or self.y_pos < 0:
                return False
            return True
        return False
