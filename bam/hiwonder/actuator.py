import numpy as np
from bam.message import yellow, print_parameter, bright
from bam.actuator import VoltageControlledActuator
from bam.parameter import Parameter
from bam.testbench import Testbench, Pendulum


class HiwonderBusServoActuator(VoltageControlledActuator):
    """
    Hiwonder bus servo actuator (e.g., LX-16A, LX-15D, LD-27MG)

    These servos use serial bus communication and support position, speed, and torque control.
    Common specifications:
    - Operating voltage: 4.8V - 8.4V (typically 6V - 7.4V)
    - Protocol: Half-duplex serial communication
    - Position resolution: 1000 steps (0-1000)
    - Speed control available
    """

    def __init__(self, testbench_class: Testbench, voltage: float = 6.0):
        """
        Initialize Hiwonder bus servo actuator.

        Args:
            testbench_class: The testbench class to use (typically Pendulum)
            voltage: Operating voltage (default: 6.0V, typical for LX-16A/LX-15D)
        """
        super().__init__(
            testbench_class,
            vin=voltage,
            kp=32.0,
            # Error gain: This needs to be determined experimentally with oscilloscope
            # For Hiwonder servos, this is an initial estimate
            error_gain=0.15,
            # Maximum PWM duty cycle
            max_pwm=0.95
        )

    def initialize(self):
        """
        Initialize model parameters for Hiwonder bus servos.
        These initial values should be refined through the fitting process.
        """
        # Torque constant [Nm/A] or [V/(rad/s)]
        # These values are estimates and should be fitted from data
        self.model.kt = Parameter(0.8, 0.1, 2.5)

        # Motor resistance [Ohm]
        self.model.R = Parameter(2.5, 0.5, 8.0)

        # Motor armature / apparent inertia [kg m^2]
        # Bus servos typically have smaller rotors
        self.model.armature = Parameter(0.002, 0.0001, 0.02)

    def get_extra_inertia(self) -> float:
        """Return the rotor inertia."""
        return self.model.armature.value


class HiwonderHTD45HActuator(HiwonderBusServoActuator):
    """
    Hiwonder HTD-45H servo (high-torque 12V model)

    Specifications:
    - Voltage: 12V (required)
    - Torque: ~45 kg·cm @ 12V
    - Higher power industrial servo
    - Metal gears
    """

    def __init__(self, testbench_class: Testbench):
        super().__init__(testbench_class, voltage=12.0)

    def initialize(self):
        super().initialize()
        # Refine parameters specific to HTD-45H
        self.model.kt = Parameter(4.4, 2.0, 8.0)  # Based on ~45 kg·cm torque
        self.model.R = Parameter(3.5, 1.5, 8.0)
        self.model.armature = Parameter(0.008, 0.002, 0.025)


class HiwonderLX16AActuator(HiwonderBusServoActuator):
    """
    Hiwonder LX-16A servo (common hobby model)

    Specifications:
    - Voltage: 4.8V - 8.4V (6V recommended)
    - Torque: ~1.6 kg·cm @ 6V
    - Speed: ~0.12 sec/60° @ 6V
    - Weight: 16.5g
    """

    def __init__(self, testbench_class: Testbench):
        super().__init__(testbench_class, voltage=6.0)

    def initialize(self):
        super().initialize()
        # Refine parameters specific to LX-16A
        self.model.kt = Parameter(0.157, 0.05, 0.5)  # Based on ~1.6 kg·cm torque
        self.model.R = Parameter(3.0, 1.0, 6.0)
        self.model.armature = Parameter(0.0015, 0.0005, 0.008)


class HiwonderLD27MGActuator(HiwonderBusServoActuator):
    """
    Hiwonder LD-27MG servo (higher torque model)

    Specifications:
    - Voltage: 6V - 8.4V (7.4V recommended)
    - Torque: ~27 kg·cm @ 7.4V
    - Speed: ~0.16 sec/60° @ 7.4V
    - Weight: 60g
    - Metal gears
    """

    def __init__(self, testbench_class: Testbench):
        super().__init__(testbench_class, voltage=7.4)

    def initialize(self):
        super().initialize()
        # Refine parameters specific to LD-27MG
        self.model.kt = Parameter(2.65, 1.0, 5.0)  # Based on ~27 kg·cm torque
        self.model.R = Parameter(2.5, 1.0, 6.0)
        self.model.armature = Parameter(0.005, 0.001, 0.015)


class HiwonderLX15DActuator(HiwonderBusServoActuator):
    """
    Hiwonder LX-15D servo (compact digital servo)

    Specifications:
    - Voltage: 4.8V - 8.4V (6V recommended)
    - Torque: ~1.5 kg·cm @ 6V
    - Speed: ~0.12 sec/60° @ 6V
    - Weight: 15.5g
    """

    def __init__(self, testbench_class: Testbench):
        super().__init__(testbench_class, voltage=6.0)

    def initialize(self):
        super().initialize()
        # Refine parameters specific to LX-15D
        self.model.kt = Parameter(0.147, 0.05, 0.5)  # Based on ~1.5 kg·cm torque
        self.model.R = Parameter(3.0, 1.0, 6.0)
        self.model.armature = Parameter(0.0012, 0.0003, 0.007)
