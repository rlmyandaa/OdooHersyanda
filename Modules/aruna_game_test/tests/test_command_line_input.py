# -*- coding: utf-8 -*-

from datetime import datetime
import odoo
from odoo.tests.common import HttpCase, TransactionCase, tagged
from ..models.models import aruna_game_test
from ..utils.constants import eObjectTurnDirection, eObjectFacing, ProperPositionException
from ..wizard.input_command_wizard_model import InputCommandWizard


@tagged('aruna', 'test_command_line_input', '-at_install', 'post_install')
class TestCommandLineInput(TransactionCase):
    def setUp(self):
        super(TestCommandLineInput, self).setUp()
        self.wizard_model: InputCommandWizard = self.env['input.command.wizard']
        self.game_model: aruna_game_test = self.env['aruna_game_test.aruna_game_test']

    def test_1_input_cli_sample_1(self):
        # Test 1 is using sample from this Interview Test Case
        # Input :
        # PLACE 0,0,NORTH
        # MOVE
        # REPORT
        #
        # Output : 0,1,NORTH

        # Create wizard record
        input_cmd = """
        PLACE 0,0,NORTH
        MOVE
        REPORT
        """
        wizard = self.wizard_model.create({
            'input_cmd': input_cmd
        })
        result = wizard.execute_input()

        # Get output game record
        game_id = result.get('res_id')
        game_record = self.game_model.browse(game_id)

        # Check result data
        self.assertEqual(game_record.x_pos, 0)
        self.assertEqual(game_record.y_pos, 1)
        self.assertEqual(game_record.facing, eObjectFacing.north.name)

        # Check report data
        report_data = game_record.report
        report_should_be = '{},{},{}'.format(
            0, 1, eObjectFacing.north.name.upper())
        self.assertEqual(report_data, report_should_be)

    def test_2_input_cli_sample_2(self):
        # Test 1 is using sample from this Interview Test Case
        # Input :
        # PLACE 0,0,NORTH
        # LEFT
        # REPORT
        #
        # Output : 0,1,WEST

        # Create wizard record
        input_cmd = """
        PLACE 0,0,NORTH
        LEFT
        REPORT
        """
        wizard = self.wizard_model.create({
            'input_cmd': input_cmd
        })
        result = wizard.execute_input()

        # Get output game record
        game_id = result.get('res_id')
        game_record = self.game_model.browse(game_id)

        # Check result data
        self.assertEqual(game_record.x_pos, 0)
        self.assertEqual(game_record.y_pos, 0)
        self.assertEqual(game_record.facing, eObjectFacing.west.name)

        # Check report data
        report_data = game_record.report
        report_should_be = '{},{},{}'.format(
            0, 0, eObjectFacing.west.name.upper())
        self.assertEqual(report_data, report_should_be)

    def test_3_input_cli_sample_3(self):
        # Test 1 is using sample from this Interview Test Case
        # Input :
        # PLACE 1,2,EAST
        # MOVE
        # MOVE
        # LEFT
        # MOVE
        # REPORT
        #
        # Output : 3,3,NORTH

        # Create wizard record
        input_cmd = """
        PLACE 1,2,EAST
        MOVE
        MOVE
        LEFT
        MOVE
        REPORT
        """
        wizard = self.wizard_model.create({
            'input_cmd': input_cmd
        })
        result = wizard.execute_input()

        # Get output game record
        game_id = result.get('res_id')
        game_record = self.game_model.browse(game_id)

        # Check result data
        self.assertEqual(game_record.x_pos, 3)
        self.assertEqual(game_record.y_pos, 3)
        self.assertEqual(game_record.facing, eObjectFacing.north.name)

        # Check report data
        report_data = game_record.report
        report_should_be = '{},{},{}'.format(
            3, 3, eObjectFacing.north.name.upper())
        self.assertEqual(report_data, report_should_be)
