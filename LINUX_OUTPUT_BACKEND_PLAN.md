# Linux Output Backend Development Plan

## Current Status: `linux-output-backend` Branch

Date: June 18, 2025

## 🎯 **Objectives**

Replace Windows-specific output functionality with Linux-native implementations:

### 1. **Core Output Components to Replace**
- `gremlin/sendinput.py` - Currently Windows SendInput API
- Virtual joystick output capabilities  
- Keyboard/mouse output integration
- Multi-device output management

### 2. **Integration Points**
Files that depend on output functionality:
- `gremlin/macro.py` - Uses `gremlin.sendinput`
- `action_plugins/map_to_mouse/` - Mouse output actions
- `gremlin/code_runner.py` - MouseController integration  

## 📋 **Implementation Plan**

### Phase 1: Linux SendInput Replacement ✅ (PRIORITY)
- [ ] Create Linux-native `gremlin/sendinput.py`
- [ ] Implement keyboard output functions (key_press, key_release)
- [ ] Implement mouse output functions (click, move, scroll)
- [ ] Maintain API compatibility with existing code

### Phase 2: Virtual Device Enhancement 
- [ ] Port enhanced virtual output from `linux-input-backend`
- [ ] Multi-device virtual joystick management
- [ ] Robust device creation/destruction
- [ ] Permission handling improvements

### Phase 3: Output Device Management
- [ ] Device enumeration and status
- [ ] Output validation and error handling
- [ ] Resource cleanup and lifecycle management

### Phase 4: Integration & Testing
- [ ] Integration with existing action plugins
- [ ] Cross-platform compatibility layer
- [ ] Comprehensive testing suite

## 🛠 **Technical Approach**

### Linux SendInput Implementation:
- **Keyboard**: Use `pynput.keyboard.Controller`
- **Mouse**: Use `pynput.mouse.Controller`  
- **Virtual Joystick**: Use `python-uinput` 

### API Compatibility:
- Maintain existing function signatures
- Preserve Windows-style constants/enums
- Add Linux-specific extensions where beneficial

## 📁 **Files to Create/Modify**

### New Files:
- `linput/` - (Port from linux-input-backend branch)
- Test files for output validation

### Modified Files: 
- `gremlin/sendinput.py` - Complete Linux rewrite
- `requirements.txt` - Add Linux dependencies if missing

### Integration Files:
- Various action plugins and core modules (minimal changes)

## 🎯 **Success Criteria**

1. ✅ All existing `gremlin.sendinput` calls work on Linux
2. ✅ Virtual joystick creation and control functional 
3. ✅ Keyboard/mouse output working in action plugins
4. ✅ No Windows dependencies remaining in output path
5. ✅ Comprehensive test coverage

## 📝 **Notes**

- This branch focuses specifically on OUTPUT capabilities
- Input functionality will be merged from `linux-input-backend` later
- Maintain backward compatibility with existing profiles/configs
- Consider permissions (uinput, input group) in implementation

## 🔄 **Dependencies**

- pynput - Keyboard/mouse control
- python-uinput - Virtual device creation  
- evdev - Device monitoring (for validation)
- pyudev - Device management

## ⏭️ **Next Steps**

1. Start with `gremlin/sendinput.py` Linux replacement
2. Create basic test script to validate output functions
3. Port virtual device capabilities 
4. Test integration with existing code
