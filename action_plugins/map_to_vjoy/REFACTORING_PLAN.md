# Map to VJoy Action Plugin - Refactoring Plan

## Status: 📋 PLANNED

**Target**: action_plugins/map_to_vjoy/__init__.py  
**Current**: 885 lines, 3 classes  
**Goal**: Split into focused modules for better maintainability

## Classes to Extract (3 total)

### 1. MapToVjoyFunctor (lines ~43-136)
**Purpose**: Runtime execution of VJoy mapping  
**Size**: ~95 lines  
**Target Module**: `functor.py`

**Features**:
- Axis, button, hat mapping to VJoy devices
- Curve application for axis inputs
- Relative axis mode handling
- State management for different input types
- Parent action parameter inheritance

### 2. MapToVjoyModel (lines ~137-261)
**Purpose**: QML model for VJoy mapping configuration  
**Size**: ~125 lines  
**Target Module**: `model.py`

**Features**:
- VJoy device and input selection
- Axis mode configuration (Absolute/Relative)
- Axis scaling settings
- Response curve management
- Action parameter management
- QML property bindings

### 3. MapToVjoyData (lines ~262-885)
**Purpose**: Data storage and persistence  
**Size**: ~625 lines (LARGEST - 70% of file!)  
**Target Module**: `data.py`

**Features**:
- VJoy target configuration (device, input type, input ID)
- Axis mode and scaling
- Response curve configuration
- XML serialization/deserialization
- Data validation
- Extensive property management

## Proposed Module Structure

```
action_plugins/map_to_vjoy/
├── __init__.py          # Re-exports + plugin registration (~50 lines)
├── README.md            # This file
├── functor.py           # MapToVjoyFunctor (~95 lines)
├── model.py             # MapToVjoyModel (~125 lines)
└── data.py              # MapToVjoyData (~625 lines)
```

## Extraction Plan

1. ✅ Create documentation
2. ⏳ Extract functor.py (MapToVjoyFunctor)
3. ⏳ Extract model.py (MapToVjoyModel)
4. ⏳ Extract data.py (MapToVjoyData - largest class)
5. ⏳ Update __init__.py with re-exports and plugin registration
6. ⏳ Ensure plugin manager integration works

## Impact Metrics (Projected)

- **Original**: 885 lines, 3 classes
- **Target**: ~50 lines (re-exports + registration)
- **Reduction**: 94.4% (885 → 50 lines)
- **Modules**: 3 focused modules + init
- **Average module size**: ~282 lines

## Dependencies

- gremlin.base_classes (AbstractActionData, AbstractFunctor)
- gremlin.ui.action_model (ActionModel)
- gremlin.spline (CubicSpline)
- gremlin.types (InputType, AxisMode, AxisButtonDirection)
- vjoy.vjoy (VJoyProxy)
- XML (ElementTree)
- PySide6 (QtCore, QtQml)

## Notes

- MapToVjoyData is extremely large (70% of file)
- Plugin registration must be preserved in __init__.py
- Functor-Model-Data pattern is clean separation
- XML persistence is critical for profile saving
- VJoy integration requires careful testing

## Key Challenge

The Data class is massive (~625 lines) and could potentially be split further:
- Core data management (~200 lines)
- XML serialization (~200 lines)
- Property getters/setters (~225 lines)

Consider further splitting data.py into:
- `data_core.py` - Main data class
- `data_xml.py` - XML serialization
- `data_properties.py` - Property management

This would achieve even better modularity.

---

*Phase 5 Planning - October 29, 2025*
