from odoo import models, fields
from odoo.exceptions import ValidationError
from ..utils.constants import COMMAND_MAP, OBJECT_TURNING_POS
from ..utils.exceptions import TestingException
from ..models.models import aruna_game_test


class InputCommandWizard(models.TransientModel):
    _name = 'input.command.wizard'
    _description = 'Input Command Wizard'

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
            raise ValidationError(
                'Valid Place Command is "PLACE POS_X,POS_Y,FACING"')

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
            raise ValidationError(
                'Invalid Facing Direction "{}"'.format(facing))
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
        game_model: aruna_game_test = self.env['aruna_game_test.aruna_game_test']
        game_data = game_model.create({})

        # Trim input, and split per line by line
        string_command = self.input_cmd.strip()
        command_list = string_command.splitlines()

        # Counter for first valid place command, all command before
        # place should be discarded
        is_place_found = False

        # initial position data for error purpose
        initial_x_pos = game_data.x_pos
        initial_y_pos = game_data.y_pos
        initial_facing = game_data.facing

        # Loop through command
        for index, cmd in enumerate(command_list):
            try:
                # Trim command for whitespace
                cmd = cmd.strip()
                # Check if current command is the place command
                if 'PLACE ' in cmd.upper():
                    place_data = self._decode_place_command(cmd.upper())
                    game_data.place_robot(
                        is_from_command_input=True,
                        command_place_data=place_data)
                    is_place_found = True

                # Only execute if place command is found
                elif is_place_found:
                    # Get command data
                    command_data = COMMAND_MAP.get(cmd.upper())
                    if not command_data:
                        raise ValidationError(
                            'Invalid command "{}"'.format(cmd))

                    # Get function name and context data
                    func_name = command_data.get('func')
                    context_data = command_data.get('context') or dict()

                    # Save initial position data for error purpose
                    initial_x_pos = game_data.x_pos
                    initial_y_pos = game_data.y_pos
                    initial_facing = game_data.facing

                    # Execute command
                    func = getattr(
                        game_data.with_context(context_data), func_name)
                    func()
                elif not is_place_found and not COMMAND_MAP.get(cmd.upper()):
                    # Build error message
                    msg_1 = 'Invalid command "{}"'.format(cmd)
                    msg_2 = ''

                    # In case the error is place command
                    if 'place' in cmd.lower():
                        msg_1 += '\n'
                        msg_2 = 'Place command should be "PLACE X_POS,Y_POS,FACING", \
                            separate "PLACE" and position data with space.'
                    msg = msg_1 + msg_2
                    raise ValidationError(msg)

            except Exception as e:
                # Build error message
                line = index + 1
                error_msg_1 = 'Error on Command at Line {} ({}) \n'.format(
                    line, cmd)
                error_msg_reason = 'Reason: {}\n'.format(e.name)
                error_msg_pos_head_before_error = '\n\nPosition before Error: {},{},{}\n'.format(
                    initial_x_pos, initial_y_pos, initial_facing.upper())
                error_msg_pos_head_at_error = 'Position at Error: {},{},{}'.format(
                    game_data.x_pos, game_data.y_pos, game_data.facing.upper())
                error_msg = error_msg_1 + error_msg_reason + \
                    error_msg_pos_head_before_error + error_msg_pos_head_at_error

                # In case for testing purpose
                if self.env.context.get('is_testing'):
                    error_data = {
                        'line': line, 'command': cmd, 'reason': e.name, 'position_before_error': [
                            initial_x_pos, initial_y_pos, initial_facing.upper()], 'position_at_error': [
                            game_data.x_pos, game_data.y_pos, game_data.facing.upper()]}
                    raise TestingException(error_data)

                raise ValidationError(error_msg)

        return {
            'name': ('Aruna Odoo Test'),
            'type': 'ir.actions.act_window',
            'res_model': 'aruna_game_test.aruna_game_test',
            'view_mode': 'form',
            'res_id': game_data.id
        }
