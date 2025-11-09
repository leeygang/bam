# Hiwonder HTD-45H Servo for BAM

Support for the **Hiwonder HTD-45H** servo (12V, 45 kg·cm) in the BAM (Better Actuator Models) framework.

**IMPORTANT**: The HTD-45H must be controlled via the **Hiwonder Bus Servo Controller Board**. Direct serial communication is not supported.

## Quick Start

**For complete experimental setup including pendulum test bench**, see **[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md)**.

## HTD-45H Specifications

| Parameter | Value |
|-----------|-------|
| **Voltage** | 12V |
| **Torque** | 45 kg·cm |
| **Current** | 2-3A peak |
| **Gears** | Metal (industrial grade) |
| **Protocol** | Half-duplex serial, 115200 baud |
| **Motor name** | `htd45h` |

## Control Method

The HTD-45H servo **requires** control via the **Hiwonder Bus Servo Controller Board**:
- Reliable half-duplex serial communication
- Synchronized multi-servo control
- Built-in battery voltage monitoring
- Hardware-level servo control
- Safety features and error handling

**Details**: See [BOARD_CONTROLLER_GUIDE.md](BOARD_CONTROLLER_GUIDE.md)

## Usage Examples

### Test Recording
```bash
# Using uv (recommended)
uv run python -m bam.hiwonder.record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir test_data \
    --trajectory lift_and_drop

# Using regular python
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

### Batch Data Collection
```bash
# Using uv (recommended)
uv run python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h

# Using regular python
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h
```

**Records 12 trajectories** (4 types × 3 KP values) automatically in ~10-15 minutes.

## Standard BAM Workflow

After data collection:

```bash
# Using uv (recommended)

# 1. Process raw data
uv run python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 2. Fit baseline model (M1)
mkdir -p params/htd45h
uv run python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m1.json \
    --trials 5000

# 3. Fit advanced model (M6)
uv run python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m6.json \
    --trials 20000

# 4. Validate results
uv run python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# 5. Generate friction diagrams
uv run python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```

<details>
<summary>Using regular python (legacy)</summary>

```bash
# 1. Process raw data
python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 2. Fit baseline model (M1)
mkdir -p params/htd45h
python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m1.json \
    --trials 5000

# 3. Fit advanced model (M6)
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m6.json \
    --trials 20000

# 4. Validate results
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# 5. Generate friction diagrams
python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```
</details>

## Hardware Requirements

### Required Components
- **HTD-45H servo** (Hiwonder bus servo)
- **12V power supply** (2-3A capacity, regulated DC recommended)
- **Hiwonder Bus Servo Controller Board** (required)
- **USB cable** (for board to computer connection)
- **Pendulum components**:
  - Servo mount (bracket or base plate)
  - Arm: 10-15 cm aluminum tube or carbon fiber rod
  - End weight: 200-500 g (300 g recommended)
  - Fasteners and tools

### Installation
```bash
# Using uv (recommended)
uv pip install -e .

# Using pip (legacy)
pip install pyserial

# Linux: Add user to serial port group
sudo usermod -a -G dialout $USER
# Log out and back in for this to take effect

# Verify serial port
ls -l /dev/ttyUSB*   # Linux
ls -l /dev/tty.*     # macOS
```

## Documentation

| Document | Contents |
|----------|----------|
| **[EXPERIMENT_GUIDE.md](EXPERIMENT_GUIDE.md)** | Complete experimental setup: pendulum test bench, wiring, data collection |
| **[BOARD_CONTROLLER_GUIDE.md](BOARD_CONTROLLER_GUIDE.md)** | Board controller protocol details and advanced features |
| **[IMPLEMENTATION.md](IMPLEMENTATION.md)** | Technical implementation details and software architecture |

## Expected Results

| Model | Description | Expected MAE |
|-------|-------------|--------------|
| **M1** | Coulomb-Viscous (baseline) | 0.05-0.08 rad |
| **M6** | Full friction model | 0.02-0.04 rad (50% improvement) |

## Authors

- Yonatan Gu Li (HTD-45H implementation)
- Based on BAM framework by Rhoban team
