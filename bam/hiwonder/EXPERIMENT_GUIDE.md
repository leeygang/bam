# HTD-45H Servo Experiment Guide

Complete guide for collecting friction identification data with the Hiwonder HTD-45H servo in BAM.

## First Time? Start Here! 👋

**Never done this before?** Follow these steps in order:

1. ✅ **Watch the video** (10 minutes): https://youtu.be/5XPEEKDnQEM
   - You'll see exactly what we're building and how it works
   - Much easier to understand after seeing it in action!

2. ✅ **Read this guide** (20 minutes)
   - Come back here after watching the video
   - Things will make much more sense

3. ✅ **Order components** (see "Where to Buy Components" section below)
   - HTD-45H servo, power supply, and mechanical parts

4. ✅ **Follow the step-by-step instructions** (2-3 hours)
   - We'll walk you through everything

**Don't worry if it seems complicated** - the video makes it much clearer! Many people have successfully built this setup with no prior robotics experience.

## Overview

This guide covers the complete experimental setup for using the **Hiwonder HTD-45H** servo (12V, 45 kg·cm) for friction model identification. The HTD-45H is an industrial-grade bus servo with metal gears, suitable for accurate friction characterization.

**IMPORTANT**: The HTD-45H must be controlled via the **Hiwonder Bus Servo Controller Board**. Direct serial communication is not supported for this servo.

### Visual References (Highly Recommended!)

**Before you start**, watch and review these resources to see what the setup looks like:

1. **Video Tutorial** (HIGHLY RECOMMENDED - watch first!):
   - https://youtu.be/5XPEEKDnQEM
   - Shows the actual pendulum testbench, how it moves, and what data collection looks like
   - You'll see the exact setup we're trying to replicate with HTD-45H

2. **Research Paper** (has photos):
   - https://arxiv.org/pdf/2410.08650v1
   - Check Figures showing the pendulum setup and experiment photos
   - Look for images of servo mounted vertically with pendulum arm

3. **Main README.md**:
   - See `README.md` in this repository
   - Contains photos of Dynamixel setup (same concept applies to HTD-45H)
   - Shows what the pendulum looks like: https://github.com/user-attachments/assets/be9176e3-2aa7-4476-9d2b-88ffca177eb1

**What you'll build**: A simple pendulum (weight on a stick) attached to a servo motor standing upright. The servo controls the pendulum motion while we record position and friction data.

### Complete Workflow Timeline

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: PREPARATION (1-2 hours)                       │
├─────────────────────────────────────────────────────────┤
│  1. Order/acquire all components                        │
│  2. Install software (Python, dependencies)             │
│  3. Build pendulum test bench                           │
│  4. Wire electronics                                    │
│  5. Verify setup with power/communication tests         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 2: DATA COLLECTION (20-30 minutes)               │
├─────────────────────────────────────────────────────────┤
│  6. Run test recording (verify everything works)        │
│  7. Run batch recording (12 trajectories)               │
│  8. Monitor servo temperature, check for issues         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 3: DATA PROCESSING (1-2 hours)                   │
├─────────────────────────────────────────────────────────┤
│  9. Process raw data (resample to constant dt)          │
│ 10. Fit M1 model (baseline, ~10 min)                    │
│ 11. Fit M6 model (advanced, ~30-60 min)                 │
│ 12. Validate with plots (visual comparison)             │
│ 13. Generate friction diagrams                          │
└─────────────────────────────────────────────────────────┘
                          ↓
                  ✓ DONE! Parameters ready for use
```

**Total time estimate:** 3-5 hours (mostly waiting for optimization)

**Important Note:** This pendulum experiment is **sufficient** to get calibrated friction parameters for the HTD-45H. The optional 2R arm validation (seen in the main BAM paper) is **NOT required** - it's only for validating parameters on multi-joint robot arms. After completing this guide, you'll have fully usable parameters.

## Required Equipment

### Where to Buy Components

**HTD-45H Servo:**
- Hiwonder official store (AliExpress, official website)
- Search: "Hiwonder HTD-45H bus servo" or "HTD-45H 12V servo"
- Comes with: Servo, horn(s), mounting screws, cable

**Control Hardware:**
- **Hiwonder Bus Servo Controller Board**: Required (Hiwonder store - search "bus servo controller board")
- **USB cable**: USB-A to USB-B or USB-C (for board to computer connection)
- **12V power supply**: Any electronics supplier (must provide 2-3A)

**Mechanical parts:**
- **Aluminum tube**: Hardware store (8-12mm OD, ~30cm length, cut to size)
- **Weights**: Hardware store (washers, bolts, nuts) or fishing supply (fishing weights)
- **Mounting hardware**: Hardware store (L-brackets, base plates, screws)

### Electronics
- **HTD-45H servo** (Hiwonder bus servo) - typically includes servo horn
- **12V power supply** (2-3A minimum capacity, regulated DC bench supply recommended)
- **Hiwonder Bus Servo Controller Board** (required for HTD-45H control)
- **USB cable** (for board to computer connection)
- **Cables**: Power cables with alligator clips or terminals, jumper wires if needed

### Mechanical Components for Pendulum
- **Servo mount/base**: Stable mounting bracket or base plate
- **Pendulum arm**: 10-15 cm lightweight rod
  - Recommended: Aluminum tube (8-12 mm diameter) or carbon fiber rod
  - Alternative: Wooden dowel, plastic rod (must be rigid)
- **End weight**: 200-600 g mass (recommended: 300 g)
  - Options: Metal cylinder, bolt with nuts, fishing weight
  - Must be securely attachable to arm end
  - **Note**: 1.3 lb (~590 g) is safe and works well with HTD-45H
- **Servo horn/adapter**: Connects pendulum arm to servo output shaft
- **Fasteners**: Screws, bolts, or strong adhesive to attach arm to horn
- **Optional**: Bearing or bushing for smoother rotation (if not using servo horn directly)

### Tools & Supplies
- Screwdriver set
- Drill (if making mounting holes)
- Scale (for weighing end mass and arm)
- Ruler or caliper (for measuring arm length)
- Multimeter (for verifying voltage)
- Zip ties or tape (for cable management)

## Pendulum Test Bench Setup

### Complete Setup Overview

Here's what the final setup looks like:

```
                    Computer
                       |
                    [USB]
                       |
    ┌──────────────────┴──────────────────┐
    │                                     │
    │  Board Controller    OR    USB-TTL  │
    │        |                      |     │
    └────────┼──────────────────────┼─────┘
             │                      │
          [Cable]               [Cable]
             │                      │
             ↓                      ↓
         HTD-45H ←──[12V]──← Power Supply
           Servo      [GND]
             |
             ↓ (output shaft)
           [Horn]
             |
             ↓
         [12cm Arm]
             |
             ↓
         [300g Weight]
```

**Key measurements for this guide:**
- Arm length: **12 cm** (0.12 m)
- End mass: **300 g** (0.3 kg)
- Supply voltage: **12V**
- Control gain (KP): **8, 16, 32** (tested automatically)

### Step 1: Prepare the Servo Mount

The servo must be mounted **vertically** with the output shaft pointing upward.

**Real-world analogy:** Think of a ceiling fan - the motor is mounted to the ceiling, and the blades hang down. For our setup, the servo is like the motor (mounted firmly), and the pendulum arm hangs down like a single blade.

**Visual reference:** See the BAM paper and video for photos of the actual setup:
- **Paper**: https://arxiv.org/pdf/2410.08650v1 (Figure showing pendulum setup)
- **Video**: https://youtu.be/5XPEEKDnQEM (Shows real testbench)
- **README images**: See main README.md for photos of Dynamixel setup (same concept for HTD-45H)

**What "vertical" means:**
```
    Side View (imagine looking at the setup from the side):

    Pendulum arm (hangs down) ──────┐
                                    ↓
                           ┌────────────────┐
                           │   Servo Horn   │  ← Disc attached to servo shaft
                           └────────────────┘
                                    │
                                    │ Servo shaft (rotation axis)
                           ┌────────────────┐
                           │                │
                           │    HTD-45H     │  ← Servo body (rectangular box)
                           │     Servo      │     stands upright like a tower
                           │                │
                           └────────────────┘
                                    │
    ═══════════════════════════════════════  ← Table/base (horizontal)
                   (stable surface)
```

**In simple terms:**
1. Your **table** is horizontal (flat)
2. The **servo body** stands upright on the table (like a can standing up)
3. The **servo shaft** points up toward the ceiling
4. The **pendulum arm** hangs down from the shaft (pulled by gravity)

**Mounting options:**

1. **Heavy base plate** (Simplest, recommended for beginners)
   - Use thick wood board (>20mm) or metal plate (>10mm)
   - Dimensions: 20cm × 20cm minimum
   - Bolt servo to center using servo mounting holes (typically 4 holes)
   - Use M3 or M4 screws (check servo mounting holes)
   - Add rubber feet or C-clamp plate to table for stability
   - Weight: >1 kg for stability (add weights if needed)

2. **L-bracket mount** (Professional, rigid)
   - Use metal L-bracket (aluminum or steel, 90° angle)
   - One leg bolted to table/workbench (horizontal)
   - Other leg holds servo (vertical)
   - Bracket should be sturdy (>2mm thickness)
   - Bolt servo mounting holes to vertical leg of bracket

3. **3D-printed custom mount** (If you have 3D printer)
   - Design vertical tower with servo mounting holes
   - Include wide base for stability
   - Print with >50% infill for strength
   - Material: PLA, PETG, or ABS
   - May need to add weight to base

4. **C-clamp mount** (Quick setup, portable)
   - Clamp heavy bracket to table edge
   - Bolt servo to bracket
   - Ensure clamp is extremely tight (will resist torque)
   - Test: servo should not budge when you pull on it

**Critical requirements:**
- Servo must **not move** or vibrate during operation (test by pulling on servo body)
- Output shaft must be **vertical** (±5° tolerance - use level or visual check)
- Base must be heavy/secured enough to resist torque reactions
- Minimum **15 cm clearance** around servo for ±120° pendulum swing
- Mounting screws must be **tight** (check periodically)

**HTD-45H mounting hole pattern:**
- Check servo body for mounting holes (typically 4 holes in square pattern)
- Hole size: Usually M3 or M4 threaded
- Spacing: ~30-40mm between holes (measure your specific servo)
- Use appropriate length screws (typically 8-12mm)

### Step 2: Build the Pendulum Arm

The pendulum consists of a lightweight arm with a concentrated mass at the end.

#### Arm Construction

**Option A: Aluminum Tube (Recommended)**
1. Cut aluminum tube to 12 cm length (outside diameter 8-10 mm)
2. Drill hole at one end to fit servo horn screw
3. Drill hole or tap threads at other end for weight attachment
4. Weigh the arm (typical: 10-30 g)

**Option B: Wooden Dowel**
1. Cut wooden dowel to 12 cm length (diameter 6-10 mm)
2. Sand one end flat for servo horn mounting
3. Drill pilot holes for screws
4. Weigh the arm

**Option C: 3D Printed**
1. Design arm with mounting holes on both ends
2. Print with lightweight filament (PLA, PETG)
3. Keep wall thickness minimal (2-3 mm)
4. Weigh the arm

#### Weight Attachment

The end mass should be 200-600 g, concentrated as much as possible. **1.3 lb (~590 g) is perfectly safe!**

**Options:**
1. **Metal cylinder**: Drill hole through center, slide onto arm, secure with set screw
2. **Stacked washers**: Thread large washers onto bolt, secure with nuts
3. **Fishing weight**: Clamp-on type or bolt-through
4. **Custom weight**: Machine or cast metal piece

**Weight mounting:**
```
Top View:
    [Servo Horn]
         |
         |_____ (12 cm arm)
         |
    [Weight 300g]
```

**Critical requirements:**
- Weight must be **securely fastened** (will experience significant forces)
- Center of mass should be at arm tip (not offset laterally)
- Total weight: 200-500 g (300 g recommended)
- Arm must be balanced (not twisted or bent)

### Step 3: Measure Pendulum Parameters

Accurate measurements are **critical** for friction identification.

#### Length Measurement

Measure distance from **servo rotation axis** to **center of mass** of end weight:

```
    ┌─── Servo shaft axis (rotation center)
    │
    ├────────────────┐
    │   (arm)        │
    └────────────────┘
                     ↓
              [Weight center of mass]

    ◄────── L ──────►
```

**How to measure:**
1. Measure from servo shaft center to weight attachment point
2. Add half the weight's length/diameter (approximates center of mass)
3. Example: 10 cm arm + 2 cm weight radius = **12 cm = 0.12 m**

**Typical value**: `--length 0.12` (12 cm)

#### Mass Measurement

**End mass** (the weight at the tip):
1. Weigh the end weight alone with scale
2. Typical: 200-500 g
3. Example: **300 g = 0.3 kg**

**Typical value**: `--mass 0.3` (300 g)

**Arm mass** (optional but improves accuracy):
1. Weigh the arm alone with scale
2. Typical: 10-30 g for aluminum tube
3. Example: **20 g = 0.02 kg**

**Typical value**: `--arm_mass 0.02` (20 g, optional)

### Step 4: Attach Arm to Servo

1. **Mount servo horn** to servo output shaft
   - HTD-45H comes with included servo horn (disc or cross-shaped)
   - Align horn splines with servo shaft splines
   - Press horn firmly onto shaft
   - Secure with center screw (typically M3 or M4)
   - Tighten firmly but don't strip threads
   - Ensure no wobble or play in horn

2. **Attach pendulum arm** to servo horn
   - Servo horn has multiple mounting holes arranged radially
   - Choose holes that align with your arm
   - Use **2-3 screws** through horn holes into arm for security
   - **Critical**: Arm must be **perpendicular** to horn plane (90°)
   - Check arm is **centered** and balanced (not offset)
   - If using aluminum tube: may need to flatten/drill one end
   - If using wooden dowel: pre-drill pilot holes to prevent splitting
   - Alternative: Use strong epoxy/adhesive + mechanical fastener

3. **Verify zero position**
   - Power OFF the servo initially
   - Let pendulum hang down naturally under gravity
   - Pendulum should point straight down (0 radians reference)
   - Mark this position on the base/table with tape or marker
   - Note the servo horn orientation at zero (for reassembly)

4. **Test range of motion**
   - Manually swing pendulum ±90° from vertical (servo unpowered)
   - Check for smooth rotation throughout range
   - Ensure no cable interference with pendulum
   - Verify weight doesn't hit base/table at extremes
   - Listen for any grinding, clicking, or binding sounds
   - Pendulum should swing freely and return to center

### Step 5: Electrical Wiring

The HTD-45H servo must be controlled via the Hiwonder Bus Servo Controller Board:

```
┌──────────────────────────────────────────────┐
│  Hiwonder Bus Servo Controller Board         │
│                                               │
│  USB Port ──────────► Computer               │
│                                               │
│  Power Input:                                │
│    [12V] ◄────────── 12V Power Supply (+)    │
│    [GND] ◄────────── Power Supply GND (-)    │
│                                               │
│  Servo Port 1:                               │
│    [Signal/Power] ◄─── HTD-45H Cable         │
│                                               │
└──────────────────────────────────────────────┘
```

**Wiring Steps:**
1. Connect 12V power supply to board power input (observe polarity!)
2. Connect HTD-45H servo cable to Port 1 on board
3. Connect USB cable from board to computer
4. Verify board power LED is ON

**CRITICAL SAFETY**:
- **Never** power servo from USB (insufficient current, will damage USB)
- Always use external 12V power supply
- Double-check polarity before powering on

### Step 6: Verify Setup

Before data collection, verify everything works:

1. **Power check**
   - **Before powering on**: Double-check all connections (polarity!)
   - Connect power supply, turn ON
   - Measure voltage at servo with multimeter: should be **~12V**
   - Check servo LED is ON (if equipped - small LED on servo body)
   - **First power-on**: Servo may move slightly to initialization position (normal)
   - Pendulum should remain relatively stationary or move gently

2. **Communication test**
   ```bash
   # Linux: Check serial port appears
   ls -l /dev/ttyUSB*
   # Should show: /dev/ttyUSB0 or /dev/ttyUSB1

   # macOS: Check serial port
   ls -l /dev/tty.usbserial*
   # Should show: /dev/tty.usbserial-XXXXXXXX

   # Check permissions (Linux)
   # If you see "Permission denied", run:
   sudo chmod 666 /dev/ttyUSB0
   ```

3. **Movement test** (run test recording in next section)
   - Servo responds to commands
   - Pendulum swings smoothly
   - Returns to zero position (hanging down)
   - No mechanical binding or wobble
   - No unusual sounds (grinding, clicking)

**What to expect when it works:**
- Terminal shows "Recording..." or similar
- Servo hums quietly during motion
- Pendulum moves smoothly through commanded trajectory
- Data is logged (timestamps, positions printed to terminal)
- At end, servo gently returns pendulum to zero (hanging down)

**Red flags (stop and troubleshoot):**
- Servo doesn't move at all
- Loud grinding or clicking sounds
- Pendulum jerks violently
- Error messages about communication timeout
- Servo gets very hot (>70°C) quickly

## Software Installation

**Using uv (recommended):**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install BAM with dependencies
uv pip install -e .

# Linux: Add user to serial port group (for permissions)
sudo usermod -a -G dialout $USER
# IMPORTANT: Log out and back in for this to take effect

# macOS: No special permissions needed

# Verify serial port is accessible
ls -l /dev/ttyUSB*   # Linux
ls -l /dev/tty.*     # macOS
```

**Using pip (legacy):**
```bash
# Install required Python packages
pip install pyserial

# Linux: Add user to serial port group (for permissions)
sudo usermod -a -G dialout $USER
# IMPORTANT: Log out and back in for this to take effect

# macOS: No special permissions needed

# Verify serial port is accessible
ls -l /dev/ttyUSB*   # Linux
ls -l /dev/tty.*     # macOS
```

## Running Experiments

### Test Recording (Verify Setup)

Before collecting full dataset, run a single test recording to verify hardware setup:

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

**What happens during test recording (step-by-step):**

1. **Initialization** (~2 seconds)
   - Script connects to servo
   - Terminal shows: "Connected to servo on /dev/ttyUSB0"
   - Servo enables torque (you may hear a slight hum)
   - Pendulum may move slightly to hold position

2. **Trajectory execution** (~10 seconds for `lift_and_drop`)
   - Servo lifts pendulum upward smoothly
   - Reaches peak (~45-90° from vertical)
   - Torque disables → pendulum drops under gravity
   - Pendulum swings freely through several oscillations
   - Data logged continuously (~100-200 samples/sec)

3. **Return to zero** (~3-5 seconds)
   - Servo re-enables torque
   - Gently brings pendulum to hanging-down position
   - Uses damped control to avoid oscillations

4. **Completion**
   - Servo disables torque (pendulum hangs freely)
   - Terminal shows: "Recording complete"
   - Data saved to `test_data/lift_and_drop_kp32.json`
   - Total duration: ~15-20 seconds

**What you should observe:**
- Pendulum lifts smoothly (no jerking)
- Drop phase: pendulum swings freely like a real pendulum
- Return phase: controlled movement back to center
- Terminal prints timestamps and positions continuously
- No error messages or communication timeouts

**Checklist after test:**
- [ ] Servo responds to commands
- [ ] Pendulum swings through ±45° minimum
- [ ] Movement is smooth (no jerking or binding)
- [ ] Returns to zero safely
- [ ] No error messages
- [ ] Log file created in `test_data/` directory
- [ ] File size is reasonable (>10 KB for 10-second trajectory)

### Full Data Collection (Batch Recording)

Once test recording succeeds, collect complete dataset for model fitting:

```bash
# Using uv (recommended)
uv run python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 \
    --id 1 \
    --mass 0.3 \
    --length 0.12 \
    --motor htd45h \
    --vin 12.0 \
    --logdir data_raw_htd45h \
    --speak

# Using regular python
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

**What this does:**
- Records **12 trajectories** automatically
- 4 trajectory types: `sin_time_square`, `sin_sin`, `lift_and_drop`, `up_and_down`
- 3 control gains (KP): 8, 16, 32
- Each recording: ~20-30 seconds
- Total duration: ~10-15 minutes
- Optional `--speak` flag announces each recording (requires `espeak`)

**During batch recording:**
- Stay near the setup (supervise)
- Watch for any mechanical issues
- Check servo temperature (should be warm but not hot)
- Let servo rest briefly between recordings if needed
- Note any anomalies for later reference

### Command Reference

| Parameter | Description | HTD-45H Value |
|-----------|-------------|---------------|
| `--port` | Serial port | `/dev/ttyUSB0` (Linux), `/dev/tty.usbserial-*` (macOS) |
| `--baudrate` | Communication speed | `115200` (default) |
| `--id` | Servo ID | `1` (default) |
| `--mass` | End weight (kg) | `0.3` (300 g) |
| `--length` | Arm length (m) | `0.12` (12 cm) |
| `--arm_mass` | Arm mass (kg) | `0.02` (20 g, optional) |
| `--motor` | Servo model | `htd45h` |
| `--vin` | Supply voltage | `12.0` |
| `--logdir` | Output directory | `data_raw_htd45h` |
| `--trajectory` | Trajectory type | `lift_and_drop`, `sin_time_square`, etc. |
| `--kp` | Control gain | `8`, `16`, or `32` |
| `--speak` | Voice announcements | flag (optional) |

## Complete Data Processing Workflow

After collecting raw data, process and fit friction models:

```bash
# Using uv (recommended)

# 1. Process raw data (resample to constant timestep)
uv run python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 2. Verify data quality with plots
uv run python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h

# Check plots show smooth trajectories, no obvious errors
# See "How to Check Plot Quality" section below for detailed guidance

# 3. Fit baseline model (M1: Coulomb-Viscous)
mkdir -p params/htd45h

uv run python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m1.json \
    --trials 5000

# 4. Fit advanced model (M6: Full friction model)
uv run python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m6.json \
    --trials 20000

# 5. Validate results (compare simulation vs real data)
uv run python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# 6. Generate friction characteristic diagrams
uv run python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```

<details>
<summary>Using regular python (legacy)</summary>

```bash
# 1. Process raw data (resample to constant timestep)
python -m bam.process \
    --raw data_raw_htd45h \
    --logdir data_processed_htd45h \
    --dt 0.005

# 2. Verify data quality with plots
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h

# 3. Fit baseline model (M1: Coulomb-Viscous)
mkdir -p params/htd45h

python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m1.json \
    --trials 5000

# 4. Fit advanced model (M6: Full friction model)
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed_htd45h \
    --method cmaes \
    --output params/htd45h/m6.json \
    --trials 20000

# 5. Validate results (compare simulation vs real data)
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed_htd45h \
    --sim \
    --params params/htd45h/m6.json

# 6. Generate friction characteristic diagrams
python -m bam.drive_backdrive \
    --params params/htd45h/m6.json \
    --max_torque 50
```
</details>

## Expected Results

### How to Check Plot Quality

After running `python -m bam.plot --actuator htd45h --logdir data_processed_htd45h`, matplotlib will show a plot for each recorded trajectory with 2-3 subplots:

#### Plot Layout
1. **Top subplot (Position)**: Shows joint angle over time
   - Blue line: Actual position (`q`)
   - Black dashed line: Goal position (`goal_q`)

2. **Middle subplot (Speed)**: Shows angular velocity over time (if available)
   - Blue line: Angular velocity (`speed`)

3. **Bottom subplot (Control)**: Shows voltage/control signal
   - Blue line: Control signal (voltage in volts)
   - Red shaded areas: Torque disabled periods

#### What to Look For - Good Quality Data ✅

**Position Plot (Top):**
- ✅ **Smooth curves**: Position should be continuous without sudden jumps
- ✅ **Follows trajectory**: Actual position (blue) should roughly track goal position (black dashed)
- ✅ **Reasonable range**: Pendulum should swing at least ±0.5 rad (±30°), ideally ±1.0 rad or more
- ✅ **Complete motion**: Should show the full trajectory from start to end
- ✅ **Returns to zero**: At the end, position should return close to 0 rad (hanging down)

**Example good position plot:**
```
Position [rad]
  1.5 |           /\
  1.0 |         /    \
  0.5 |       /        \
  0.0 |-----/            \--------
 -0.5 |                    \    /
 -1.0 |                      \/
      |_________________________
      0    5    10   15   20   Time [s]
```

**Speed Plot (Middle):**
- ✅ **Smooth transitions**: Speed changes should be gradual, not jagged
- ✅ **Zero crossings**: Speed should cross zero when pendulum changes direction
- ✅ **Reasonable magnitude**: Typical speeds 1-5 rad/s for pendulum motion
- ✅ **Some noise is OK**: HTD-45H has limited encoder resolution, small noise is normal

**Control Plot (Bottom):**
- ✅ **Reasonable voltage**: Should be within ±12V for HTD-45H
- ✅ **Torque-off periods visible**: Red shaded areas show when torque is disabled
- ✅ **Smooth when enabled**: Control signal should be continuous (not extremely noisy)

#### Warning Signs - Poor Quality Data ⚠️

**Position Issues:**
- ❌ **Sudden jumps**: Large discontinuities (>0.2 rad jump) indicate communication errors
- ❌ **Flat sections**: Long periods with no movement may indicate stuck servo
- ❌ **Extreme values**: Position >3.14 rad or <-3.14 rad suggests calibration issue
- ❌ **Doesn't return to zero**: Final position far from 0 rad indicates problem
- ❌ **Too small range**: Swing <0.3 rad means insufficient excitation

**Example bad position plot (jumps):**
```
Position [rad]
  1.5 |      /\
  1.0 |    /    \___  <- Sudden jump
  0.5 |  /           |
  0.0 |/             |_____
      |_________________________
```

**Speed Issues:**
- ❌ **Extremely jagged**: If speed plot looks like random noise, data quality is poor
- ❌ **Unrealistic values**: Speeds >10 rad/s for pendulum are suspicious
- ❌ **Missing data**: If speed is all zeros, speed estimation failed

**Control Issues:**
- ❌ **Saturated voltage**: Constantly at ±12V means controller is saturating
- ❌ **Extreme noise**: Wild oscillations in control signal
- ❌ **Always zero**: Control never activates (torque issue)

#### Specific Trajectory Checks

**For `lift_and_drop`:**
- Should see smooth lift upward (positive position)
- Flat section at peak (torque disabled - red shading)
- Free fall with oscillations (damped sinusoid)
- Example: Position lifts to +1.5 rad, drops, swings through -1.0 rad, returns to 0

**For `sin_time_square`:**
- Sinusoidal motion with progressively increasing frequency
- Position oscillates symmetrically around 0 rad
- Amplitude decreases as frequency increases

**For `sin_sin`:**
- Smooth oscillations with two superimposed frequencies
- Should look like a complex wave pattern
- Consistent amplitude throughout

**For `up_and_down`:**
- Controlled rise and fall
- No free-fall sections (torque always on except red areas)
- Smooth transitions

#### What to Do Based on Plot Inspection

**If plots look good:**
```bash
# Proceed to model fitting
uv run python -m bam.fit \
    --actuator htd45h \
    --model m1 \
    --logdir data_processed_htd45h \
    --output params/htd45h/m1.json \
    --trials 5000
```

**If you see issues:**

1. **Occasional jumps in 1-2 trajectories:**
   - Acceptable - Delete those specific bad trajectory files
   - Re-run those trajectories if needed
   - Proceed with remaining good data

2. **Consistent issues across all trajectories:**
   - Check hardware: servo mounting, power supply, cables
   - Verify pendulum swings freely (no binding)
   - Check communication: try lowering sampling rate
   - Re-collect all data after fixing issues

3. **Position range too small:**
   - Increase pendulum mass or length
   - Check servo can handle the load
   - Verify trajectory parameters

4. **Noisy speed data:**
   - This is normal for HTD-45H (limited encoder resolution)
   - Processing and fitting will handle this
   - Only worry if position is also very noisy

#### Quick Visual Checklist

For each trajectory plot, verify:
- [ ] Position curve is continuous (no jumps >0.2 rad)
- [ ] Position swings at least ±0.5 rad
- [ ] Position returns to ~0 rad at end
- [ ] Speed plot (if shown) has reasonable shape
- [ ] Control voltage is within ±12V range
- [ ] Red shaded areas (torque off) appear where expected
- [ ] Overall plot looks like pendulum motion (not random)

**Target: At least 8-10 good trajectories out of 12** for successful model fitting.

### Data Quality Indicators

**Good quality data shows:**
- Smooth position trajectories (no jumps or discontinuities)
- Consistent sampling rate (~100-200 Hz)
- Pendulum swings through ±45° minimum (more is better)
- Clean return to zero position (no residual oscillations)
- Stable voltage readings (~12V throughout)
- Temperature within reasonable range (<60°C)

### Model Performance

| Model | Description | Expected MAE | Typical Parameters |
|-------|-------------|--------------|-------------------|
| **M1** | Coulomb-Viscous (baseline) | 0.05-0.08 rad | `friction_base`, `friction_viscous`, `kt`, `R` |
| **M6** | Full friction (Stribeck + load-dependent + directional + quadratic) | 0.02-0.04 rad | M1 + 8-10 additional parameters |

**Success criteria:**
- M6 MAE should be **50% or less** than M1 MAE
- Simulation trajectories closely match real data in plots
- Parameters are physically reasonable (check order of magnitude)

**Typical M6 improvement:**
- M1 MAE: ~0.06 rad → M6 MAE: ~0.03 rad (50% reduction)

## Troubleshooting

### Hardware Issues

#### Servo doesn't move
**Symptoms**: Servo powered but doesn't respond to commands

**Solutions:**
1. Check 12V power supply is connected and ON
2. Measure voltage at servo with multimeter (should be ~12V)
3. Verify all GND connections are solid
4. Check board power LED (should be ON)
5. Verify USB connection to computer
6. Try different servo ID: `--id 2` (servo might be misconfigured)
7. Check servo cable is properly connected to board Port 1

#### Communication errors
**Symptoms**: "Timeout", "No response", or checksum errors

**Solutions:**
1. Verify correct serial port: `ls -l /dev/ttyUSB*`
2. Check permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Verify servo ID is 1: `--id 1`
4. Check USB cable connection to board
5. Try different USB port on computer
6. Restart the board controller

#### Erratic or jerky movement
**Symptoms**: Servo moves but not smoothly

**Solutions:**
1. Check power supply is **regulated** (not just battery)
2. Verify power supply has sufficient current (2-3A minimum)
3. Check all wiring connections are tight
4. Ensure proper grounding (GND connected)
5. Reduce load if servo struggles (lighter weight or shorter arm)
6. Check for mechanical binding in pendulum

#### Pendulum hits limits or binds
**Symptoms**: Pendulum stops at certain angles

**Solutions:**
1. Check cables don't interfere with swing
2. Verify arm is balanced (not twisted)
3. Ensure horn is tight on servo shaft
4. Check weight is securely fastened
5. Verify clearance for ±120° swing

### Data Quality Issues

#### High MAE / poor model fit
**Symptoms**: M6 MAE > 0.06 rad, or M6 not much better than M1

**Solutions:**
1. **Verify measurements**: Re-measure mass and length accurately
2. **Check pendulum**: Ensure free swinging (no friction in joints)
3. **Stable power**: Use regulated supply, voltage should be constant 12V
4. **More data**: Collect additional trajectories
5. **More trials**: Increase `--trials 50000` for M6
6. **Mechanical issues**: Check for loose parts, binding, or wobble

#### Noisy position data
**Symptoms**: Position traces look jagged or noisy in plots

**Solutions:**
1. This is **normal** for HTD-45H servos (limited encoder resolution)
2. Processing step filters data automatically
3. Ensure stable mechanical setup (no vibration)
4. Check for loose connections (electrical or mechanical)
5. Verify power supply is clean (no voltage fluctuations)
6. Ensure board controller is properly powered and grounded

#### Inconsistent results across trajectories
**Symptoms**: Some trajectories fit well, others don't

**Solutions:**
1. Check if bad trajectories have mechanical issues
2. Remove outlier trajectories and re-fit
3. Verify temperature is stable (friction changes with temperature)
4. Check for position-dependent friction (worn gears)

### Board Controller vs Direct Serial

The HTD-45H servo **requires** the Hiwonder Bus Servo Controller Board for proper operation. Direct serial communication is not supported.

**Why the board controller is required:**
- Provides reliable half-duplex communication protocol
- Handles voltage regulation and signal conditioning
- Supports multi-servo setups
- Includes safety features and error handling
- Ensures proper timing for servo communication

## Best Practices

### Hardware Setup
1. **Stable mounting**: Servo must not move during operation
2. **Regulated power**: Use bench supply or regulated DC, not battery
3. **Secure fasteners**: Check all screws and connections are tight
4. **Cable management**: Route cables to avoid interfering with swing
5. **Zero position**: Mark pendulum zero (hanging down) for reference

### Pendulum Design
1. **Rigid arm**: No flex or bending (use metal or carbon fiber)
2. **Concentrated mass**: Weight at tip, not distributed along arm
3. **Balanced**: Arm should hang straight down (not twisted)
4. **Appropriate load**: 200-500 g range is optimal for HTD-45H
5. **Secure weight**: Use locknuts or adhesive to prevent loosening

### Data Collection
1. **Test first**: Always run single test recording before batch
2. **Monitor temperature**: Servo should be warm but not hot (< 60°C)
3. **Cool down**: Let servo rest 1-2 min between long recordings if needed
4. **Supervise**: Watch first few recordings to catch issues early
5. **Document setup**: Photo of setup, note exact measurements

### Measurement Accuracy
1. **Weigh carefully**: Use scale accurate to 1 g
2. **Measure length**: Use caliper or ruler, measure to 1 mm
3. **Find center of mass**: For weight, measure to midpoint
4. **Include arm mass**: Optional but improves accuracy if arm is heavy
5. **Record everything**: Write down actual values used

### Optimization
1. **Start with M1**: Baseline model, quick to fit (~10 min)
2. **Check M1 first**: Should give MAE ~0.06-0.08 rad
3. **Then fit M6**: Advanced model, slower (~1 hour)
4. **Sufficient trials**: 5000 for M1, 20000+ for M6
5. **Validate plots**: Visual check that sim matches real data

## HTD-45H Specifications

| Parameter | Value |
|-----------|-------|
| **Voltage** | 12V (nominal) |
| **Current** | 2-3A peak |
| **Torque** | 45 kg·cm @ 12V |
| **Speed** | ~0.2 sec/60° |
| **Gears** | Metal (industrial grade) |
| **Protocol** | Half-duplex serial, 115200 baud |
| **Position range** | 0-1000 (0-240°) |
| **Communication** | Hiwonder bus protocol |

## Available Trajectories

| Name | Description | Duration | Best for |
|------|-------------|----------|----------|
| `sin_time_square` | Sine wave with t² modulation | 10s | Varied acceleration, complex dynamics |
| `sin_sin` | Double sine wave | 10s | Smooth oscillation, low acceleration |
| `lift_and_drop` | Lift up, then free fall | 10s | Load transitions, backdrive friction |
| `up_and_down` | Controlled up and down | 10s | Step responses, control friction |

All trajectories are designed to excite different friction regimes (low speed, high speed, acceleration, deceleration, forward, backward).

## Control Parameters (KP Values)

Batch recording tests 3 KP values: **8, 16, 32**

- **KP = 8**: Low stiffness, more compliant
  - Reveals low-speed friction
  - More backdrive (external torque dominant)

- **KP = 16**: Medium stiffness
  - Balanced motor/external torque
  - General operating condition

- **KP = 32**: High stiffness, tight control
  - Reveals high-speed dynamics
  - More drive friction (motor torque dominant)

Multiple KP values ensure the model captures friction across diverse operating conditions.

## Data Format

Data saved as JSON files:

```json
{
  "mass": 0.3,
  "length": 0.12,
  "arm_mass": 0.02,
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

Fields:
- `position`: Joint angle (radians), 0 = hanging down
- `speed`: Angular velocity (rad/s), estimated from position changes
- `goal_position`: Desired position from controller (radians)
- `voltage`: Battery/supply voltage (V)
- `temperature`: Servo temperature (°C), if available

## Summary Checklist

### Before Starting
- [ ] HTD-45H servo acquired
- [ ] 12V power supply (2-3A) ready
- [ ] Board controller or USB-TTL adapter ready
- [ ] Pendulum materials collected
- [ ] Tools available (screwdriver, drill, scale, ruler)

### Hardware Assembly
- [ ] Servo mounted vertically and securely
- [ ] Pendulum arm built (10-15 cm)
- [ ] End weight attached (200-500 g)
- [ ] Arm attached to servo horn
- [ ] Pendulum hangs straight down at zero
- [ ] Full ±90° swing clearance verified
- [ ] No binding or wobble in rotation

### Measurements
- [ ] End mass weighed accurately: _____ kg
- [ ] Arm length measured: _____ m
- [ ] Arm mass weighed (optional): _____ kg
- [ ] Values recorded for command arguments

### Wiring
- [ ] Power supply connected to servo (12V, GND)
- [ ] Board controller or USB-TTL connected
- [ ] USB cable to computer
- [ ] Polarity double-checked
- [ ] Voltage verified with multimeter (~12V)

### Software
- [ ] Python dependencies installed (`pyserial`)
- [ ] Serial port permissions configured (Linux)
- [ ] Serial port detected (`/dev/ttyUSB0` or similar)

### Initial Testing
- [ ] Test recording completed successfully
- [ ] Pendulum swings smoothly
- [ ] Returns to zero position
- [ ] No error messages
- [ ] Data file created

### Data Collection
- [ ] Batch recording started
- [ ] Supervising recordings
- [ ] Servo temperature monitored
- [ ] All 12 recordings completed
- [ ] Raw data saved in `data_raw_htd45h/`

### Data Processing
- [ ] Data processed with `bam.process`
- [ ] Plots checked for quality
- [ ] M1 model fitted (baseline)
- [ ] M6 model fitted (advanced)
- [ ] Results validated with plots
- [ ] Parameters saved in `params/htd45h/`

### Documentation
- [ ] Setup photographed
- [ ] Measurements recorded
- [ ] Any issues noted
- [ ] Parameters documented

## Quick Reference Card

### Essential Commands (Copy & Paste)

**Test Recording:**
```bash
# Using uv (recommended)
uv run python -m bam.hiwonder.record_board --port /dev/ttyUSB0 --id 1 \
  --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
  --logdir test_data --trajectory lift_and_drop

# Using regular python
python -m bam.hiwonder.record_board --port /dev/ttyUSB0 --id 1 \
  --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
  --logdir test_data --trajectory lift_and_drop
```

**Batch Collection:**
```bash
# Using uv (recommended)
uv run python -m bam.hiwonder.all_record_board --port /dev/ttyUSB0 --id 1 \
  --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
  --logdir data_raw_htd45h

# Using regular python
python -m bam.hiwonder.all_record_board --port /dev/ttyUSB0 --id 1 \
  --mass 0.3 --length 0.12 --motor htd45h --vin 12.0 \
  --logdir data_raw_htd45h
```

**Processing & Fitting:**
```bash
# Using uv (recommended)
uv run python -m bam.process --raw data_raw_htd45h --logdir data_processed_htd45h --dt 0.005
uv run python -m bam.fit --actuator htd45h --model m6 --logdir data_processed_htd45h \
  --output params/htd45h/m6.json --trials 20000
uv run python -m bam.plot --actuator htd45h --logdir data_processed_htd45h \
  --sim --params params/htd45h/m6.json

# Using regular python
python -m bam.process --raw data_raw_htd45h --logdir data_processed_htd45h --dt 0.005
python -m bam.fit --actuator htd45h --model m6 --logdir data_processed_htd45h \
  --output params/htd45h/m6.json --trials 20000
python -m bam.plot --actuator htd45h --logdir data_processed_htd45h \
  --sim --params params/htd45h/m6.json
```

### Key Specifications

| Parameter | Value |
|-----------|-------|
| **Servo model** | HTD-45H |
| **Voltage** | 12V |
| **Arm length** | 12 cm (0.12 m) |
| **End weight** | 300 g (0.3 kg) |
| **Port** | `/dev/ttyUSB0` (Linux) or `/dev/tty.usbserial-*` (macOS) |
| **Baud rate** | 115200 |
| **Servo ID** | 1 |

### Help Resources

| Resource | Link |
|----------|------|
| **Video tutorial** | https://youtu.be/5XPEEKDnQEM |
| **Research paper** | https://arxiv.org/pdf/2410.08650v1 |
| **Visual setup reference** | See main README.md images |
| **Troubleshooting** | See "Troubleshooting" section above |

## FAQ

### Do I need the 2R arm experiment to calibrate HTD-45H?

**NO!** The pendulum experiment in this guide is **complete and sufficient** for calibration.

- ✅ **Pendulum (1R) = Calibration** - Get friction parameters (what you need!)
- ❌ **2R arm = Optional validation** - Only for testing on multi-joint robots

The 2R arm experiment shown in the BAM paper is **optional validation** for researchers. It's NOT required to get working friction parameters. After completing this guide, your `params/htd45h/m6.json` file is ready to use in simulations.

**Same process as Dynamixel and Feetech servos** - they also only require the pendulum experiment.

### Can I use the parameters immediately?

**YES!** After fitting M6, your parameters in `params/htd45h/m6.json` are ready to use:
- In MuJoCo simulations (using `MujocoController`)
- In other simulators that support friction models
- For any robotics application using HTD-45H servos

No additional validation is required unless you want extra confidence for a specific robot arm.

### Is 1.3 lb (590g) too heavy for HTD-45H?

**NO! It's perfectly safe.** Here's the analysis:

**Weight Conversion:**
- 1.3 lb = 590 g (0.59 kg)

**Torque Requirements with 12 cm arm:**
- HTD-45H max torque: **45 kg·cm**
- Required to hold 590g horizontally: **7.1 kg·cm**
- **Safety margin: 6.4x** ✅

**At typical 45° angle:**
- Required torque: **5.0 kg·cm**
- **Safety margin: 9.0x** ✅

**Verdict:** 590g is **well within safe limits** and will work excellently for friction identification.

**Weight Guidelines for HTD-45H:**

| Weight | Arm Length | Safety Margin | Recommendation |
|--------|------------|---------------|----------------|
| 200g | 12 cm | 15.9x | ✅ Very conservative |
| 300g | 12 cm | 10.6x | ✅ Recommended baseline |
| **590g (1.3 lb)** | **12 cm** | **6.4x** | ✅ **Excellent choice** |
| 600g | 12 cm | 6.3x | ✅ Safe |
| 800g | 12 cm | 4.7x | ✅ Still good |
| 1000g | 12 cm | 3.8x | ⚠️ Getting heavy |

**Bottom line:** Use your 1.3 lb weight with confidence! It provides good dynamic range for friction identification while maintaining excellent safety margin.

## Additional Documentation

- **Implementation details**: See `IMPLEMENTATION.md` for software architecture
- **Board controller protocol**: See `BOARD_CONTROLLER_GUIDE.md` for low-level details
- **API reference**: See `README.md` for all commands and options
- **General BAM workflow**: See main project `CLAUDE.md` and `README.md`
- **Optional 2R validation**: See `2R/README.md` if you want to validate on a robot arm

---

**For questions or issues**:
1. Watch the video tutorial first: https://youtu.be/5XPEEKDnQEM
2. Check the Troubleshooting section in this guide
3. Review the research paper: https://arxiv.org/pdf/2410.08650v1
4. Check GitHub issues or project documentation
