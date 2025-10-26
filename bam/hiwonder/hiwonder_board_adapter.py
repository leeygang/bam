"""
Adapter for using Hiwonder servos via Board Controller for BAM testing

This module provides a BAM-compatible interface for Hiwonder servos
controlled through the Hiwonder Bus Servo Controller Board.

The board controller provides these advantages:
- Controls multiple servos simultaneously
- More reliable communication
- Battery voltage monitoring
- Synchronized multi-servo movements
"""

import os
import numpy as np
import time
from typing import Optional


class HiwonderBoardServo:
    """
    BAM-compatible interface for Hiwonder servos via board controller.

    This wraps the HiwonderBoardController to provide the same interface
    as HiwonderServo for BAM data collection.
    """

    def __init__(self, port: str, baudrate: int = 115200, servo_id: int = 1):
        """
        Initialize Hiwonder servo via board controller.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0')
            baudrate: Baud rate (default: 115200)
            servo_id: Servo ID (default: 1)
        """
        from .hiwonder_board_controller import HiwonderBoardController

        self.servo_id = servo_id
        self.port = port
        self.baudrate = baudrate

        # Try to set low latency mode (optional, improves timing)
        try:
            result = os.system(f"setserial {port} low_latency 2>/dev/null")
        except:
            pass  # Not critical if this fails

        # Initialize board controller
        self.board = HiwonderBoardController(port=port, baudrate=baudrate)

        print(f"Hiwonder Board Servo initialized (ID: {servo_id})")

    def set_torque_enable(self, enable: bool) -> None:
        """
        Enable or disable servo torque.

        Args:
            enable: True to enable torque, False to disable
        """
        if not enable:
            # Unload servo (disable torque)
            self.board.unload_servos([self.servo_id])
        # Note: Enabling torque happens automatically when sending position commands

    def set_goal_position(self, position: float, duration: int = 0) -> None:
        """
        Set servo goal position.

        Args:
            position: Position in radians (will be converted to 0-1000 range)
            duration: Movement duration in milliseconds (0 = use fast default)
        """
        # Convert radians to servo units (0-1000 for 0-240 degrees typically)
        # Assuming 0 radians = 500 (center), full range is about ±120 degrees = ±2.094 rad
        position_units = int(500 + (position / (2 * np.pi)) * 1000)
        position_units = np.clip(position_units, 0, 1000)

        # Use fast movement if duration not specified
        if duration == 0:
            duration = 20  # 20ms = fast movement

        # Send move command to board
        self.board.move_servos([(self.servo_id, position_units, duration)])

    def read_position(self) -> float:
        """
        Read current servo position.

        Returns:
            Position in radians
        """
        positions = self.board.read_servo_positions([self.servo_id])

        if positions is None or len(positions) == 0:
            return 0.0

        # Extract position for our servo
        for servo_id, position_units in positions:
            if servo_id == self.servo_id:
                # Convert to radians (500 = center = 0 rad)
                position = ((position_units - 500) / 1000.0) * (2 * np.pi)
                return position

        return 0.0

    def read_voltage(self) -> float:
        """
        Read servo input voltage (from board).

        Returns:
            Voltage in volts
        """
        voltage = self.board.get_battery_voltage()
        return voltage if voltage is not None else 0.0

    def read_temperature(self) -> int:
        """
        Read servo temperature.

        Note: Board controller doesn't provide per-servo temperature.
        Returns 0 for compatibility.

        Returns:
            Temperature in degrees Celsius (always 0)
        """
        return 0

    def read_data(self) -> dict:
        """
        Read all servo data (position, voltage, temperature).

        Returns:
            Dictionary with position, speed (estimated), load, input_volts, temp
        """
        position = self.read_position()
        voltage = self.read_voltage()

        # Speed and load are not directly available
        return {
            "position": position,
            "speed": 0.0,  # Will be estimated from position differences
            "load": 0,  # Not available on board controller
            "input_volts": voltage,
            "temp": 0,  # Not available on board controller
        }

    def close(self) -> None:
        """Close board controller connection."""
        self.board.close()


class HiwonderBoardServoWithSpeedEstimation(HiwonderBoardServo):
    """
    Extended version that estimates speed from position changes.

    This is the recommended class for BAM data collection.
    """

    def __init__(self, port: str, baudrate: int = 115200, servo_id: int = 1):
        super().__init__(port, baudrate, servo_id)
        self.last_position = None
        self.last_time = None

    def read_data(self) -> dict:
        """
        Read servo data with speed estimation.

        Returns:
            Dictionary with position, estimated speed, load, input_volts, temp
        """
        current_time = time.time()
        position = self.read_position()
        voltage = self.read_voltage()

        # Estimate speed from position change
        speed = 0.0
        if self.last_position is not None and self.last_time is not None:
            dt = current_time - self.last_time
            if dt > 0:
                speed = (position - self.last_position) / dt

        self.last_position = position
        self.last_time = current_time

        return {
            "position": position,
            "speed": speed,
            "load": 0,  # Not available
            "input_volts": voltage,
            "temp": 0,  # Not available
        }


# For backward compatibility with existing code
HiwonderBoardAdapter = HiwonderBoardServoWithSpeedEstimation
