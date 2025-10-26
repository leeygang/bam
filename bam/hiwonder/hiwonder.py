import os
import numpy as np
import serial
import time
from typing import Optional


class HiwonderServo:
    """
    Communication protocol for Hiwonder bus servos (LX-16A, LX-15D, LD-27MG, etc.)

    Protocol specifications:
    - Baud rate: 115200 (default) or 9600
    - Data bits: 8
    - Stop bits: 1
    - Parity: None
    - Half-duplex serial communication

    Command format:
    Header | ID | Length | Command | Parameters | Checksum

    Position range: 0-1000 (corresponding to 0-240 degrees typically)
    """

    # Command definitions
    CMD_SERVO_MOVE = 1  # Move servo to position
    CMD_SERVO_MOVE_TIME_WRITE = 1  # Move with time
    CMD_SERVO_MOVE_TIME_READ = 2
    CMD_SERVO_MOVE_TIME_WAIT_WRITE = 7
    CMD_SERVO_MOVE_TIME_WAIT_READ = 8
    CMD_SERVO_MOVE_START = 11
    CMD_SERVO_MOVE_STOP = 12
    CMD_SERVO_ID_WRITE = 13
    CMD_SERVO_ID_READ = 14
    CMD_SERVO_ANGLE_OFFSET_ADJUST = 17
    CMD_SERVO_ANGLE_OFFSET_WRITE = 18
    CMD_SERVO_ANGLE_OFFSET_READ = 19
    CMD_SERVO_ANGLE_LIMIT_WRITE = 20
    CMD_SERVO_ANGLE_LIMIT_READ = 21
    CMD_SERVO_VIN_LIMIT_WRITE = 22
    CMD_SERVO_VIN_LIMIT_READ = 23
    CMD_SERVO_TEMP_MAX_LIMIT_WRITE = 24
    CMD_SERVO_TEMP_MAX_LIMIT_READ = 25
    CMD_SERVO_TEMP_READ = 26
    CMD_SERVO_VIN_READ = 27
    CMD_SERVO_POS_READ = 28
    CMD_SERVO_OR_MOTOR_MODE_WRITE = 29
    CMD_SERVO_OR_MOTOR_MODE_READ = 30
    CMD_SERVO_LOAD_OR_UNLOAD_WRITE = 31
    CMD_SERVO_LOAD_OR_UNLOAD_READ = 32
    CMD_SERVO_LED_CTRL_WRITE = 33
    CMD_SERVO_LED_CTRL_READ = 34
    CMD_SERVO_LED_ERROR_WRITE = 35
    CMD_SERVO_LED_ERROR_READ = 36

    def __init__(self, port: str, baudrate: int = 115200, servo_id: int = 1):
        """
        Initialize Hiwonder servo communication.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0')
            baudrate: Baud rate (default: 115200)
            servo_id: Servo ID (default: 1)
        """
        self.servo_id = servo_id
        self.port = port
        self.baudrate = baudrate

        # Try to set low latency mode (optional, improves timing)
        try:
            result = os.system(f"setserial {port} low_latency 2>/dev/null")
        except:
            pass  # Not critical if this fails

        # Open serial connection
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )

        # Clear any existing data
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def _calculate_checksum(self, data: bytes) -> int:
        """Calculate checksum for command packet."""
        return (~sum(data)) & 0xFF

    def _send_command(self, command: int, params: bytes = b'') -> None:
        """
        Send command to servo.

        Args:
            command: Command byte
            params: Parameter bytes
        """
        length = len(params) + 3  # ID + Length + Command
        packet = bytes([0x55, 0x55, self.servo_id, length, command]) + params
        checksum = self._calculate_checksum(packet[2:])
        packet += bytes([checksum])

        self.serial.write(packet)
        self.serial.flush()

    def _read_response(self, expected_length: int) -> Optional[bytes]:
        """
        Read response from servo.

        Args:
            expected_length: Expected number of bytes in response

        Returns:
            Response data or None if timeout/error
        """
        # Look for header (0x55 0x55)
        start_time = time.time()
        while time.time() - start_time < 0.1:  # 100ms timeout
            if self.serial.in_waiting >= 2:
                header = self.serial.read(2)
                if header == b'\x55\x55':
                    break
        else:
            return None

        # Read rest of packet
        if self.serial.in_waiting < expected_length - 2:
            time.sleep(0.01)  # Give it a bit more time

        data = self.serial.read(expected_length - 2)
        if len(data) < expected_length - 2:
            return None

        return header + data

    def set_torque_enable(self, enable: bool) -> None:
        """
        Enable or disable servo torque.

        Args:
            enable: True to enable torque, False to disable
        """
        params = bytes([1 if enable else 0])
        self._send_command(self.CMD_SERVO_LOAD_OR_UNLOAD_WRITE, params)
        time.sleep(0.001)

    def set_goal_position(self, position: float, duration: int = 0) -> None:
        """
        Set servo goal position.

        Args:
            position: Position in radians (will be converted to 0-1000 range)
            duration: Movement duration in milliseconds (0 = immediate)
        """
        # Convert radians to servo units (0-1000 for 0-240 degrees typically)
        # Assuming 0 radians = 500 (center), full range is about ±120 degrees = ±2.094 rad
        position_units = int(500 + (position / (2 * np.pi)) * 1000)
        position_units = np.clip(position_units, 0, 1000)

        # Pack parameters: position (2 bytes, low-high) + duration (2 bytes, low-high)
        params = bytes([
            position_units & 0xFF,
            (position_units >> 8) & 0xFF,
            duration & 0xFF,
            (duration >> 8) & 0xFF
        ])

        self._send_command(self.CMD_SERVO_MOVE_TIME_WRITE, params)

    def read_position(self) -> float:
        """
        Read current servo position.

        Returns:
            Position in radians
        """
        self._send_command(self.CMD_SERVO_POS_READ)
        response = self._read_response(8)  # Header(2) + ID(1) + Len(1) + Cmd(1) + Pos(2) + Checksum(1)

        if response is None or len(response) < 8:
            return 0.0

        # Extract position (2 bytes, low-high)
        position_units = response[5] | (response[6] << 8)

        # Convert to radians (500 = center = 0 rad)
        position = ((position_units - 500) / 1000.0) * (2 * np.pi)

        return position

    def read_voltage(self) -> float:
        """
        Read servo input voltage.

        Returns:
            Voltage in volts
        """
        self._send_command(self.CMD_SERVO_VIN_READ)
        response = self._read_response(7)  # Header(2) + ID(1) + Len(1) + Cmd(1) + Voltage(1) + Checksum(1)

        if response is None or len(response) < 7:
            return 0.0

        # Voltage is in units of 100mV
        voltage = response[5] / 10.0

        return voltage

    def read_temperature(self) -> int:
        """
        Read servo temperature.

        Returns:
            Temperature in degrees Celsius
        """
        self._send_command(self.CMD_SERVO_TEMP_READ)
        response = self._read_response(7)

        if response is None or len(response) < 7:
            return 0

        temperature = response[5]

        return temperature

    def read_data(self) -> dict:
        """
        Read all servo data (position, voltage, temperature).

        Returns:
            Dictionary with position, speed (estimated), load, input_volts, temp
        """
        position = self.read_position()
        voltage = self.read_voltage()
        temperature = self.read_temperature()

        # Speed and load are not directly available on basic Hiwonder servos
        # Speed can be estimated by tracking position changes
        return {
            "position": position,
            "speed": 0.0,  # Will be estimated from position differences
            "load": 0,  # Not available on basic models
            "input_volts": voltage,
            "temp": temperature,
        }

    def close(self) -> None:
        """Close serial connection."""
        if self.serial.is_open:
            self.serial.close()


class HiwonderServoWithSpeedEstimation(HiwonderServo):
    """
    Extended version that estimates speed from position changes.
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
        temperature = self.read_temperature()

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
            "temp": temperature,
        }
