# Macro Modules Package - Refactoring Plan

## Status: 📋 PLANNED

**Target**: gremlin/macro.py  
**Current**: 920 lines, 13 classes  
**Goal**: Modular package structure with 90%+ reduction

## Classes to Extract (13 total)

### 1. MacroManager (lines ~48-251)
**Purpose**: Singleton macro scheduler and dispatcher  
**Size**: ~200 lines (LARGEST)  
**Target Module**: `manager.py`

**Features**:
- Macro queue management
- Scheduler thread for macro execution
- Exclusive and repeat macro handling
- State flag management with thread locks
- Default delay configuration

### 2. Macro (lines ~252-343)
**Purpose**: Macro sequence container  
**Size**: ~90 lines  
**Target Module**: `macro.py`

**Features**:
- Action sequence storage
- Repeat configuration
- Exclusive execution flag
- XML persistence (from_xml, to_xml)

### Action Classes (7 classes, lines ~344-769)
**Target Module**: `actions.py`

#### 3. AbstractAction (lines ~344-379)
**Purpose**: Base class for all macro actions  
**Size**: ~35 lines

#### 4. JoystickAction (lines ~380-496)
**Purpose**: VJoy axis/button/hat actions  
**Size**: ~115 lines (LARGE)

#### 5. KeyAction (lines ~497-547)
**Purpose**: Keyboard key press/release  
**Size**: ~50 lines

#### 6. MouseButtonAction (lines ~548-601)
**Purpose**: Mouse button press/release  
**Size**: ~55 lines

#### 7. MouseMotionAction (lines ~602-640)
**Purpose**: Mouse cursor movement  
**Size**: ~40 lines

#### 8. PauseAction (lines ~641-674)
**Purpose**: Delay/pause in macro sequence  
**Size**: ~35 lines

#### 9. VJoyAction (lines ~675-769)
**Purpose**: VJoy device state changes  
**Size**: ~95 lines

### Repeat Classes (4 classes, lines ~770-920)
**Target Module**: `repeat.py`

#### 10. AbstractRepeat (lines ~770-812)
**Purpose**: Base class for repeat modes  
**Size**: ~40 lines

#### 11. CountRepeat (lines ~813-846)
**Purpose**: Repeat N times  
**Size**: ~35 lines

#### 12. ToggleRepeat (lines ~847-876)
**Purpose**: Toggle on/off repeat  
**Size**: ~30 lines

#### 13. HoldRepeat (lines ~877-920)
**Purpose**: Repeat while held  
**Size**: ~45 lines

## Proposed Module Structure

```
gremlin/macro_modules/
├── __init__.py          # Re-exports all classes
├── README.md            # This file
├── manager.py           # MacroManager singleton (~200 lines)
├── macro.py             # Macro class (~90 lines)
├── actions.py           # All 7 action classes (~425 lines)
└── repeat.py            # All 4 repeat classes (~150 lines)
```

## Logical Grouping

**Group 1: Core Management**
- MacroManager (scheduler, dispatcher)
- Macro (container)

**Group 2: Actions**
- AbstractAction (base)
- JoystickAction (VJoy control)
- KeyAction (keyboard)
- MouseButtonAction (mouse clicks)
- MouseMotionAction (mouse movement)
- PauseAction (delays)
- VJoyAction (VJoy state)

**Group 3: Repeat Modes**
- AbstractRepeat (base)
- CountRepeat (N times)
- ToggleRepeat (on/off)
- HoldRepeat (while held)

## Extraction Plan

1. ✅ Create package structure
2. ⏳ Extract manager.py (MacroManager singleton)
3. ⏳ Extract macro.py (Macro class)
4. ⏳ Extract actions.py (all 7 action classes)
5. ⏳ Extract repeat.py (all 4 repeat classes)
6. ⏳ Update __init__.py with all re-exports
7. ⏳ Replace macro.py with re-exports (~50 lines)

## Impact Metrics (Projected)

- **Original**: 920 lines, 13 classes
- **Target**: ~50 lines (re-exports only)
- **Reduction**: 94.6% (920 → 50 lines)
- **Modules**: 4 focused modules + package init
- **Average module size**: ~216 lines

## Dependencies

- dill (device input library)
- vjoy.vjoy (VJoyProxy)
- gremlin.keyboard (key_from_code, send_key_down/up)
- gremlin.sendinput (MouseMotion)
- gremlin.types (AxisMode, InputType, MouseButton)
- gremlin.common (SingletonDecorator)
- gremlin.config (Configuration)
- Threading (Event, Lock, Thread)
- XML (ElementTree)

## Notes

- MacroManager is a singleton with complex threading logic
- Actions use ABC (Abstract Base Class) pattern
- Repeat modes also use ABC pattern
- XML persistence required for all classes
- Thread-safe queue and flag management critical

---

*Phase 5 Planning - October 29, 2025*
