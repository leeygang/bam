# Hiwonder Servo Experiment Guide

Complete guide for collecting friction identification data with Hiwonder servos in BAM.

## Hardware Setup

### Supported Servos

| Model | Voltage | Torque | Status | Notes |
|-------|---------|--------|--------|-------|
| **HTD-45H** | 12V | 45 kg·cm | ⭐ Primary | Industrial, metal gears |
| LX-16A | 6V | 1.6 kg·cm | Supported | Hobby, lightweight |
| LD-27MG | 7.4V | 27 kg·cm | Supported | Hobby, metal gears |
| LX-15D | 6V | 1.5 kg·cm | Supported | Hobby, compact |

**Recommendation**: Use HTD-45H for best results due to higher torque and better friction characterization.

### Required Equipment

#### Method 1: Board Controller (Recommended)
- Hiwonder Bus Servo Controller Board
- Servo (HTD-45H recommended)
- Power supply (12V/2-3A for HTD-45H, 6V for LX-16A)
- USB cable (board to computer)
- Pendulum arm and weight

#### Method 2: Direct Serial
- USB-to-TTL adapter (FTDI, CH340, CP2102)
- Servo (HTD-45H recommended)
- Power supply (12V/2-3A for HTD-45H, 6V for LX-16A)
- Pendulum arm and weight

### Wiring

#### Board Controller Setup
```
┌─────────────────────────────────────┐
│  Hiwonder Bus Servo Controller      │
│  [USB] ────► Computer               │
│  [12V IN] ◄──── Power Supply        │
│  [GND] ◄──── GND                    │
│  [Port 1] ◄──── Servo               │
└─────────────────────────────────────┘
```

#### Direct Serial Setup
```
Servo          USB-TTL       Power Supply
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Red    -----> (not used)  --> 12V+
Brown  -----> GND         --> GND
Orange -----> TX/RX
```

**CRITICAL**: Power servos from external supply, NOT USB!

### Pendulum Configuration

#### HTD-45H (12V)
- Arm length: 10-15 cm
- End mass: 200-500 g
- Arm material: Lightweight aluminum or carbon fiber
- Example: 12 cm arm, 300 g weight

#### LX-16A (6V)
- Arm length: 8-10 cm
- End mass: 50-100 g
- Arm material: Lightweight rod/tube
- Example: 8 cm arm, 100 g weight

#### LD-27MG (7.4V)
- Arm length: 10-15 cm
- End mass: 100-300 g
- Similar to HTD-45H but less load capacity

**Important**: Measure actual mass and length accurately with scale and ruler.

## Software Installation

```bash
# Install dependencies
pip install pyserial

# Linux: Add user to serial port group
sudo usermod -a -G dialout $USER
# Log out and back in for this to take effect

# Verify serial port
ls -l /dev/ttyUSB*
```

## Running Experiments

### Quick Test (Single Recording)

Test your setup before batch collection:

**Board Controller:**
```bash
python -m bam.hiwonder.record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir test_data \
    --trajectory lift_and_drop
```

**Direct Serial:**
```bash
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir test_data \
    --trajectory lift_and_drop
```

Verify the pendulum:
- Moves smoothly
- Reaches reasonable angles (±45° minimum)
- Returns to zero position safely
- No mechanical binding or hitting limits

### Full Data Collection (Batch)

For complete model fitting, collect multiple trajectories with different control gains:

**Board Controller (Recommended):**
```bash
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h \
    --speak
```

**Direct Serial:**
```bash
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h \
    --speak
```

This records **12 trajectories**:
- 4 trajectory types: `sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`
- 3 KP values: 8, 16, 32
- Duration: ~10-15 minutes total

The `--speak` flag announces each recording using `espeak` (optional).

### Command Reference

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--port` | Serial port | `/dev/ttyUSB0` |
| `--baudrate` | Communication speed | `115200` (default) |
| `--id` | Servo ID on bus | `1` (default) |
| `--mass` | Pendulum weight (kg) | `0.3` |
| `--length` | Arm length (m) | `0.12` |
| `--arm_mass` | Arm mass (kg) | `0.02` (optional) |
| `--motor` | Servo model | `htd45h`, `lx16a`, etc. |
| `--vin` | Supply voltage | `12.0` for HTD-45H |
| `--logdir` | Output directory | `data_raw_htd45h` |
| `--trajectory` | Trajectory name | `lift_and_drop` |
| `--kp` | Control gain | `32` |
| `--speak` | Voice announcements | flag |

## Data Collection Workflow

### Complete Pipeline

```bash
# 1. Collect raw data
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h

# 2. Process data (resample to constant dt)
python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 3. Verify data quality
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h

# 4. Fit simple model (baseline)
mkdir -p params/htd45h
python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m1.json \
    --trials 5000

# 5. Fit advanced model
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m6.json \
    --trials 20000

# 6. Validate results
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# 7. Generate friction diagram
python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```

## Expected Results

### Data Quality Indicators

Good quality data shows:
- Smooth position traces
- Consistent sampling rate (~100-200 Hz)
- Pendulum swings through ±45° minimum
- Clean return to zero position
- Stable voltage readings

### Model Performance

| Model | Description | Typical MAE | Parameters |
|-------|-------------|-------------|------------|
| M1 | Coulomb-Viscous | 0.05-0.08 rad | friction_base, friction_viscous, kt, R |
| M6 | Full friction model | 0.02-0.04 rad | M1 + Stribeck, load-dependent, directional, quadratic |

**Good fit**: M6 should reduce MAE by 50%+ compared to M1.

## Troubleshooting

### Hardware Issues

**Servo doesn't move:**
- Check 12V power supply is connected and ON
- Verify voltage with multimeter
- Ensure GND connections are solid
- Check servo LED is on

**Communication errors:**
- Verify correct serial port: `ls -l /dev/ttyUSB*`
- Check permissions: `sudo chmod 666 /dev/ttyUSB0`
- Try different baud rate: `--baudrate 9600`
- Verify servo ID: `--id 1` (default)

**Erratic movement:**
- Check stable power supply (use regulated supply, not battery)
- Verify all wiring connections
- Ensure proper grounding
- Reduce load if servo struggles

### Data Quality Issues

**High MAE / poor fit:**
- Verify accurate mass and length measurements
- Check pendulum swings freely (no binding)
- Ensure consistent power supply voltage
- Collect more diverse trajectories
- Increase optimization trials

**Noisy data:**
- Normal for Hiwonder servos (no velocity sensor)
- Will be filtered during processing
- Ensure stable mechanical setup
- Check for loose connections

### Board Controller vs Direct Serial

**When to use Board Controller:**
- Production data collection
- Multi-servo setups
- When reliability is critical
- Professional applications

**When to use Direct Serial:**
- Quick prototyping
- Single servo testing
- Budget constraints
- Learning/education

Both produce compatible data for BAM processing.

## Best Practices

### Hardware Setup
1. Use regulated power supply (not battery if possible)
2. Secure all mechanical connections
3. Ensure pendulum swings freely in full range
4. Mark zero position clearly
5. Verify no cable interference with movement

### Data Collection
1. Run test recording first to verify setup
2. Monitor servo temperature during batch collection
3. Let servo cool between long recordings
4. Check data quality with plot before fitting
5. Record ambient conditions (temperature, voltage)

### Optimization
1. Start with M1 model for baseline
2. Progress to M6 for best results
3. Use sufficient trials (5000 for M1, 20000+ for M6)
4. Validate with plots comparing sim vs real
5. Document fitted parameters

## Technical Details

### Available Trajectories

| Name | Description | Duration | Use Case |
|------|-------------|----------|----------|
| `sin_time_square` | Sine wave with time² | 10s | Varied acceleration |
| `sin_sin` | Double sine wave | 10s | Smooth oscillation |
| `lift_and_drop` | Lift up, free fall | 10s | Load transitions |
| `up_and_down` | Controlled up/down | 10s | Step responses |

### Control Parameters

**KP Values Tested**: 8, 16, 32
- Lower KP: More compliant, reveals friction at low speeds
- Higher KP: Stiffer, reveals high-speed dynamics
- Multiple values ensure diverse operating conditions

### Data Format

Logs saved as JSON:
```json
{
  "mass": 0.3,
  "length": 0.12,
  "motor": "htd45h",
  "kp": 32,
  "vin": 12.0,
  "trajectory": "sin_time_square",
  "controller": "board",
  "dt": 0.01,
  "entries": [
    {
      "timestamp": 0.0,
      "position": 0.0,
      "speed": 0.0,
      "goal_position": 0.0,
      "voltage": 12.0,
      "temperature": 25
    },
    ...
  ]
}
```

## Quick Reference

### HTD-45H (Primary Model)

**Specifications:**
- Voltage: 12V
- Torque: 45 kg·cm
- Current: 2-3A peak
- Protocol: Half-duplex serial, 115200 baud
- Position range: 0-1000 (0-240°)

**Recommended Setup:**
- Arm: 12 cm
- Weight: 300 g
- Total load moment: ~0.04 kg·m²

**Quick Commands:**
```bash
# Test
python -m bam.hiwonder.record_board --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
    --logdir test --trajectory lift_and_drop

# Full collection
python -m bam.hiwonder.all_record_board --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
    --logdir data_raw_htd45h
```

## Additional Documentation

- **Implementation details**: See `IMPLEMENTATION.md` for architecture
- **Full API reference**: See `README.md` for all features
- **Board controller guide**: See `BOARD_CONTROLLER_GUIDE.md` for protocol details
- **General BAM workflow**: See main `CLAUDE.md` and project README

## Summary Checklist

Before data collection:
- [ ] Hardware assembled correctly
- [ ] Power supply verified (12V for HTD-45H)
- [ ] Serial communication tested
- [ ] Pendulum parameters measured accurately
- [ ] Test recording successful

During data collection:
- [ ] Monitor servo temperature
- [ ] Check data quality after first few recordings
- [ ] Verify pendulum moves through full range
- [ ] Note any mechanical issues

After data collection:
- [ ] Process data with `bam.process`
- [ ] Visualize data with `bam.plot`
- [ ] Fit M1 model as baseline
- [ ] Fit M6 model for best results
- [ ] Validate with simulation comparison
- [ ] Document parameters and conditions
