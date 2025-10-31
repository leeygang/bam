# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BAM (Better Actuator Models) is a research project for identifying and simulating extended friction models for servo actuators. The project enables accurate modeling of actuator friction beyond the basic Coulomb-Viscous model (M1), including Stribeck effects, load-dependence, and quadratic friction (M2-M6). This improves sim-to-real transfer for robotics applications, particularly in Reinforcement Learning.

## Core Architecture

### Model-Actuator-Testbench Trinity

The codebase is organized around three interconnected abstractions:

1. **Model** (`bam/model.py`): Defines friction models (M1-M6) with varying complexity
   - M1: Basic Coulomb-Viscous (baseline)
   - M2: Adds Stribeck friction
   - M3: Adds load-dependent friction
   - M4: Stribeck + load-dependent
   - M5: M4 + directional friction
   - M6: M5 + quadratic effects (most complete)
   - Models contain optimizable `Parameter` objects that get fitted during identification
   - `compute_frictions()` calculates frictionloss and damping based on motor/external torques

2. **Actuator** (`bam/actuator.py`): Represents physical servo motors
   - Base class defines interface: `compute_control()` and `compute_torque()`
   - `VoltageControlledActuator`: Models DC motors with back-EMF (kt, R parameters)
   - Specific implementations: `MXActuator` (Dynamixel), `ErobActuator`, `STS3215Actuator`, `UnitreeGo1Actuator`, `HiwonderLX16AActuator` (Hiwonder servos)
   - Each actuator is registered in `bam/actuators.py` dictionary

3. **Testbench** (`bam/testbench.py`): Physical test setup (pendulum in this case)
   - `compute_mass()`: Returns system inertia
   - `compute_bias()`: Returns gravitational torque
   - The `Pendulum` class implements inverse dynamics for a weighted pendulum

These three components combine: a Model uses an Actuator which uses a Testbench to simulate dynamics.

### Simulation Pipeline

The `Simulator` class (`bam/simulate.py`) integrates dynamics:
1. Computes bias torque from testbench
2. Computes motor torque from actuator model
3. Computes friction from the model
4. Integrates equations of motion (semi-implicit Euler)
5. `rollout_log()` replays recorded trajectories through the simulator

### Parameter Optimization

The `bam/fit.py` script uses Optuna to optimize model parameters:
- Loads processed logs from `--logdir`
- Creates a model with `models[model_name]()` and actuator
- Objective function: Mean Absolute Error between simulated and real positions
- Supports multiple optimization methods: `cmaes`, `random`, `nsgaii`
- Outputs fitted parameters to JSON (e.g., `params/mx106/m6.json`)

## Key Commands

### Installation
```bash
# For identification/fitting work
pip install -r requirements_bam.txt

# For 2R validation work
pip install -r requirements_2R.txt
```

### Data Collection Workflow

**Dynamixel Recording:**
```bash
# Single trajectory
python -m bam.dynamixel.record \
    --port /dev/ttyUSB0 \
    --mass 0.567 \
    --length 0.105 \
    --logdir data_raw \
    --trajectory sin_time_square \
    --motor mx106 \
    --kp 8 \
    --vin 15.0

# Batch recording (modify script for specific trajectories/kp values)
python -m bam.dynamixel.all_record \
    --port /dev/ttyUSB0 \
    --mass 0.567 \
    --length 0.105 \
    --logdir data_raw \
    --motor mx106 \
    --speak
```

**eRob Recording (requires Etherban server):**
```bash
# First compile protobuf definitions
cd bam/erob/
bash generate_protobuf.sh

# Monitor devices and find angular offset
python -m bam.erob.etherban

# Record trajectory
python -m bam.erob.record \
    --host 127.0.0.1 \
    --offset 1.57 \
    --mass 2.0 \
    --arm_mass 1.0 \
    --length 0.105 \
    --logdir data_raw \
    --trajectory sin_time_square \
    --motor erob100 \
    --kp 8 \
    --damping 0.1
```

**Available trajectories:** `sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`, `nothing`

### Hiwonder Servos

Hiwonder bus servos (HTD-45H, LX-16A, LD-27MG, LX-15D) are supported with **two control methods**:

**Method 1: Board Controller (Recommended ⭐)**
- More reliable, synchronized control via Hiwonder Bus Servo Controller Board
- See `bam/hiwonder/BOARD_CONTROLLER_GUIDE.md`

**Method 2: Direct Serial**
- Direct control via USB-to-TTL adapter

**Quick start (HTD-45H with Board Controller):**
```bash
# Single recording
python -m bam.hiwonder.record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --trajectory sin_time_square \
    --motor htd45h \
    --vin 12.0

# Batch recording (all trajectories and KP values)
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --motor htd45h \
    --vin 12.0
```

**Quick start (Direct Serial - alternative):**
```bash
# Use record.py and all_record.py instead of record_board.py
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --logdir data_raw_htd45h \
    --trajectory sin_time_square \
    --motor htd45h \
    --vin 12.0
```

**Supported motors:** `htd45h` (12V, 45 kg·cm), `lx16a` (6V), `ld27mg` (7.4V), `lx15d` (6V)

**Hardware options:**
- **Board Controller**: Hiwonder Bus Servo Controller Board (recommended)
- **Direct Serial**: USB-to-TTL adapter (FTDI, CH340, CP2102)
- **HTD-45H: 12V power required** (primary model for testing)
- LX-16A/LX-15D: 6V, LD-27MG: 7.4V

### Processing and Fitting

```bash
# Post-process raw data (interpolate to constant timestep)
python -m bam.process \
    --raw data_raw \
    --logdir data_processed \
    --dt 0.005

# Fit friction model
python -m bam.fit \
    --actuator mx106 \
    --model m6 \
    --logdir data_processed \
    --method cmaes \
    --output params/mx106/m6.json \
    --trials 1000

# Plot results (compare simulation vs real)
python -m bam.plot \
    --actuator mx106 \
    --logdir data_processed \
    --sim \
    --params params/mx106/m6.json
```

### 2R Arm Validation

The `2R/` directory contains MuJoCo-based validation on 2-degree-of-freedom arms:

```bash
# Record 2R trajectory (Dynamixel)
python -m bam.dynamixel.record_2R \
    --port /dev/ttyUSB0 \
    --mass 0.567 \
    --logdir data_2R_dyn \
    --trajectory circle \
    --kp 8 \
    --speed 1.0

# Simulate and compare
python -m 2R.sim \
    --log data_2R_dyn/circle.json \
    --params params/mx106/m4.json,params/mx64/m4.json \
    --testbench mx \
    --render \
    --plot \
    --mae

# Batch MAE computation
./2R/mae.sh mx data_2R_dyn/*
```

**2R trajectories:** `circle`, `square`, `square_wave`, `triangular_wave`

## MuJoCo Integration

### MujocoController
The `MujocoController` class (`bam/mujoco.py`) bridges BAM models into MuJoCo simulations:
- Updates actuator torque each timestep via `mujoco_data.ctrl`
- Dynamically adjusts `dof_frictionloss` and `dof_damping` based on model
- Reads external torques from `qfrc_bias` and `qfrc_constraint`
- Use `load_config()` to load multiple controllers from JSON

### Converting Models to MuJoCo Parameters
Some actuators implement `to_mujoco()` to print equivalent MuJoCo XML parameters:
- Converts BAM friction model to MuJoCo's built-in actuator parameters
- Only approximates M1 model (MuJoCo doesn't support advanced friction)

### URDF to MuJoCo Conversion
See `2R/README.md` for the conversion procedure:
- Remove `package:///` prefixes
- Add `<compiler fusestatic="false"/>`
- Use `~/.mujoco/mujoco-3.1.1/bin/compile` to convert
- Manually add sites, actuators, and adjust collision settings

## Parameter Files

Fitted parameters are stored as JSON in `params/{actuator}/{model}.json`:
```json
{
  "model": "m6",
  "actuator": "mx106",
  "friction_base": 0.123,
  "kt": 0.456,
  "R": 7.89,
  ...
}
```

Load with: `model = load_model("params/mx106/m6.json")`

## Important Implementation Details

### Friction Computation Logic
The core friction calculation in `Model.compute_frictions()`:
- Computes gearbox torque from motor vs external torque
- Applies Stribeck exponential decay: `exp(-(|dq/dq_stribeck|^alpha))`
- For directional models (M5, M6): separate coefficients for motor vs external torque
- Static friction uses `tau_stop` to determine if motion should stop

### Control Flow
1. Real hardware sends position/torque data → saved to JSON logs
2. `bam.process` resamples logs to constant dt
3. `bam.fit` optimizes `Parameter` values by simulating logs and minimizing MAE
4. Fitted parameters saved to `params/` directory
5. `bam.plot` or `2R.sim` validates by comparing simulation to real data

### Log Format
Logs are JSON dictionaries with:
- `mass`, `length`, `arm_mass`: pendulum properties
- `kp`, `vin`: controller parameters
- `dt`: timestep
- `entries`: list of `{timestamp, position, speed, goal_position, torque_enable, ...}` dicts

### Adding New Actuators
1. Create actuator class in `bam/{vendor}/actuator.py` extending `Actuator` or `VoltageControlledActuator`
2. Implement `initialize()` to add model parameters
3. Implement `compute_control()` and `compute_torque()` (or use base class defaults)
4. Implement `get_extra_inertia()` to return rotor inertia
5. Register in `bam/actuators.py` dictionary
6. Create recording script based on `bam/dynamixel/record.py` template

### Module Execution Pattern
Most scripts use `if __name__ == "__main__":` with argparse at module level. Always run as modules:
```bash
python -m bam.fit ...     # Correct
python bam/fit.py ...     # Will fail due to relative imports
```
