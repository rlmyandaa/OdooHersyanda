# -*- coding: utf-8 -*-

from datetime import datetime
from distutils.log import error
from xml.dom import ValidationErr
import odoo
from odoo.tests.common import HttpCase, TransactionCase, tagged
from ..models.models import aruna_game_test
from ..utils.constants import eObjectTurnDirection, eObjectFacing, ProperPositionException, TestingException
from ..wizard.input_command_wizard_model import InputCommandWizard
from odoo.exceptions import ValidationError
from ..utils.test_utils import execute_wizard_cli

@tagged('aruna', 'test_negative_command_line_input', '-at_install', 'post_install')
class TestCommandLineInput(TransactionCase):
    def setUp(self):
        super(TestCommandLineInput, self).setUp()
        # Set context is_testing = True so that we could get error message in dictionary format using
        # TestingException
        self.wizard_model: InputCommandWizard = self.env['input.command.wizard'].with_context(is_testing=True)
        self.game_model: aruna_game_test = self.env['aruna_game_test.aruna_game_test']

    def test_1_error_place_command(self):
        # Test error in place command
        # A valid place command is "PLACE <space>X_POS,Y_POS,FACING"
        
        # Test error when using x and y pos that is not integer
        input_cmd = """
        PLACE A,B,NORTH
        """
        with self.assertRaises(TestingException):
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        # Check error message
        try:
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        except TestingException as err:
            # Check reason
            reason = 'X_POS should be a integer number'
            self.assertEqual(reason, err.error_data.get('reason'))
            
            # Check which line that trigger error
            self.assertEqual(1, err.error_data.get('line'))
    
    def test_2_error_command_at_a_line(self):
        # Test detect which line that trigger error in a command list
        # Should output line 4 since GHJ is unknown command
        input_cmd = """
        PLACE 1,2,NORTH
        MOVE
        MOVE
        GHJ
        LEFT
        """
        with self.assertRaises(TestingException):
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        # Check error message
        try:
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        except TestingException as err:
            # Check which line that trigger error
            self.assertEqual(4, err.error_data.get('line'))
    
    def test_3_error_when_navigating_the_table(self):
        # Test detect at which line the robot moving is no longer valid.
        # It's not valid when a command is trying to make the robot fall off the table.
        # The command will be:
        input_cmd = """
        PLACE 0,0,EAST
        MOVE
        MOVE
        MOVE
        MOVE
        MOVE
        LEFT
        REPORT
        """
        # The 5th MOVE will trigger error since before the move the pos will be 4,0,EAST,
        # and if we move forward the robot will fall off the table.
        # This should output line 6 as the source of error
        with self.assertRaises(TestingException):
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        # Check error message
        try:
            result = execute_wizard_cli(self, self.wizard_model, input_cmd)
        except TestingException as err:
            # Check which line that trigger error
            self.assertEqual(6, err.error_data.get('line'))
            # Check the position before the object would fall, should be 4,0,EAST
            self.assertEqual([4,0,eObjectFacing.east.name.upper()], err.error_data.get('position_before_error'))
            # Check the position when error is triggered / when the object is falling due to moving forward
            self.assertEqual([5,0,eObjectFacing.east.name.upper()], err.error_data.get('position_at_error'))
    
        
        
        
            