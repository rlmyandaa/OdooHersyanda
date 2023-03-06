# -*- coding: utf-8 -*-

from datetime import datetime
import odoo
from odoo.tests.common import HttpCase, TransactionCase, tagged
from ..models.models import aruna_game_test
from ..utils.constants import eObjectTurnDirection, eObjectFacing, ProperPositionException

@tagged('aruna', 'test_positioning', '-at_install', 'post_install')
class TestPositioning(TransactionCase):
    def setUp(self):
        super(TestPositioning, self).setUp()
        base_model : aruna_game_test = self.env['aruna_game_test.aruna_game_test']
        self.base_game = base_model.create({
            'x_pos': 0,
            'y_pos': 0,
            'facing': eObjectFacing.north.name
        })
    
    def test_1_placing_object(self):
        # The first valid command is PLACE command, any command before PLACE command will
        # be discarded, in other word while not is_placed, any movement command will be ignored.
        
        # Give some movement, currently object is not placed yet, any movement should
        # be ignored
        self.base_game.move_robot()
        self.base_game.with_context(turn_direction=eObjectTurnDirection.right.value).turn_robot()
        # Check, should not change anything
        self.assertEqual(self.base_game.x_pos, 0)
        self.assertEqual(self.base_game.y_pos, 0)
        self.assertEqual(self.base_game.facing, eObjectFacing.north.name)
        
        # Now, call place command. If the object is placed within valid table boundary (5x5 board),
        # all valid movement command should be executed.
        self.base_game.place_robot()
        
        # Now try to move robot again
        # The initial position is 0,0 and facing to north.
        # After first move, position should be 0,1
        # Then after turning right, the new facing should be east
        self.base_game.move_robot()
        self.base_game.with_context(turn_direction=eObjectTurnDirection.right.name).turn_robot()
        
        # Check
        self.assertEqual(self.base_game.x_pos, 0)
        self.assertEqual(self.base_game.y_pos, 1)
        self.assertEqual(self.base_game.facing, eObjectFacing.east.name)
    
    def test_2_avoid_object_falling(self):
        # While object is within table boundary, we should avoid any movement command
        # that would make object fall off the table.
        # Let's initialize robot first to 0,0,SOUTH position.
        # Then try to move 1 point ahead, alert should be triggered since object would fall
        # if it move forward.
        # |  |  |  |  |  | 
        # |  |  |  |  |  |
        # |  |  |  |  |  |
        # |  |  |  |  |  |
        # |V |  |  |  |  | -> object would fall if move forward
        
        # Set object place
        self.base_game.write({
            'x_pos': 0,
            'y_pos': 0,
            'facing': eObjectFacing.south.name
        })
        self.base_game.place_robot()
        # Try to move forward, should trigger exception
        with self.assertRaises(ProperPositionException):
            self.base_game.move_robot()
        
        # Try to turn object to right, so it will face to west, then try to move forward.
        # Since the object would also fall if move forward in this position and facing,
        # alert should be triggered.
        # |  |  |  |  |  | 
        # |  |  |  |  |  |
        # |  |  |  |  |  |
        # |  |  |  |  |  |
        # |< |  |  |  |  | -> object would fall if move forward
        self.base_game.with_context(turn_direction=eObjectTurnDirection.right.name).turn_robot()
        # Check direction
        self.assertEqual(self.base_game.facing, eObjectFacing.west.name)
        
        # Try to move forward again, should trigger exception
        with self.assertRaises(ProperPositionException):
            self.base_game.move_robot()
        

    def test_3_placing_out_of_bound_area(self):
        # If placed in out of bound area, report should not be shown.
        # The status should be is_placed but not is_properly_placed.
        # All movement command should be able to executed when on out off bound are,
        # but won't affect anything.
        
        # Place it in out off bound area
        self.base_game.write({
            'x_pos': -5,
            'y_pos': -5
        })
        self.base_game.place_robot()
        
        self.assertTrue(self.base_game.is_placed)
        self.assertFalse(self.base_game.is_properly_placed)
        self.assertEqual(self.base_game.report, '(Robot Position is Outside the Table, Report Ignored)')
        
    def test_4_placing_out_of_bound_area_with_movement(self):
        # All movement command should be able to executed when on out off bound are,
        # but won't affect anything.
        # Place it in out off bound area
        self.base_game.write({
            'x_pos': -5,
            'y_pos': -5
        })
        self.base_game.place_robot()
        self.base_game.move_robot()
        self.base_game.move_robot()
        self.base_game.move_robot()
        self.base_game.with_context(turn_direction='right').turn_robot()
        
        # Check position
        self.assertEqual(self.base_game.x_pos, -5)
        self.assertEqual(self.base_game.y_pos, -5)
        self.assertEqual(self.base_game.facing, 'north')
