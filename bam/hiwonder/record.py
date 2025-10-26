import json
import datetime
import os
import numpy as np
import argparse
import time
from .hiwonder import HiwonderServoWithSpeedEstimation
from bam.trajectory import trajectories

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--mass", type=float, required=True, help="Mass of the pendulum load (kg)")
arg_parser.add_argument("--length", type=float, required=True, help="Length of the pendulum (m)")
arg_parser.add_argument("--arm_mass", type=float, default=0.0, help="Mass of the pendulum arm (kg)")
arg_parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port")
arg_parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate (default: 115200)")
arg_parser.add_argument("--id", type=int, default=1, help="Servo ID (default: 1)")
arg_parser.add_argument("--logdir", type=str, required=True, help="Directory to save logs")
arg_parser.add_argument("--trajectory", type=str, default="lift_and_drop", help="Trajectory name")
arg_parser.add_argument("--motor", type=str, required=True, help="Motor model (lx16a, ld27mg, lx15d)")
arg_parser.add_argument("--kp", type=int, default=32, help="Proportional gain")
arg_parser.add_argument("--vin", type=float, default=6.0, help="Input voltage (V)")
args = arg_parser.parse_args()

# Create log directory if it doesn't exist
os.makedirs(args.logdir, exist_ok=True)

# Validate trajectory
if args.trajectory not in trajectories:
    raise ValueError(f"Unknown trajectory: {args.trajectory}. Available: {list(trajectories.keys())}")

# Initialize servo
print(f"Connecting to Hiwonder servo on {args.port} at {args.baudrate} baud...")
servo = HiwonderServoWithSpeedEstimation(args.port, args.baudrate, args.id)
trajectory = trajectories[args.trajectory]

print(f"Running trajectory: {args.trajectory}")
print(f"Motor: {args.motor}, KP: {args.kp}, Vin: {args.vin}V")
print(f"Mass: {args.mass}kg, Length: {args.length}m")

# Initialization phase: set initial position and torque for 1 second
print("Initializing servo...")
torque_enable = False
start = time.time()
while time.time() - start < 1.0:
    goal_position, torque_enable = trajectory(0)
    if torque_enable:
        servo.set_goal_position(goal_position)
    servo.set_torque_enable(torque_enable)
    time.sleep(0.01)

# Start recording
print(f"Recording for {trajectory.duration} seconds...")
start = time.time()
data = {
    "mass": args.mass,
    "length": args.length,
    "arm_mass": args.arm_mass,
    "kp": args.kp,
    "vin": args.vin,
    "motor": args.motor,
    "trajectory": args.trajectory,
    "entries": []
}

# Main recording loop
while time.time() - start < trajectory.duration:
    t = time.time() - start

    # Get trajectory target
    goal_position, new_torque_enable = trajectory(t)

    # Update torque enable if changed
    if new_torque_enable != torque_enable:
        servo.set_torque_enable(new_torque_enable)
        torque_enable = new_torque_enable
        time.sleep(0.001)

    # Update goal position if torque is enabled
    if torque_enable:
        servo.set_goal_position(goal_position)
        time.sleep(0.001)

    # Read data from servo
    t0 = time.time() - start
    entry = servo.read_data()
    t1 = time.time() - start

    # Add metadata to entry
    entry["timestamp"] = (t0 + t1) / 2.0
    entry["goal_position"] = goal_position
    entry["torque_enable"] = torque_enable
    data["entries"].append(entry)

    # Small delay to control sampling rate (~100Hz)
    time.sleep(0.005)

print(f"Recording complete. Recorded {len(data['entries'])} samples.")

# Return to zero position slowly
print("Returning to zero position...")
goal_position = data["entries"][-1]["position"]
return_dt = 0.01
max_variation = return_dt * 1.0  # Maximum 1 rad/s

while abs(goal_position) > 0.01:  # Within 0.01 rad of zero
    if goal_position > 0:
        goal_position = max(0, goal_position - max_variation)
    else:
        goal_position = min(0, goal_position + max_variation)
    servo.set_goal_position(goal_position)
    time.sleep(return_dt)

# Disable torque
servo.set_torque_enable(False)
servo.close()

# Save data to file
date = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%S")
filename = f"{args.logdir}/{date}.json"
json.dump(data, open(filename, "w"))

print(f"Data saved to: {filename}")
print(f"Average sampling rate: {len(data['entries']) / trajectory.duration:.1f} Hz")
