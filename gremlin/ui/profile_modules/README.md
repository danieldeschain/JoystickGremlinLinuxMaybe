# Profile Modules Package - Refactoring Plan

## Status: 📋 PLANNED

**Target**: gremlin/ui/profile.py  
**Current**: 943 lines, 7 classes  
**Goal**: Modular package structure with 90%+ reduction

## Classes to Extract (7 total)

### 1. VirtualButtonModel (lines ~49-181)
**Purpose**: Axis and hat virtual button configuration  
**Size**: ~130 lines  
**Target Module**: `virtual_buttons.py`

**Features**:
- Lower/upper limit configuration for axis buttons
- Direction selection (above/below)
- Hat direction multi-selection (8 directions)
- QML Property bindings for all settings

### 2. HatDirectionModel (lines ~182-261)
**Purpose**: Hat direction state management  
**Size**: ~80 lines  
**Target Module**: `virtual_buttons.py` (same as VirtualButtonModel)

**Features**:
- Generic hat direction list management
- 8-direction boolean properties
- Direction add/remove logic

### 3. InputItemBindingModel (lines ~262-651)
**Purpose**: Input item binding configuration  
**Size**: ~390 lines (LARGEST CLASS)  
**Target Module**: `input_binding.py`

**Features**:
- Input item description and always-execute flag
- Action sequence management (add, delete, move, duplicate)
- Container management (create, update, delete, move)
- Virtual button configuration
- Activation condition management
- Complex QML integration

### 4. InputItemModel (lines ~652-765)
**Purpose**: Input items list model for QML  
**Size**: ~115 lines  
**Target Module**: `input_model.py`

**Features**:
- QAbstractListModel for device inputs
- Device and mode filtering
- Input identifier generation
- Input description aggregation

### 5. ModeListModel (lines ~766-809)
**Purpose**: Profile modes list  
**Size**: ~45 lines  
**Target Module**: `mode_models.py`

**Features**:
- Simple list of mode names
- QAbstractListModel implementation

### 6. ModeHierarchyModel (lines ~810-861)
**Purpose**: Mode inheritance hierarchy  
**Size**: ~50 lines  
**Target Module**: `mode_models.py` (with ModeListModel)

**Features**:
- Mode parent-child relationships
- Hierarchical mode display

### 7. LabelValueSelectionModel (lines ~862-943)
**Purpose**: Generic label-value selection  
**Size**: ~80 lines  
**Target Module**: `selection_models.py`

**Features**:
- Generic key-value pair list
- QAbstractListModel for dropdowns
- Current selection tracking

## Proposed Module Structure

```
gremlin/ui/profile_modules/
├── __init__.py              # Re-exports all classes
├── README.md                # This file
├── virtual_buttons.py       # VirtualButtonModel, HatDirectionModel (~210 lines)
├── input_binding.py         # InputItemBindingModel (~390 lines)
├── input_model.py           # InputItemModel (~115 lines)
├── mode_models.py           # ModeListModel, ModeHierarchyModel (~95 lines)
└── selection_models.py      # LabelValueSelectionModel (~80 lines)
```

## Extraction Plan

1. ✅ Create package structure
2. ⏳ Extract virtual_buttons.py (VirtualButtonModel, HatDirectionModel)
3. ⏳ Extract input_binding.py (InputItemBindingModel - largest, most complex)
4. ⏳ Extract input_model.py (InputItemModel)
5. ⏳ Extract mode_models.py (ModeListModel, ModeHierarchyModel)
6. ⏳ Extract selection_models.py (LabelValueSelectionModel)
7. ⏳ Update __init__.py with all re-exports
8. ⏳ Replace profile.py with re-exports (~50 lines)

## Impact Metrics (Projected)

- **Original**: 943 lines, 7 classes
- **Target**: ~50 lines (re-exports only)
- **Reduction**: 94.7% (943 → 50 lines)
- **Modules**: 5 focused modules + package init
- **Average module size**: ~178 lines

## Dependencies

- PySide6 (QtCore, QtQml)
- gremlin.profile
- gremlin.types
- gremlin.util
- gremlin.ui.action_model
- gremlin.ui.models

## Notes

- InputItemBindingModel is the largest and most complex class (~390 lines)
- Virtual button models share similar patterns (8 hat directions)
- Mode models are lightweight and can share a module
- All models are QML-exposed (@QtQml.QmlElement)
- Backward compatibility critical - many QML dependencies

---

*Phase 5 Planning - October 29, 2025*
