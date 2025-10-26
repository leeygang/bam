# Hiwonder Bus Servo Support for BAM

Support for Hiwonder bus servos in the BAM (Better Actuator Models) framework.

## Supported Models

### HTD-45H (High-Torque Industrial)
- **Voltage**: 12V (required)
- **Torque**: ~45 kg·cm @ 12V
- **Features**: Metal gears, industrial grade
- **Use case**: High-torque applications, robotic arms, primary model for BAM testing
- **Motor name**: `htd45h`

### LX-16A (Hobby - General Purpose)
- **Voltage**: 4.8V - 8.4V (6V recommended)
- **Torque**: ~1.6 kg·cm @ 6V
- **Speed**: ~0.12 sec/60° @ 6V
- **Weight**: 16.5g
- **Use case**: Lightweight hobbyist applications
- **Motor name**: `lx16a`

### LD-27MG (Hobby - High Torque)
- **Voltage**: 6V - 8.4V (7.4V recommended)
- **Torque**: ~27 kg·cm @ 7.4V
- **Speed**: ~0.16 sec/60° @ 7.4V
- **Weight**: 60g
- **Features**: Metal gears for durability
- **Use case**: Medium-duty hobbyist applications
- **Motor name**: `ld27mg`

### LX-15D (Hobby - Compact)
- **Voltage**: 4.8V - 8.4V (6V recommended)
- **Torque**: ~1.5 kg·cm @ 6V
- **Speed**: ~0.12 sec/60° @ 6V
- **Weight**: 15.5g
- **Use case**: Compact applications, similar to LX-16A
- **Motor name**: `lx15d`

## Hardware Requirements

### Wiring
Hiwonder servos use a 3-wire connection:
- **Red**: Power (VCC) - Connect to appropriate voltage (6V or 7.4V)
- **Brown/Black**: Ground (GND)
- **Orange/Yellow**: Signal (TX/RX) - Connect to USB-to-TTL adapter

### USB-to-TTL Adapter
You need a USB-to-serial adapter (FTDI, CH340, CP2102, etc.):
- **TX** on adapter → **Signal** on servo
- **RX** on adapter → **Signal** on servo (half-duplex)
- **GND** on adapter → **GND** on servo

**Important**: Some adapters may require a pull-up resistor on the signal line or a proper half-duplex circuit.

### Power Supply
- Use a regulated power supply matching your servo voltage
- **HTD-45H: 12V (can use 3S LiPo, ensure 2-3A capacity)**
- LX-16A/LX-15D: 6V (can use 2S LiPo)
- LD-27MG: 7.4V (can use 2S LiPo)
- Ensure adequate current capacity (HTD-45H needs more power due to higher torque)

## Installation

### Python Dependencies
```bash
pip install pyserial
```

### System Configuration (Linux)
```bash
# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER

# Install setserial for low latency (optional but recommended)
sudo apt install setserial

# Log out and back in for group changes to take effect
```

## Usage

### Single Recording

Record a single trajectory:

```bash
# For HTD-45H (12V, recommended for BAM testing)
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --trajectory sin_time_square \
    --motor htd45h \
    --kp 32 \
    --vin 12.0

# For LX-16A (6V, hobby servo)
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.1 \
    --length 0.08 \
    --logdir data_raw_lx16a \
    --trajectory sin_time_square \
    --motor lx16a \
    --kp 32 \
    --vin 6.0
```

**Arguments**:
- `--port`: Serial port (default: `/dev/ttyUSB0`)
- `--baudrate`: Baud rate (default: `115200`)
- `--id`: Servo ID (default: `1`)
- `--mass`: Mass of the pendulum load in kg (HTD-45H: 0.2-0.5kg, LX-16A: 0.05-0.15kg)
- `--length`: Length of the pendulum in meters (HTD-45H: 0.10-0.15m, LX-16A: 0.06-0.10m)
- `--arm_mass`: Mass of the pendulum arm in kg (default: `0.0`)
- `--logdir`: Directory to save log files
- `--trajectory`: Trajectory name (`sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`)
- `--motor`: Motor model (`htd45h`, `lx16a`, `ld27mg`, `lx15d`)
- `--kp`: Proportional gain (default: `32`)
- `--vin`: Input voltage in volts (HTD-45H: `12.0`, LX-16A/LX-15D: `6.0`, LD-27MG: `7.4`)

### Batch Recording

Record multiple trajectories and KP values automatically:

```bash
# For HTD-45H (recommended)
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --motor htd45h \
    --vin 12.0 \
    --speak

# For LX-16A (hobby servo)
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.1 \
    --length 0.08 \
    --logdir data_raw_lx16a \
    --motor lx16a \
    --vin 6.0 \
    --speak
```

This will automatically record:
- 4 trajectories: `sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`
- 3 KP values: 8, 16, 32
- Total: 12 recordings

The `--speak` flag (optional) announces each recording using `espeak`.

## Data Processing and Model Fitting

After recording, follow the standard BAM workflow:

### 1. Post-process Raw Data
```bash
python -m bam.process \
    --raw data_raw_lx16a \
    --logdir data_processed_lx16a \
    --dt 0.005
```

### 2. Fit Friction Model
```bash
# Start with simple model (M1)
python -m bam.fit \
    --actuator lx16a \
    --model m1 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m1.json \
    --trials 10000

# Progress to advanced models (M4, M6)
python -m bam.fit \
    --actuator lx16a \
    --model m6 \
    --logdir data_processed_lx16a \
    --method cmaes \
    --output params/lx16a/m6.json \
    --trials 50000
```

### 3. Visualize Results
```bash
python -m bam.plot \
    --actuator lx16a \
    --logdir data_processed_lx16a \
    --sim \
    --params params/lx16a/m6.json
```

### 4. Generate Drive/Backdrive Diagrams
```bash
python -m bam.drive_backdrive \
    --params params/lx16a/m6.json \
    --max_torque 15
```

## Testbench Setup

Build a simple pendulum testbench:

1. **Mount the servo** vertically on a stable base
2. **Attach a pendulum arm** to the servo horn (lightweight rod/tube)
3. **Add a weight** at the end of the arm
4. **Ensure free movement**: The pendulum should swing freely ±90° from vertical
5. **Mark zero position**: Pendulum hanging straight down = 0 radians

**Example dimensions**:
- Arm length: 8-12 cm
- End mass: 50-200g (depending on servo)
- For LX-16A: 50-100g mass, 8-10cm arm
- For LD-27MG: 100-300g mass, 10-15cm arm

## Troubleshooting

### Serial Port Issues
```bash
# Check if port exists
ls -l /dev/ttyUSB*

# Test port permissions
sudo chmod 666 /dev/ttyUSB0  # Temporary fix
# OR add user to dialout group (permanent)
sudo usermod -a -G dialout $USER
```

### Communication Errors
- Verify baud rate (should be 115200 for most Hiwonder servos)
- Check servo ID (default is 1, can be changed with servo software)
- Ensure proper wiring and power supply
- Try reducing baud rate to 9600 if issues persist

### No Servo Movement
- Check that servo is powered (LED should be on)
- Verify voltage is within spec (6V for LX-16A, 7.4V for LD-27MG)
- Test servo with Hiwonder's official software first
- Ensure torque is enabled in the code

### Speed Measurement
Hiwonder basic servos don't provide direct speed measurement. The code estimates speed from position changes between samples. For better speed estimates:
- Use higher sampling rates
- Ensure consistent timing
- Filter position data if noisy

## Protocol Notes

Hiwonder servos use a proprietary half-duplex serial protocol:
- **Packet format**: `[0x55, 0x55, ID, Length, Command, Params..., Checksum]`
- **Position range**: 0-1000 (typically 0-240 degrees)
- **Checksum**: `~(sum of bytes from ID to last param) & 0xFF`

The implementation in `hiwonder.py` handles all protocol details automatically.

## Parameter Refinement

The initial parameter values in `actuator.py` are estimates. After collecting data and fitting:

1. Compare fitted parameters to initial values
2. Update `actuator.py` with better initial values for faster convergence
3. Iterate with new data if needed

Key parameters to refine:
- `kt` (torque constant): Affects torque production
- `R` (resistance): Affects motor dynamics
- `armature` (rotor inertia): Affects acceleration response
- `error_gain`: Affects control loop behavior

## Integration with MuJoCo

To use fitted models in MuJoCo simulations, see the main BAM documentation and the `2R/` validation examples.

## Contributing

If you identify parameters for other Hiwonder servo models, please contribute them back to the project!

## Authors
- Yonatan Gu Li (Initial Hiwonder implementation)
- Based on BAM framework by Rhoban team
