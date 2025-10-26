# Hiwonder Servo Implementation for BAM

This document describes the complete implementation of Hiwonder servo support in the BAM framework.

## Overview

The implementation adds support for Hiwonder bus servos (LX-16A, LD-27MG, LX-15D) to the BAM friction identification system. These are low-cost Chinese servos commonly used in hobbyist and educational robotics.

## Implementation Structure

### Files Created

```
bam/hiwonder/
├── __init__.py              # Package initialization
├── actuator.py              # Actuator model definitions
├── hiwonder.py              # Serial communication protocol
├── record.py                # Single trajectory recording
├── all_record.py            # Batch recording script
├── README.md                # User documentation
└── IMPLEMENTATION.md        # This file (implementation details)
```

### Files Modified

- `bam/actuators.py`: Added Hiwonder actuator registrations
- `CLAUDE.md`: Added Hiwonder usage examples

## Architecture

### 1. Actuator Models (`actuator.py`)

Defines three specific actuator classes:

- **`HiwonderLX16AActuator`**: Most common model (1.6 kg·cm @ 6V)
- **`HiwonderLD27MGActuator`**: High-torque model (27 kg·cm @ 7.4V)
- **`HiwonderLX15DActuator`**: Compact model (1.5 kg·cm @ 6V)

All inherit from `VoltageControlledActuator`, providing:
- `initialize()`: Sets up model parameters (kt, R, armature)
- `get_extra_inertia()`: Returns rotor inertia

**Parameter Initialization Strategy:**
- Parameters are initialized with reasonable estimates based on datasheet values
- These will be refined through the fitting process
- Initial bounds are set wide enough to accommodate model uncertainty

### 2. Communication Protocol (`hiwonder.py`)

Implements two classes:

#### `HiwonderServo`
Basic communication with Hiwonder servos:
- Serial protocol implementation (half-duplex)
- Command/response packet handling
- Position, voltage, temperature reading
- Torque enable/disable

**Protocol Details:**
- Header: `[0x55, 0x55]`
- Packet: `[Header, ID, Length, Command, Params..., Checksum]`
- Checksum: `~(sum of ID through params) & 0xFF`
- Position range: 0-1000 (typically 0-240 degrees)

#### `HiwonderServoWithSpeedEstimation`
Extended version that estimates angular velocity:
- Tracks position changes over time
- Computes `speed = Δposition / Δtime`
- More accurate for BAM data collection

**Speed Estimation Rationale:**
Basic Hiwonder servos don't provide direct velocity feedback. The estimation approach:
1. Records position and timestamp on each read
2. Calculates velocity from consecutive samples
3. Provides reasonable velocity estimates for friction identification

### 3. Recording Scripts

#### `record.py`
Single trajectory recording with:
- Configurable pendulum parameters (mass, length, arm_mass)
- Trajectory execution with timing control
- Data logging to JSON format
- Safe return-to-zero at end

**Data Collection Flow:**
1. Initialize servo and enable torque
2. Execute trajectory for specified duration
3. Sample at ~100-200Hz (adjustable via sleep)
4. Record: timestamp, position, speed, goal_position, voltage, temperature
5. Return to zero position smoothly
6. Disable torque and save data

#### `all_record.py`
Automated batch recording:
- Tests multiple trajectories: `sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`
- Tests multiple KP gains: 8, 16, 32
- Optional speech announcements (via `espeak`)
- Error handling with user intervention

**Batch Strategy:**
- Systematically varies control parameters (KP) and excitation (trajectory)
- Captures diverse operating conditions for robust fitting
- Total of 12 recordings per batch run

### 4. Integration with BAM

#### Registration in `actuators.py`
```python
"lx16a": lambda: HiwonderLX16AActuator(Pendulum),
"ld27mg": lambda: HiwonderLD27MGActuator(Pendulum),
"lx15d": lambda: HiwonderLX15DActuator(Pendulum),
```

This allows the actuators to be used throughout BAM:
- `bam.fit --actuator lx16a`
- `bam.plot --actuator lx16a`
- Model loading: `actuators["lx16a"]()`

## Design Decisions

### 1. Voltage-Controlled Model
Hiwonder servos are modeled as voltage-controlled DC motors because:
- They have brushed DC motors inside
- Controller applies PWM voltage to the motor
- Back-EMF and resistance are the dominant electrical characteristics
- This matches the Dynamixel and Feetech implementations

### 2. Half-Duplex Communication
The protocol uses a single wire for TX/RX:
- Simpler wiring (only 3 wires total)
- Common in hobby servo protocols
- Requires careful timing to avoid bus conflicts
- Implementation uses timeouts and retries

### 3. Speed Estimation vs. Direct Measurement
Basic Hiwonder servos lack velocity sensors, so we estimate:
- **Pros**: Works with hardware limitations, provides reasonable estimates
- **Cons**: Sensitive to sampling rate, can be noisy
- **Mitigation**: Use consistent timing, post-processing filters available

### 4. Parameter Initialization
Initial parameter values are educated guesses:
- Based on torque specs (torque constant kt)
- Typical motor resistance values
- Reasonable inertia estimates
- Wide bounds to allow convergence

**Why this approach:**
- Speeds up optimization (starts near solution)
- Prevents optimizer from exploring unrealistic regions
- Can be refined after first round of fitting

## Usage Workflow

### Complete Identification Pipeline

```bash
# 1. Collect raw data
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --mass 0.1 \
    --length 0.08 \
    --logdir data_raw_lx16a \
    --motor lx16a \
    --vin 6.0

# 2. Post-process (resample to constant dt)
python -m bam.process \
    --raw data_raw_lx16a \
    --logdir data_processed_lx16a \
    --dt 0.005

# 3. Fit simple model first (M1)
python -m bam.fit \
    --actuator lx16a \
    --model m1 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m1.json \
    --trials 10000

# 4. Fit advanced model (M6)
python -m bam.fit \
    --actuator lx16a \
    --model m6 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m6.json \
    --trials 50000

# 5. Validate results
python -m bam.plot \
    --actuator lx16a \
    --logdir data_processed_lx16a \
    --sim \
    --params params/lx16a/m6.json

# 6. Generate friction diagrams
python -m bam.drive_backdrive \
    --params params/lx16a/m6.json \
    --max_torque 15
```

## Testing and Validation

### Recommended Test Setup

**Pendulum Configuration for LX-16A:**
- Arm length: 8-10 cm
- End mass: 50-100g
- Arm mass: ~5-10g (lightweight rod/tube)
- Ensure free swing ±90° minimum

**Pendulum Configuration for LD-27MG:**
- Arm length: 10-15 cm
- End mass: 100-300g
- Can use heavier arm due to higher torque

### Data Quality Checks

Before fitting, verify:
1. **Sampling rate**: Should be 100-200Hz
2. **Position range**: Pendulum swings through significant angles
3. **No saturation**: Servo doesn't hit mechanical limits
4. **Smooth return**: Pendulum returns to zero without oscillation

Visualize raw data:
```bash
python -m bam.plot \
    --actuator lx16a \
    --logdir data_processed_lx16a
```

## Troubleshooting

### Common Issues

**Serial communication errors:**
- Check port permissions (`sudo chmod 666 /dev/ttyUSB0`)
- Verify baud rate (115200 is standard)
- Test with shorter cables if issues persist
- Ensure proper power supply

**Position reading errors:**
- Verify servo is powered and responding
- Check ID matches (default is 1)
- Test with Hiwonder's official software first

**Poor model fit:**
- Collect more diverse trajectories
- Increase optimization trials
- Check for mechanical issues (binding, loose parts)
- Verify accurate mass/length measurements

**Speed estimates are noisy:**
- Increase sampling rate (reduce sleep time)
- Post-process with filters
- Check for USB latency issues

## Future Improvements

### Potential Enhancements

1. **Direct velocity measurement**: If higher-end Hiwonder servos with velocity feedback become available
2. **Current sensing**: Some models may support current reading for better torque estimation
3. **Temperature compensation**: Model temperature effects on friction
4. **Multi-servo support**: Coordinate multiple servos on single bus
5. **Async communication**: Non-blocking reads for higher throughput

### Parameter Refinement

After initial fitting:
1. Update `actuator.py` with fitted parameter values
2. Narrow parameter bounds based on results
3. Re-run optimization with tighter bounds
4. Iterate if needed for different operating voltages

## References

- **BAM Framework**: See main README.md and paper
- **Hiwonder Protocol**: Based on reverse engineering and community documentation
- **Similar implementations**: See `bam/dynamixel/` and `bam/feetech/` for comparison

## Authors

- Yonatan Gu Li (Initial Hiwonder implementation)
- Based on BAM framework by Rhoban team

## License

Same as BAM project (MIT License)
