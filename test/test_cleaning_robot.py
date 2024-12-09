from unittest import TestCase
from unittest.mock import Mock, patch, call

from mock import GPIO
from mock.ibs import IBS
from src.cleaning_robot import CleaningRobot, CleaningRobotError


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

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_turn_off_the_cleaning_system_turn_on_the_led_when_battery_lower_equal_10(self, mock_ibs: Mock,
                                                                                    mock_gpio: Mock):
        mock_ibs.return_value = 10
        robot = CleaningRobot()
        robot.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(robot.CLEANING_SYSTEM_PIN, GPIO.LOW), call(robot.RECHARGE_LED_PIN, GPIO.HIGH)])

    @patch.object(GPIO, "output")
    @patch.object(IBS, "get_charge_left")
    def test_turn_on_the_cleaning_system_turn_off_the_led_when_battery_greater_10(self, mock_ibs: Mock,
                                                                                        mock_gpio: Mock):
        mock_ibs.return_value = 11
        robot = CleaningRobot()
        robot.manage_cleaning_system()
        mock_gpio.assert_has_calls([call(robot.CLEANING_SYSTEM_PIN, GPIO.HIGH), call(robot.RECHARGE_LED_PIN, GPIO.LOW)])

    def test_execute_command_move_forward_heading_N(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.execute_command(robot.FORWARD)
        self.assertEqual(robot.robot_status(), '(0,1,N)')

    def test_execute_command_move_forward_heading_E(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.E
        robot.execute_command(robot.FORWARD)
        self.assertEqual(robot.robot_status(), '(1,0,E)')

    def test_execute_command_move_forward_heading_W(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.W
        robot.execute_command(robot.FORWARD)
        self.assertEqual(robot.robot_status(), '(-1,0,W)')

    def test_execute_command_move_forward_heading_S(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.S
        robot.execute_command(robot.FORWARD)
        self.assertEqual(robot.robot_status(), '(0,-1,S)')

    def test_execute_command_rotate_left_from_N(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.execute_command(robot.LEFT)
        self.assertEqual(robot.robot_status(), '(0,0,W)')

    def test_execute_command_rotate_left_from_W(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.W
        robot.execute_command(robot.LEFT)
        self.assertEqual(robot.robot_status(), '(0,0,S)')

    def test_execute_command_rotate_left_from_S(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.S
        robot.execute_command(robot.LEFT)
        self.assertEqual(robot.robot_status(), '(0,0,E)')

    def test_execute_command_rotate_left_from_E(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.E
        robot.execute_command(robot.LEFT)
        self.assertEqual(robot.robot_status(), '(0,0,N)')

    def test_execute_command_rotate_right_from_N(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.execute_command(robot.RIGHT)
        self.assertEqual(robot.robot_status(), '(0,0,E)')

    def test_execute_command_rotate_right_from_E(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.E
        robot.execute_command(robot.RIGHT)
        self.assertEqual(robot.robot_status(), '(0,0,S)')

    def test_execute_command_rotate_right_from_S(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.S
        robot.execute_command(robot.RIGHT)
        self.assertEqual(robot.robot_status(), '(0,0,W)')

    def test_execute_command_rotate_right_from_W(self):
        robot = CleaningRobot()
        robot.initialize_robot()
        robot.heading = robot.W
        robot.execute_command(robot.RIGHT)
        self.assertEqual(robot.robot_status(), '(0,0,N)')

    @patch.object(GPIO, "input")
    def test_obstacle_found_should_not_move_and_return_obstacle_position(self, mock_input):
        mock_input.return_value = True
        robot = CleaningRobot()
        robot.initialize_robot()
        self.assertEqual(robot.execute_command(robot.FORWARD), '(0,0,N),(0,1)')