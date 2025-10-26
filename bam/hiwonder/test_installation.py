#!/usr/bin/env python
"""
Test script to verify Hiwonder implementation is correctly installed.
Run this before attempting to use the Hiwonder servos.
"""

import sys
import os

def test_imports():
    """Test that all necessary modules can be imported."""
    print("Testing imports...")
    errors = []

    try:
        import serial
        print("  ✓ pyserial installed")
    except ImportError:
        errors.append("pyserial not installed. Run: pip install pyserial")

    try:
        import numpy as np
        print("  ✓ numpy installed")
    except ImportError:
        errors.append("numpy not installed. Run: pip install numpy")

    try:
        from bam.hiwonder.actuator import HiwonderLX16AActuator
        print("  ✓ Hiwonder actuator module found")
    except ImportError as e:
        errors.append(f"Cannot import Hiwonder actuator: {e}")

    try:
        from bam.hiwonder.hiwonder import HiwonderServo
        print("  ✓ Hiwonder protocol module found")
    except ImportError as e:
        errors.append(f"Cannot import Hiwonder protocol: {e}")

    try:
        from bam.actuators import actuators
        assert "lx16a" in actuators
        assert "ld27mg" in actuators
        assert "lx15d" in actuators
        print("  ✓ Hiwonder actuators registered")
    except (ImportError, AssertionError) as e:
        errors.append(f"Hiwonder actuators not properly registered: {e}")

    try:
        from bam.trajectory import trajectories
        print("  ✓ Trajectory module found")
    except ImportError as e:
        errors.append(f"Cannot import trajectories: {e}")

    return errors


def test_serial_ports():
    """Test for available serial ports."""
    print("\nChecking serial ports...")

    # Check common serial port locations
    port_locations = [
        "/dev/ttyUSB0",
        "/dev/ttyUSB1",
        "/dev/ttyACM0",
        "/dev/ttyACM1",
        "COM1",
        "COM2",
        "COM3",
        "COM4"
    ]

    found_ports = []
    for port in port_locations:
        if os.path.exists(port):
            found_ports.append(port)
            print(f"  ✓ Found: {port}")

    if not found_ports:
        print("  ⚠ No serial ports found")
        print("    Connect your USB-to-TTL adapter and try again")

    return found_ports


def test_actuator_creation():
    """Test that actuator objects can be created."""
    print("\nTesting actuator creation...")
    errors = []

    try:
        from bam.actuators import actuators
        from bam.testbench import Pendulum

        # Test LX-16A
        try:
            lx16a = actuators["lx16a"]()
            print("  ✓ LX-16A actuator created")
        except Exception as e:
            errors.append(f"Failed to create LX-16A: {e}")

        # Test LD-27MG
        try:
            ld27mg = actuators["ld27mg"]()
            print("  ✓ LD-27MG actuator created")
        except Exception as e:
            errors.append(f"Failed to create LD-27MG: {e}")

        # Test LX-15D
        try:
            lx15d = actuators["lx15d"]()
            print("  ✓ LX-15D actuator created")
        except Exception as e:
            errors.append(f"Failed to create LX-15D: {e}")

    except Exception as e:
        errors.append(f"Failed to test actuator creation: {e}")

    return errors


def test_model_creation():
    """Test that models can be created with Hiwonder actuators."""
    print("\nTesting model creation...")
    errors = []

    try:
        from bam.model import models
        from bam.actuators import actuators

        # Test M1 model with LX-16A
        try:
            model = models["m1"]()
            model.set_actuator(actuators["lx16a"]())
            print("  ✓ M1 model with LX-16A created")
        except Exception as e:
            errors.append(f"Failed to create M1 with LX-16A: {e}")

        # Test M6 model with LX-16A
        try:
            model = models["m6"]()
            model.set_actuator(actuators["lx16a"]())
            print("  ✓ M6 model with LX-16A created")
        except Exception as e:
            errors.append(f"Failed to create M6 with LX-16A: {e}")

    except Exception as e:
        errors.append(f"Failed to test model creation: {e}")

    return errors


def print_summary(all_errors):
    """Print test summary."""
    print("\n" + "="*60)
    if not all_errors:
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to use Hiwonder servos with BAM.")
        print("\nNext steps:")
        print("  1. Connect your servo and USB-to-TTL adapter")
        print("  2. Test communication with test_servo.py (see HIWONDER_SETUP_GUIDE.md)")
        print("  3. Start collecting data with bam.hiwonder.record")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nErrors found:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        print("\nPlease fix these issues before using Hiwonder servos.")
        print("See HIWONDER_SETUP_GUIDE.md for help.")
    print("="*60)


def main():
    """Run all tests."""
    print("="*60)
    print("HIWONDER SERVO IMPLEMENTATION TEST")
    print("="*60)

    all_errors = []

    # Test imports
    errors = test_imports()
    all_errors.extend(errors)

    # Test serial ports
    found_ports = test_serial_ports()

    # Test actuator creation
    errors = test_actuator_creation()
    all_errors.extend(errors)

    # Test model creation
    errors = test_model_creation()
    all_errors.extend(errors)

    # Print summary
    print_summary(all_errors)

    # Return exit code
    return 0 if not all_errors else 1


if __name__ == "__main__":
    sys.exit(main())
