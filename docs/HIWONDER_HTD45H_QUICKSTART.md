# HTD-45H Quick Start Guide

Quick reference for using the Hiwonder HTD-45H servo (12V, 45 kg·cm) with BAM.

## Hardware Setup

### What You Need
- Hiwonder HTD-45H servo
- USB-to-TTL adapter (FTDI, CH340, CP2102)
- **12V power supply** (3S LiPo or regulated DC, 2-3A capacity)
- Pendulum arm: 10-15cm lightweight rod
- Weight: 200-500g

### Wiring
```
HTD-45H        USB-TTL       Power Supply
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Red     -----> (not connected)  -----> 12V+
Brown   -----> GND          -----> GND
Orange  -----> TX/RX (signal)
```

**IMPORTANT**: Power the servo from external 12V supply, NOT from USB!

## Quick Commands

### Test Recording (Single Trajectory)
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

### Full Data Collection (Batch)
```bash
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --motor htd45h \
    --vin 12.0
```

This records 12 trajectories automatically (~10-15 minutes).

### Process Data
```bash
python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005
```

### Fit Friction Model
```bash
# Create output directory
mkdir -p params/htd45h

# Fit M1 (simple model, fast)
python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m1.json \
    --trials 5000

# Fit M6 (advanced model, slower but better)
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m6.json \
    --trials 20000
```

### Validate Results
```bash
# Plot comparison
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# Generate friction diagram
python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```

## HTD-45H Specifications

| Parameter | Value |
|-----------|-------|
| Voltage | 12V (required) |
| Torque | 45 kg·cm @ 12V |
| Current | ~2-3A peak |
| Gears | Metal |
| Protocol | Half-duplex serial |
| Baud rate | 115200 |
| Position range | 0-1000 (0-240°) |

## Recommended Pendulum Setup

For best results with HTD-45H:

```
Pendulum Configuration:
  Servo: Mounted vertically
  Arm length: 12cm (0.12m)
  Arm material: Lightweight aluminum tube or carbon fiber
  End weight: 300g (0.3kg)
  Total mass: ~320g (including arm)
```

This provides good dynamic range without saturating the servo.

## Troubleshooting HTD-45H

### Servo doesn't move
- ✓ Check 12V power supply is connected and ON
- ✓ Verify voltage is actually 12V (use multimeter)
- ✓ Check current capacity (needs 2-3A)
- ✓ Ensure proper GND connection

### Communication errors
- ✓ Verify baud rate is 115200
- ✓ Check USB-TTL adapter is working
- ✓ Try different USB port
- ✓ Check servo ID (default is 1)

### Weak torque
- ✓ Ensure using 12V (not 6V or other voltage)
- ✓ Check power supply can provide enough current
- ✓ Verify wiring connections are solid
- ✓ Test with smaller load first

### High temperature
- HTD-45H can get warm under load
- Ensure adequate cooling/airflow
- Don't run continuously at high torque for extended periods
- Let servo rest between batch recordings

## Parameter Expectations

Initial parameters for HTD-45H (will be refined during fitting):

```python
kt (torque constant): ~4.4 Nm/A (based on 45 kg·cm spec)
R (resistance): ~3.5 Ohm
armature (inertia): ~0.008 kg·m²
```

After fitting, you should see:
- M1 MAE: ~0.05-0.08 rad
- M6 MAE: ~0.02-0.04 rad (50%+ improvement)

## Complete Workflow

1. **Setup**: Connect servo with 12V power
2. **Test**: Run single recording to verify
3. **Collect**: Run batch recording (12 trajectories)
4. **Process**: Resample to constant dt
5. **Fit M1**: Quick baseline model
6. **Fit M6**: Advanced friction model
7. **Validate**: Compare simulation vs real data
8. **Use**: Integrate fitted model into your simulation

## Tips for HTD-45H

- **Higher torque = better data**: HTD-45H's high torque captures friction effects well
- **Use appropriate loads**: 200-500g range is optimal
- **Stable power**: Use regulated supply, not battery (if possible)
- **Temperature**: Monitor servo temperature during batch recording
- **Mechanical setup**: Ensure pendulum swings freely, no binding

## Next Steps

After successful fitting with HTD-45H:

1. Compare M1 vs M6 model performance
2. Test in MuJoCo simulation (see `2R/` examples)
3. Validate on different trajectories
4. Share your parameters with the community
5. Try different operating conditions (voltage, temperature)

## Full Documentation

- Complete guide: `HIWONDER_SETUP_GUIDE.md`
- Detailed reference: `bam/hiwonder/README.md`
- Implementation details: `bam/hiwonder/IMPLEMENTATION.md`
- General BAM docs: `README.md` and `CLAUDE.md`

---

**Motor name**: `htd45h`
**Voltage**: 12V
**Recommended for**: BAM friction identification and research applications
