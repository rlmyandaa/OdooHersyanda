from email.policy import default
from odoo import models, fields, exceptions
from odoo.exceptions import ValidationError
from ..utils.constants import COMMAND_MAP, OBJECT_TURNING_POS
from ..models.models import aruna_game_test


class InputCommandWizard(models.TransientModel):
    _name = 'input.command.wizard'
    _description = 'Input Command Wizaard'

    input_cmd = fields.Text(string="Input Command")

    def _decode_place_command(self, place_command: str) -> dict:
        """Decode place command to get position and facing data.

        Args:
            place_command (str): place command text input
        """        
        # Remove all whitespace
        place_command = place_command.replace(" ", "")
        place_command = place_command.replace("PLACE", "")
        
        # Split command
        place_cmd_list = place_command.strip().split(',')
        
        # Check command list
        if len(place_cmd_list) != 3:
            raise ValidationError('Valid Place Command is "PLACE POS_X,POS_Y,FACING"')
        
        # Validate Position and Facing Data
        # Validate position
        place_data = dict()
        try:
            x_pos = int(place_cmd_list[0])
            place_data['x_pos'] = x_pos
        except ValueError:
            raise ValidationError('X_POS should be a integer number')
        
        try:
            y_pos = int(place_cmd_list[1])
            place_data['y_pos'] = y_pos
        except ValueError:
            raise ValidationError('Y_POS should be a integer number')
        
        # Validate facing data
        facing = place_cmd_list[2].lower()
        if not isinstance(facing, str) or facing not in OBJECT_TURNING_POS:
            raise ValidationError('Invalid Facing Direction "{}"'.format(facing))
        place_data['facing'] = facing
        
        return place_data
    
    def execute_input(self):
        """Execute command from given text input.
        Valid command are:
        PLACE x_pos, y_pos, facing
        MOVE
        LEFT
        RIGHT
        REPORT

        Raises:
            ValidationError: _description_
        """        
        self.ensure_one()
        
        # Initialize game model
        game_model : aruna_game_test = self.env['aruna_game_test.aruna_game_test']
        game_data = game_model.create({})
        
        # Trim input, and split per line by line
        string_command = self.input_cmd.strip()
        command_list = string_command.splitlines()
        
        # Counter for first valid place command, all command before
        # place should be discarded
        is_place_found = False
        
        # Loop through command
        for cmd in command_list:
            # Check if current command is the place command
            if 'PLACE' in cmd.upper():
                place_data = self._decode_place_command(cmd.upper())
                game_data.place_robot(is_from_command_input=True, command_place_data=place_data)
                is_place_found = True
            
            # Only execute if place command is found
            elif is_place_found:
                # Get command data
                command_data = COMMAND_MAP.get(cmd.upper())
                if not command_data:
                    raise ValidationError('Invalid command "{}"'.format(cmd))
                
                # Get function name and context data
                func_name = command_data.get('func')
                context_data = command_data.get('context') or dict()
                
                # Execute command
                func = getattr(game_data.with_context(context_data), func_name)
                func()
        
        return {
            'name': ('Test Wizard'),

            'type': 'ir.actions.act_window',

            'res_model': 'aruna_game_test.aruna_game_test',

            'view_mode': 'form',

            'res_id': game_data.id
        }