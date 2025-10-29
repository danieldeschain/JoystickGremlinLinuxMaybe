# Code Runner Modules - Refactoring Plan

## Status: 📋 PLANNED

**Target**: gremlin/code_runner.py  
**Current**: 714 lines, 6 classes  
**Goal**: Modular package structure with 90%+ reduction

## Classes to Extract (6 total)

### Virtual Button Classes (lines ~39-153)
**Target Module**: `virtual_buttons.py`

#### 1. VirtualButton (lines ~39-83)
**Purpose**: Abstract base class for virtual buttons  
**Size**: ~45 lines

**Features**:
- Abstract base class (ABCMeta)
- Button press/release tracking
- Callback execution
- State management

#### 2. VirtualAxisButton (lines ~84-138)
**Purpose**: Axis-based virtual button  
**Size**: ~55 lines

**Features**:
- Axis direction monitoring (above/below threshold)
- Threshold range configuration
- Value change detection

#### 3. VirtualHatButton (lines ~139-153)
**Purpose**: Hat-based virtual button  
**Size**: ~15 lines

**Features**:
- Hat direction matching
- Multiple direction support

### 4. VirtualButtonFunctor (lines ~154-172)
**Purpose**: Functor for virtual button execution  
**Size**: ~20 lines  
**Target Module**: `virtual_buttons.py` (with button classes)

**Features**:
- Virtual button callback wrapper
- Event processing

### 5. CallbackObject (lines ~173-353)
**Purpose**: Callback registration and execution  
**Size**: ~180 lines  
**Target Module**: `callbacks.py`

**Features**:
- Device callback registration
- Input type callback management (axis, button, hat, keyboard)
- Virtual button callback support
- Callback list management
- Event processing and execution

### 6. CodeRunner (lines ~354-714)
**Purpose**: Main execution engine  
**Size**: ~360 lines (LARGEST - 50% of file)  
**Target Module**: `runner.py`

**Features**:
- Profile execution lifecycle
- Callback management
- Virtual button creation and management
- VJoy device management
- Keyboard callback handling
- Event processing
- Mode management integration
- Profile start/stop logic

## Proposed Module Structure

```
gremlin/code_runner_modules/
├── __init__.py              # Re-exports all classes
├── README.md                # This file
├── virtual_buttons.py       # VirtualButton hierarchy + Functor (~135 lines)
├── callbacks.py             # CallbackObject (~180 lines)
└── runner.py                # CodeRunner (~360 lines)
```

## Logical Grouping

**Group 1: Virtual Buttons**
- VirtualButton (abstract base)
- VirtualAxisButton (axis-based)
- VirtualHatButton (hat-based)
- VirtualButtonFunctor (execution wrapper)

**Group 2: Callback Management**
- CallbackObject (callback registration and execution)

**Group 3: Main Runner**
- CodeRunner (profile execution engine)

## Extraction Plan

1. ✅ Create package structure
2. ⏳ Extract virtual_buttons.py (4 classes: VirtualButton hierarchy + Functor)
3. ⏳ Extract callbacks.py (CallbackObject)
4. ⏳ Extract runner.py (CodeRunner main engine)
5. ⏳ Update __init__.py with all re-exports
6. ⏳ Replace code_runner.py with re-exports (~50 lines)

## Impact Metrics (Projected)

- **Original**: 714 lines, 6 classes
- **Target**: ~50 lines (re-exports only)
- **Reduction**: 93.0% (714 → 50 lines)
- **Modules**: 3 focused modules + package init
- **Average module size**: ~225 lines

## Dependencies

- dill (device input library)
- vjoy.vjoy (VJoyProxy)
- gremlin.base_classes (Value, AbstractActionData)
- gremlin.event_handler (Event, EventListener)
- gremlin.macro (Macro)
- gremlin.mode_manager (ModeManager)
- gremlin.signal (signal)
- gremlin.types (InputType, AxisButtonDirection, HatDirection)
- collections (defaultdict)
- logging
- uuid
- ABCMeta (abstract base classes)

## Notes

- CodeRunner is a massive central class (~360 lines, 50% of file)
- Virtual button hierarchy uses ABC pattern
- Callback system is complex with multiple input types
- VJoy device management integrated
- Mode manager integration critical
- Event processing is performance-sensitive

## Potential Further Splitting

CodeRunner is very large and could be split into:
- `runner_core.py` - Main lifecycle and profile management
- `runner_devices.py` - VJoy device management
- `runner_events.py` - Event processing

However, this might over-complicate the structure. Initial 3-module approach is cleaner.

---

*Phase 5 Planning - October 29, 2025*
