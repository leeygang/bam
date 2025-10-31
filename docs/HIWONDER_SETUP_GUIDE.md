# Quick Setup Guide: Hiwonder Servos with BAM

This guide will help you get started with Hiwonder servo friction identification using BAM.

## What You Need

### Hardware
- [ ] Hiwonder servo (HTD-45H recommended, or LX-16A, LD-27MG, LX-15D)
- [ ] USB-to-TTL serial adapter (FTDI, CH340, CP2102, etc.)
- [ ] Power supply (**12V for HTD-45H**, 6V for LX-16A/LX-15D, 7.4V for LD-27MG)
- [ ] Pendulum arm (lightweight rod, 8-15cm)
- [ ] Weight (50-300g depending on servo)
- [ ] Mounting base

### Software
- [ ] Python 3.6+
- [ ] BAM dependencies: `pip install -r requirements_bam.txt`
- [ ] PySerial: `pip install pyserial`

## Step-by-Step Setup

### 1. Hardware Assembly

**Build the Pendulum:**
```
Servo (mounted vertically)
  ↓
Servo horn → Arm (8-10cm rod) → Weight (50-100g)
```

**For HTD-45H (recommended):**
- Use **12V power supply (3S LiPo or regulated DC)**
- Arm: 10-15cm lightweight rod/tube
- Weight: 200-500g at end
- Can handle higher loads due to 45 kg·cm torque

**For LX-16A/LX-15D:**
- Use 6V power supply
- Arm: 8-10cm lightweight rod/tube
- Weight: 50-100g at end
- Total moment of inertia should be small enough for servo

**For LD-27MG:**
- Use 7.4V power supply
- Arm: 10-15cm
- Weight: 100-300g (can handle more load)

**Wiring:**
```
Servo          USB-TTL Adapter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Red    -----> VCC (via power supply, NOT from USB!)
Brown  -----> GND
Orange -----> TX/RX (signal)
               │
               └----> May need pull-up resistor
```

**Important**: Do NOT power servo from USB adapter - use external power supply!

### 2. Software Installation

```bash
# Navigate to BAM directory
cd /path/to/bam

# Install dependencies
pip install -r requirements_bam.txt
pip install pyserial

# Test serial port access
ls -l /dev/ttyUSB*

# Add user to dialout group (Linux)
sudo usermod -a -G dialout $USER
# Log out and back in for this to take effect
```

### 3. Test Servo Communication

Create a simple test script:

```python
# test_servo.py
from bam.hiwonder.hiwonder import HiwonderServo
import time

servo = HiwonderServo('/dev/ttyUSB0', baudrate=115200, servo_id=1)

print("Testing servo communication...")
servo.set_torque_enable(True)
time.sleep(0.5)

# Read initial position
pos = servo.read_position()
print(f"Position: {pos:.3f} rad")

# Read voltage
voltage = servo.read_voltage()
print(f"Voltage: {voltage:.1f}V")

# Move to 0.5 radians
print("Moving to 0.5 rad...")
servo.set_goal_position(0.5)
time.sleep(1)

# Move back to 0
print("Moving to 0 rad...")
servo.set_goal_position(0.0)
time.sleep(1)

servo.set_torque_enable(False)
servo.close()
print("Test complete!")
```

Run: `python test_servo.py`

### 4. Measure Your Pendulum

You need accurate measurements:

```bash
# Measure pendulum parameters

# For HTD-45H (12V, high torque):
MASS=0.3      # Weight mass in kg (200-500g recommended)
LENGTH=0.12   # Distance from servo axis to weight center in meters (10-15cm)
ARM_MASS=0.02 # Arm mass in kg (optional, default 0)

# For LX-16A (6V, hobby):
MASS=0.1      # Weight mass in kg (50-100g)
LENGTH=0.08   # Distance from servo axis to weight center in meters (8-10cm)
ARM_MASS=0.01 # Arm mass in kg (optional, default 0)
```

### 5. Record Data

**Single test recording (HTD-45H):**
```bash
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir test_data \
    --trajectory lift_and_drop \
    --motor htd45h \
    --kp 32 \
    --vin 12.0
```

Watch the pendulum to verify:
- [ ] Smooth motion
- [ ] No mechanical binding
- [ ] Reaches reasonable angles
- [ ] Returns to zero safely

**Full batch recording (HTD-45H recommended for fitting):**
```bash
mkdir -p data_raw_htd45h

python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --motor htd45h \
    --vin 12.0
```

This will record 12 trajectories (4 types × 3 KP values). Takes ~10-15 minutes.

### 6. Process Data

```bash
python -m bam.process \
    --raw data_raw_lx16a \
    --logdir data_processed_lx16a \
    --dt 0.005
```

Verify processed data:
```bash
python -m bam.plot \
    --actuator lx16a \
    --logdir data_processed_lx16a
```

Check that plots look reasonable:
- [ ] Position varies smoothly
- [ ] No obvious data corruption
- [ ] Multiple trajectories present

### 7. Fit Friction Model

**Start with simple model (M1):**
```bash
mkdir -p params/lx16a

python -m bam.fit \
    --actuator lx16a \
    --model m1 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m1.json \
    --trials 5000
```

This takes 5-15 minutes depending on your computer.

**Then fit advanced model (M6):**
```bash
python -m bam.fit \
    --actuator lx16a \
    --model m6 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m6.json \
    --trials 20000
```

This takes 30-60 minutes.

### 8. Validate Results

```bash
python -m bam.plot \
    --actuator lx16a \
    --logdir data_processed_lx16a \
    --sim \
    --params params/lx16a/m6.json
```

Look for:
- [ ] Simulated trajectory closely matches real data
- [ ] No systematic errors or offsets
- [ ] Good fit across different trajectories

**Generate friction diagrams:**
```bash
python -m bam.drive_backdrive \
    --params params/lx16a/m6.json \
    --max_torque 15
```

## Expected Results

### M1 Model (Coulomb-Viscous)
- **MAE**: ~0.05-0.1 rad (typical)
- **Parameters**: friction_base, friction_viscous, kt, R, armature

### M6 Model (Full Model)
- **MAE**: ~0.02-0.05 rad (50%+ improvement over M1)
- **Additional parameters**: Stribeck, load-dependent, directional, quadratic terms

## Troubleshooting

### "Permission denied: /dev/ttyUSB0"
```bash
sudo chmod 666 /dev/ttyUSB0  # Temporary
# OR (permanent):
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### "No response from servo"
- Check power supply is ON and correct voltage
- Verify wiring (especially GND connection)
- Try different baud rates: `--baudrate 9600`
- Check servo ID: `--id 1` (default)
- Test with Hiwonder's official software first

### "Servo doesn't move"
- Ensure `set_torque_enable(True)` is called
- Check position commands are in range
- Verify servo isn't mechanically blocked
- Check voltage is sufficient

### "Poor model fit / High MAE"
- Verify mass and length measurements are accurate
- Check pendulum swings freely (no binding)
- Collect more diverse data (more trajectories)
- Try increasing optimization trials
- Ensure consistent power supply voltage

### "Noisy speed estimates"
- This is normal for basic Hiwonder servos
- Post-processing will smooth the data
- Consider increasing sampling rate (reduce sleep in record.py)

## Next Steps

Once you have good fitted parameters:

1. **Share your parameters**: Contribute back to BAM project
2. **Use in simulation**: Integrate with MuJoCo (see `2R/` examples)
3. **Test other models**: Try LD-27MG or LX-15D
4. **Vary conditions**: Different voltages, loads, temperatures

## Advanced Options

### Custom Trajectories

Edit `bam/trajectory.py` to add your own trajectories:

```python
@trajectory(duration=10.0)
def my_custom_trajectory(t):
    position = # your function here
    torque_enable = True
    return position, torque_enable
```

### Multi-Servo Batch Processing

Process multiple servo types:

```bash
for motor in lx16a ld27mg lx15d; do
    python -m bam.hiwonder.all_record \
        --motor $motor \
        --logdir data_raw_$motor \
        # ... other args
done
```

### Hyperparameter Tuning

Optimize for your specific setup:
- **KP values**: Test different ranges in `all_record.py`
- **Trajectories**: Focus on most informative ones
- **Optimization trials**: More trials = better fit (but slower)
- **Optimization method**: Try `nsgaii` for multi-objective

## Getting Help

- **BAM Documentation**: See main README.md and CLAUDE.md
- **Hiwonder Specifics**: See `bam/hiwonder/README.md`
- **Implementation Details**: See `bam/hiwonder/IMPLEMENTATION.md`
- **General Issues**: Check GitHub issues or ask in discussions

## Summary Checklist

- [ ] Hardware assembled and tested
- [ ] Software installed and configured
- [ ] Servo communication working
- [ ] Pendulum parameters measured
- [ ] Test recording successful
- [ ] Batch data collection complete
- [ ] Data processed and visualized
- [ ] M1 model fitted
- [ ] M6 model fitted and validated
- [ ] Results documented

Congratulations! You've successfully identified friction parameters for your Hiwonder servo! 🎉
