# Hiwonder Bus Servo Support for BAM

Support for Hiwonder bus servos in the BAM (Better Actuator Models) framework.

## Quick Start

**For complete experimental setup and data collection**, see **[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md)**.

## Supported Models

| Model | Voltage | Torque | Status | Motor Name |
|-------|---------|--------|--------|------------|
| **HTD-45H** | 12V | 45 kg·cm | ⭐ Primary | `htd45h` |
| LX-16A | 6V | 1.6 kg·cm | Supported | `lx16a` |
| LD-27MG | 7.4V | 27 kg·cm | Supported | `ld27mg` |
| LX-15D | 6V | 1.5 kg·cm | Supported | `lx15d` |

## Control Methods

### Method 1: Board Controller (Recommended ⭐)
Control via Hiwonder Bus Servo Controller Board:
- More reliable communication
- Synchronized multi-servo control
- Built-in battery voltage monitoring
- Hardware-level servo control

**See**: [BOARD_CONTROLLER_GUIDE.md](BOARD_CONTROLLER_GUIDE.md)

### Method 2: Direct Serial
Control via USB-to-TTL adapter:
- Lower cost
- Simpler for single servo
- Good for prototyping

**See**: [EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md)

## Usage Examples

### Test Recording (HTD-45H with Board Controller)
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

### Batch Data Collection (Recommended for Fitting)
```bash
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h
```

Records 12 trajectories (4 types × 3 KP values) automatically.

### Direct Serial Alternative
Replace `record_board` with `record` and `all_record_board` with `all_record`:
```bash
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h
```

## Standard BAM Workflow

After data collection:

```bash
# 1. Process raw data
python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 2. Fit friction model
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m6.json \
    --trials 20000

# 3. Validate results
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json
```

## Hardware Requirements

### Minimal Setup (HTD-45H)
- HTD-45H servo
- 12V power supply (2-3A capacity)
- USB-to-TTL adapter (for direct serial) OR Hiwonder Board Controller
- Pendulum arm: 10-15 cm
- Weight: 200-500 g

### Installation
```bash
pip install pyserial

# Linux: Add user to serial port group
sudo usermod -a -G dialout $USER
```

## Documentation

- **[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md)** - Complete experimental setup and data collection guide
- **[BOARD_CONTROLLER_GUIDE.md](BOARD_CONTROLLER_GUIDE.md)** - Board controller protocol and advanced features
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical implementation details and architecture

## Authors

- Yonatan Gu Li (Hiwonder implementation)
- Based on BAM framework by Rhoban team
