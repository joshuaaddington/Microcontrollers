import sys
from machine import Pin, PWM

class StepperMotor:
    """Class to control a stepper motor using an A4988 driver."""
    
    VALID_MICROSTEPS = {1, 2, 4, 8, 16}  # Define valid step sizes
    
    def __init__(self, stepPin=None, dirPin=None, disablePin=None, homingPin=None, counterPin=None):
        """
        Initialize the StepperMotor with stepping pin, direction pin, disable pin, and optional homing pin.

        :param homingPin: GPIO pin used for homing (default: None)
        """
        if stepPin is None or dirPin is None or disablePin is None:
            print("ERROR: Pins not fully declared")
            sys.exit(1)
        self.currentPosition = None  # Current step position
        self.currentSpeed = None
        self.homingPin = homingPin  # Homing pin (optional)
        self.stepDivider = 1  # Default to full step mode
        self.MAX_RPM = 600 # Maximum RPM for the motor
        self.direction = 1  # Default direction is positive

        # Initialize pins
        self.stepPin = Pin(stepPin, Pin.OUT)
        self.stepPin.value(0)
        self.dirPin = Pin(dirPin, Pin.OUT)
        self.dirPin.value(1)
        self.disablePin = Pin(disablePin, Pin.OUT)
        self.disablePin.value(1)
        if self.homingPin is not None:
            Pin(self.homingPin, Pin.IN, Pin.PULL_UP)

    def enableMotor(self):
        """Enable the motor by setting the disable pin to low."""
        self.disablePin.value(0)
        print("Motor enabled")
    
    def disableMotor(self):
        """Disable the motor by setting the disable pin to high."""
        Pin(self.disablePin, Pin.OUT).value(1)
        print("Motor disabled")

    def reverseDirections(self):
        """Reverse the motor direction defaults."""
        self.direction = -self.direction
        print("Motor direction reversed")

    def setMicroStep(self, stepDivider):
        """
        Set the microstepping mode.

        stepDivider: Must be 1, 2, 4, 8, or 16
        """
        if stepDivider not in self.VALID_MICROSTEPS:
            print(f"Error: stepDivider {stepDivider} is not a valid quantity")
            sys.exit(1)  # Exit with an error
        self.stepDivider = stepDivider
        print(f"Microstepping set to {stepDivider}. Microstepping must be set on the physical driver as well!!")

    def step(self, steps):
        """
        Move the motor by a certain number of steps.

        :param steps: Number of steps to move (positive or negative)
        """
        if steps > 0:
            Pin(self.dirPin, Pin.OUT).value(self.direction)
            for _ in range(abs(steps)):
                Pin(self.stepPin, Pin.OUT).value(1)
                Pin(self.stepPin, Pin.OUT).value(0)
        if steps < 0:
            Pin(self.dirPin, Pin.OUT).value(-self.direction)
            for _ in range(abs(steps)):
                self.stepPin.value(1)
                self.stepPin.value(0)
        self.position += steps*self.direction
            
        print(f"Motor moved {steps} steps. New position: {self.position}")
        
    def setSpeed(self, rpm):
        """
        Set the motor speed in revolutions per minute (RPM).
        
        :param rpm: Speed in RPM (positive or negative)
        """        
        # Convert RPM to Hz
        steps_per_revolution = 200 * self.stepDivider  # Assuming a 1.8° stepper (200 steps/full rotation)
        self.speed = (rpm * steps_per_revolution) / 60  # Convert RPM to steps/sec
        
        # Check if speed exceeds maximum
        if self.speed > self.MAX_RPM * steps_per_revolution / 60:
            print(f"Error: Speed {rpm} RPM exceeds max speed ({self.MAX_RPM} rotations/min)")
            sys.exit(1)
        
        # Turn on PWM and set direction
        pwm = PWM(Pin(self.stepPin), duty_u16 = 32768)
        pwm.freq(int(self.speed))
        if rpm*self.direction < 0:
            self.dirPin.value(1)
        else:
            self.dirPin.value(0)

        # Update current speed
        self.currentSpeed = rpm

        # Debug Statement
        print(f"Speed set to {rpm} RPM ({self.speed:.2f} steps per second)")

    def homeMotorReverse(self, speed = -60):
        """
        Perform a homing sequence if a homing pin is set.
        """
        if self.homingPin is None:
            print("Error: No homing pin configured.")
            return
        print(f"Homing motor using pin {self.homingPin}...")
        self.setSpeed(speed)
        self.position = 0  # Reset position
        print("Motor homed successfully.")

    def homeMotorForward(self, speed = 60):
        """
        Perform a homing sequence if a homing pin is set.
        """
        if self.homingPin is None:
            print("Error: No homing pin configured.")
            return
        print(f"Homing motor using pin {self.homingPin}...")
        self.position = 0  # Reset position
        print("Motor homed successfully.")

motor = StepperMotor(stepPin = 17, dirPin = 16, disablePin = 7, homingPin = 4)
motor.enableMotor()
motor.setMicroStep(8)
motor.setSpeed(300)