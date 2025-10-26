import subprocess
import argparse
import os

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--mass", type=float, required=True, help="Mass of the pendulum load (kg)")
arg_parser.add_argument("--length", type=float, required=True, help="Length of the pendulum (m)")
arg_parser.add_argument("--arm_mass", type=float, default=0.0, help="Mass of the pendulum arm (kg)")
arg_parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port")
arg_parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate")
arg_parser.add_argument("--id", type=int, default=1, help="Servo ID")
arg_parser.add_argument("--logdir", type=str, required=True, help="Directory to save logs")
arg_parser.add_argument("--motor", type=str, required=True, help="Motor model (lx16a, ld27mg, lx15d)")
arg_parser.add_argument("--vin", type=float, default=6.0, help="Input voltage (V)")
arg_parser.add_argument("--speak", action="store_true", help="Speak trajectory and KP before recording")
args = arg_parser.parse_args()

# Create log directory
os.makedirs(args.logdir, exist_ok=True)

# Define trajectories to record
trajectories = [
    "sin_time_square",
    "sin_sin",
    "lift_and_drop",
    "up_and_down"
]

# Define KP values to test
kp_values = [8, 16, 32]

print("=" * 60)
print("HIWONDER SERVO BATCH RECORDING")
print("=" * 60)
print(f"Motor: {args.motor}")
print(f"Mass: {args.mass}kg, Length: {args.length}m, Arm mass: {args.arm_mass}kg")
print(f"Port: {args.port}, Baudrate: {args.baudrate}")
print(f"Input voltage: {args.vin}V")
print(f"Trajectories: {', '.join(trajectories)}")
print(f"KP values: {', '.join(map(str, kp_values))}")
print(f"Total recordings: {len(trajectories) * len(kp_values)}")
print("=" * 60)

recording_count = 0
total_recordings = len(trajectories) * len(kp_values)

# Record all combinations
for kp in kp_values:
    for trajectory in trajectories:
        recording_count += 1
        print(f"\n[{recording_count}/{total_recordings}] Recording: {trajectory} with KP={kp}")
        print("-" * 60)

        # Speak the current settings if requested
        if args.speak:
            try:
                message = f"Recording {trajectory.replace('_', ' ')} with K P {kp}"
                subprocess.run(["espeak", message], check=False, stderr=subprocess.DEVNULL)
            except:
                pass  # espeak not available, skip

        # Build command
        cmd = [
            "python", "-m", "bam.hiwonder.record",
            "--mass", str(args.mass),
            "--length", str(args.length),
            "--arm_mass", str(args.arm_mass),
            "--port", args.port,
            "--baudrate", str(args.baudrate),
            "--id", str(args.id),
            "--logdir", args.logdir,
            "--trajectory", trajectory,
            "--motor", args.motor,
            "--kp", str(kp),
            "--vin", str(args.vin)
        ]

        # Run recording
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"ERROR: Recording failed with code {result.returncode}")
            user_input = input("Continue with next recording? (y/n): ")
            if user_input.lower() != 'y':
                print("Batch recording aborted.")
                exit(1)
        else:
            print(f"✓ Recording successful")

print("\n" + "=" * 60)
print("BATCH RECORDING COMPLETE")
print("=" * 60)
print(f"Total recordings: {recording_count}")
print(f"Data saved to: {args.logdir}")
print("\nNext steps:")
print(f"  1. Process data: python -m bam.process --raw {args.logdir} --logdir data_processed --dt 0.005")
print(f"  2. Fit model: python -m bam.fit --actuator {args.motor} --model m6 --logdir data_processed --output params/{args.motor}/m6.json")
