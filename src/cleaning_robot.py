import time
from getpass import win_getpass

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import board
    import IBS
    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.board as board
    import mock.ibs as IBS


class CleaningRobot:

    RECHARGE_LED_PIN = 12
    CLEANING_SYSTEM_PIN = 13
    INFRARED_PIN = 15

    # Wheel motor pins
    PWMA = 16
    AIN2 = 18
    AIN1 = 22

    # Rotation motor pins
    BIN1 = 29
    BIN2 = 31
    PWMB = 32
    STBY = 33

    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    LEFT = 'l'
    RIGHT = 'r'
    FORWARD = 'f'

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN, GPIO.IN)
        GPIO.setup(self.RECHARGE_LED_PIN, GPIO.OUT)
        GPIO.setup(self.CLEANING_SYSTEM_PIN, GPIO.OUT)

        GPIO.setup(self.PWMA, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.PWMB, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.STBY, GPIO.OUT)

        ic2 = board.I2C()
        self.ibs = IBS.IBS(ic2)

        self.pos_x = None
        self.pos_y = None
        self.heading = None

        self.recharge_led_on = False
        self.cleaning_system_on = False

        self.goingBackToRechargeStation = False

    def initialize_robot(self) -> None:
        self.pos_x = 0
        self.pos_y = 0
        self.heading = self.N

    def robot_status(self) -> str:
        return f"({self.pos_x},{self.pos_y},{self.heading})"

    def execute_command(self, command: str) -> str:
        if self.ibs.get_charge_left() <= 10:
            self.manage_cleaning_system()
            return '!'+self.robot_status()
        if self.ibs.get_charge_left() <= 24 and not self.goingBackToRechargeStation:
            self.goingBackToRechargeStation = True
            self.go_to_recharge_station()
        else:
            newPosX = self.pos_x
            newPosY = self.pos_y
            if command == self.FORWARD:
                self.activate_wheel_motor()
                if self.heading == self.N:
                    newPosY = self.pos_y + 1
                if self.heading == self.E:
                    newPosX = self.pos_x + 1
                if self.heading == self.W:
                    newPosX = self.pos_x - 1
                if self.heading == self.S:
                    newPosY = self.pos_y - 1
                if not self.obstacle_found():
                    self.pos_x = newPosX
                    self.pos_y = newPosY
                else:
                    return self.robot_status() + f',({newPosX},{newPosY})'
            else:
                if command == self.LEFT:
                    if self.heading == self.N:
                        self.heading = self.W
                    elif self.heading == self.W:
                        self.heading = self.S
                    elif self.heading == self.S:
                        self.heading = self.E
                    elif self.heading == self.E:
                        self.heading = self.N
                else:
                    if self.heading == self.N:
                        self.heading = self.E
                    elif self.heading == self.E:
                        self.heading = self.S
                    elif self.heading == self.S:
                        self.heading = self.W
                    elif self.heading == self.W:
                        self.heading = self.N
                    self.activate_rotation_motor(command)
            return self.robot_status()

    def obstacle_found(self) -> bool:
        return GPIO.input(self.INFRARED_PIN)

    def go_to_recharge_station(self):
        if self.pos_x > 0:
            while self.heading != self.W:
                self.execute_command(self.LEFT)
            while self.pos_x != 0:
                status = self.execute_command(self.FORWARD)
                if status == self.robot_status() + f',({self.pos_x - 1},{self.pos_y})':
                    raise CleaningRobotError()
        elif self.pos_x < 0:
            while self.heading != self.E:
                self.execute_command(self.RIGHT)
            while self.pos_x != 0:
                status = self.execute_command(self.FORWARD)
                if status == self.robot_status() + f',({self.pos_x + 1},{self.pos_y})':
                    raise CleaningRobotError()
        if self.pos_y > 0:
            while self.heading != self.S:
                self.execute_command(self.LEFT)
            while self.pos_y != 0:
                status = self.execute_command(self.FORWARD)
                if status == self.robot_status() + f',({self.pos_x},{self.pos_y - 1})':
                    raise CleaningRobotError()
        elif self.pos_y < 0:
            while self.heading != self.N:
                self.execute_command(self.RIGHT)
            while self.pos_y != 0:
                status = self.execute_command(self.FORWARD)
                if status == self.robot_status() + f',({self.pos_x},{self.pos_y + 1})':
                    raise CleaningRobotError()
        while self.heading != self.E:
            self.execute_command(self.LEFT)

    def manage_cleaning_system(self) -> None:
        if self.ibs.get_charge_left() <= 10:
            GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.LOW)
            GPIO.output(self.RECHARGE_LED_PIN, GPIO.HIGH)
            self.cleaning_system_on = False
            self.recharge_led_on = True
        else:
            GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.HIGH)
            GPIO.output(self.RECHARGE_LED_PIN, GPIO.LOW)
            self.cleaning_system_on = True
            self.recharge_led_on = False

    def activate_wheel_motor(self) -> None:
        """
        Let the robot move forward by activating its wheel motor
        """
        # Drive the motor clockwise
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # Set the motor speed
        GPIO.output(self.PWMA, GPIO.HIGH)
        # Disable STBY
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT: # Sleep only if you are deploying on the actual hardware
            time.sleep(1) # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.PWMA, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)

    def activate_rotation_motor(self, direction) -> None:
        """
        Let the robot rotate towards a given direction
        :param direction: "l" to turn left, "r" to turn right
        """
        if direction == self.LEFT:
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
        elif direction == self.RIGHT:
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)

        GPIO.output(self.PWMB, GPIO.HIGH)
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)
        GPIO.output(self.PWMB, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)


class CleaningRobotError(Exception):
    pass
