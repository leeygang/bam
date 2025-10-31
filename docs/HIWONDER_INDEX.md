# Hiwonder Servo Documentation Index

Complete guide to all Hiwonder documentation for BAM friction identification.

## 🚀 Start Here

### New User?
**Start with:** `HIWONDER_HTD45H_QUICKSTART.md`
- Quick commands to get started
- HTD-45H specific instructions
- Step-by-step workflow

### Choosing Control Method?
**Read:** `HIWONDER_CONTROL_METHODS_COMPARISON.md`
- Board Controller vs Direct Serial
- Detailed comparison tables
- Recommendations by use case

## 📚 Documentation by Topic

### 1. Quick Starts & Guides

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **HIWONDER_HTD45H_QUICKSTART.md** | HTD-45H quick reference | Starting with HTD-45H |
| **HIWONDER_SETUP_GUIDE.md** | Complete step-by-step setup | First time setup |
| **HIWONDER_CONTROL_METHODS_COMPARISON.md** | Method comparison | Choosing control method |

### 2. Control Methods

#### Board Controller (Recommended ⭐)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **bam/hiwonder/BOARD_CONTROLLER_GUIDE.md** | Complete board guide | Using board controller |
| **bam/hiwonder/hiwonder_board_controller.py** | Protocol reference | Understanding protocol |
| **bam/hiwonder/hiwonder_board_adapter.py** | BAM adapter code | Development reference |
| **HIWONDER_BOARD_CONTROLLER_SUMMARY.md** | Implementation summary | Overview of board support |

#### Direct Serial (Alternative)

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **bam/hiwonder/README.md** | Complete direct serial guide | Using direct serial |
| **bam/hiwonder/hiwonder.py** | Protocol implementation | Understanding protocol |
| **bam/hiwonder/record.py** | Recording script | Development reference |

### 3. Implementation Details

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **bam/hiwonder/IMPLEMENTATION.md** | Architecture & design | Understanding implementation |
| **HIWONDER_SUMMARY.md** | Complete implementation summary | Project overview |
| **HIWONDER_IMPLEMENTATION_COMPLETE.md** | Final completion report | Implementation status |

### 4. Integration & Usage

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **CLAUDE.md** | BAM integration commands | Quick command reference |
| **README.md** | Main BAM documentation | Understanding BAM framework |

## 📁 File Structure

```
Project Root:
├── HIWONDER_INDEX.md                          ← YOU ARE HERE
├── HIWONDER_HTD45H_QUICKSTART.md              Quick start
├── HIWONDER_SETUP_GUIDE.md                    Complete setup guide
├── HIWONDER_CONTROL_METHODS_COMPARISON.md     Method comparison
├── HIWONDER_BOARD_CONTROLLER_SUMMARY.md       Board controller summary
├── HIWONDER_SUMMARY.md                        Implementation summary
├── HIWONDER_IMPLEMENTATION_COMPLETE.md        Completion report
├── CLAUDE.md                                  BAM integration
└── bam/hiwonder/
    ├── README.md                              Direct serial guide
    ├── BOARD_CONTROLLER_GUIDE.md              Board controller guide
    ├── IMPLEMENTATION.md                      Implementation details
    ├── actuator.py                            Actuator models
    ├── hiwonder.py                            Direct serial protocol
    ├── hiwonder_board_controller.py           Board protocol
    ├── hiwonder_board_adapter.py              Board BAM adapter
    ├── record.py                              Direct serial recording
    ├── record_board.py                        Board recording
    ├── all_record.py                          Direct serial batch
    ├── all_record_board.py                    Board batch
    └── test_installation.py                   Installation test
```

## 🎯 Documentation by Use Case

### I Want To...

#### Get Started Quickly
1. Read: `HIWONDER_HTD45H_QUICKSTART.md`
2. Run: Test installation
3. Run: Record test trajectory
4. Done!

#### Understand Control Methods
1. Read: `HIWONDER_CONTROL_METHODS_COMPARISON.md`
2. Choose: Board Controller or Direct Serial
3. Read: Respective guide (see below)

#### Setup Board Controller
1. Read: `bam/hiwonder/BOARD_CONTROLLER_GUIDE.md`
2. Connect: Hardware as documented
3. Test: Run test script
4. Record: Use `record_board.py`

#### Setup Direct Serial
1. Read: `bam/hiwonder/README.md`
2. Wire: USB-TTL adapter
3. Test: Run test script
4. Record: Use `record.py`

#### Understand Implementation
1. Read: `HIWONDER_SUMMARY.md`
2. Read: `bam/hiwonder/IMPLEMENTATION.md`
3. Review: Source code with documentation

#### Integrate with BAM
1. Read: `CLAUDE.md` (Hiwonder section)
2. Read: Main `README.md`
3. Follow: Standard BAM workflow

#### Troubleshoot Issues
1. Check: Respective guide (board or direct serial)
2. Read: Troubleshooting section
3. Review: `HIWONDER_SETUP_GUIDE.md`

#### Compare with Other Servos
1. Read: Main `README.md`
2. Compare: Dynamixel, Feetech sections
3. Review: `bam/actuators.py`

## 🔧 Command Quick Reference

### Board Controller

```bash
# Test
python -m bam.hiwonder.hiwonder_board_controller

# Single recording
python -m bam.hiwonder.record_board \
    --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 \
    --motor htd45h --vin 12.0 \
    --logdir data_raw

# Batch recording
python -m bam.hiwonder.all_record_board \
    --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 \
    --motor htd45h --vin 12.0 \
    --logdir data_raw
```

### Direct Serial

```bash
# Test installation
python -m bam.hiwonder.test_installation

# Single recording
python -m bam.hiwonder.record \
    --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 \
    --motor htd45h --vin 12.0 \
    --logdir data_raw

# Batch recording
python -m bam.hiwonder.all_record \
    --port /dev/ttyUSB0 --id 1 \
    --mass 0.3 --length 0.12 \
    --motor htd45h --vin 12.0 \
    --logdir data_raw
```

### Processing & Fitting (Both Methods)

```bash
# Process data
python -m bam.process \
    --raw data_raw \
    --logdir data_processed \
    --dt 0.005

# Fit model
python -m bam.fit \
    --actuator htd45h \
    --model m6 \
    --logdir data_processed \
    --output params/htd45h/m6.json \
    --trials 20000

# Validate
python -m bam.plot \
    --actuator htd45h \
    --logdir data_processed \
    --sim \
    --params params/htd45h/m6.json
```

## 📊 Documentation Statistics

| Category | Files | Lines |
|----------|-------|-------|
| Python code | 9 | ~1250 |
| Documentation | 9 | ~3900 |
| **Total** | **18** | **~5150** |

### By Topic

| Topic | Documents | Lines |
|-------|-----------|-------|
| Quick starts | 3 | ~1200 |
| Control methods | 4 | ~1400 |
| Implementation | 3 | ~1100 |
| Integration | 2 | ~200 |

## 🎓 Learning Path

### Beginner Path
1. `HIWONDER_HTD45H_QUICKSTART.md` - Get started
2. `HIWONDER_SETUP_GUIDE.md` - Complete setup
3. `bam/hiwonder/README.md` - Direct serial details
4. Run: Test recording

### Intermediate Path
1. `HIWONDER_CONTROL_METHODS_COMPARISON.md` - Choose method
2. `bam/hiwonder/BOARD_CONTROLLER_GUIDE.md` - Board details
3. `bam/hiwonder/IMPLEMENTATION.md` - Understand design
4. Run: Batch recording

### Advanced Path
1. `HIWONDER_SUMMARY.md` - Complete overview
2. Review: Source code
3. `bam/hiwonder/IMPLEMENTATION.md` - Architecture
4. Extend: Add features

## 🔍 Finding Information

### By Question

**"How do I get started?"**
→ `HIWONDER_HTD45H_QUICKSTART.md`

**"Which control method should I use?"**
→ `HIWONDER_CONTROL_METHODS_COMPARISON.md`

**"How does the board controller work?"**
→ `bam/hiwonder/BOARD_CONTROLLER_GUIDE.md`

**"How does direct serial work?"**
→ `bam/hiwonder/README.md`

**"What's the complete setup process?"**
→ `HIWONDER_SETUP_GUIDE.md`

**"How is everything implemented?"**
→ `bam/hiwonder/IMPLEMENTATION.md`

**"What's the overall status?"**
→ `HIWONDER_IMPLEMENTATION_COMPLETE.md`

**"How do I integrate with BAM?"**
→ `CLAUDE.md`

**"I'm having problems..."**
→ Check troubleshooting in respective guides

## ✅ Documentation Checklist

Use this to track your reading:

### Getting Started
- [ ] Read quick start guide
- [ ] Choose control method
- [ ] Setup hardware
- [ ] Test installation
- [ ] Record first trajectory

### Understanding
- [ ] Understand control methods
- [ ] Review protocol details
- [ ] Study architecture
- [ ] Compare with alternatives

### Using
- [ ] Batch recording
- [ ] Data processing
- [ ] Model fitting
- [ ] Result validation

### Advanced
- [ ] Review implementation
- [ ] Understand code structure
- [ ] Explore extensions
- [ ] Share results

## 📞 Getting Help

### Hiwonder Specific
1. Check troubleshooting in relevant guide
2. Review `HIWONDER_SETUP_GUIDE.md`
3. Test with provided scripts
4. Check hardware connections

### BAM General
1. Review main `README.md`
2. Check `CLAUDE.md` for commands
3. See examples in other servo implementations
4. Refer to BAM paper

## 🎯 Key Takeaways

### Two Control Methods
1. **Board Controller** - Professional, recommended
2. **Direct Serial** - Budget-friendly, prototyping

### Both Are:
- ✅ Fully implemented
- ✅ Well documented
- ✅ BAM compatible
- ✅ Production ready

### Choose Based On:
- Hardware availability
- Budget
- Use case
- Requirements

### All Data Compatible:
- Same processing
- Same fitting
- Same workflows
- Interchangeable

## 🚀 Next Steps

1. **Choose your path** (see Learning Path above)
2. **Read relevant docs**
3. **Setup hardware**
4. **Test & record**
5. **Process & fit**
6. **Validate & use**

## 📝 Summary

This index helps you navigate the comprehensive Hiwonder documentation:
- **18 files** with ~5150 lines
- **Both control methods** fully documented
- **Complete workflow** from setup to results
- **All BAM compatible**

**Start with:**
- New users: `HIWONDER_HTD45H_QUICKSTART.md`
- Choosing method: `HIWONDER_CONTROL_METHODS_COMPARISON.md`
- Board controller: `bam/hiwonder/BOARD_CONTROLLER_GUIDE.md`
- Direct serial: `bam/hiwonder/README.md`

**Happy BAM testing! 🎉**
