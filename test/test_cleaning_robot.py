from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot


class TestCleaningRobot(TestCase):

    def test_initialize_robot_x_to_0(self):
        robot = CleaningRobot()

        robot.initialize_robot()

        self.assertEqual(robot.pos_x, 0)

    def test_initialize_robot_y_to_0(self):
        robot = CleaningRobot()

        robot.initialize_robot()

        self.assertEqual(robot.pos_y, 0)

    def test_initialize_robot_heading_to_N(self):
        robot = CleaningRobot()

        robot.initialize_robot()

        self.assertEqual(robot.heading, robot.N)

    def test_robot_status(self):
        robot = CleaningRobot()

        robot.initialize_robot()

        self.assertEqual(robot.robot_status(), '(0,0,N)')

