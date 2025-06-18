# Joystick Penguin - Linux Joystick Configuration Tool 🐧🎮

## Rebranding & Roadmap

### **New Name: Joystick Penguin**
- Perfect for Linux (penguin mascot)
- More memorable than "Joystick Gremlin Linux Maybe"
- Keeps the playful spirit of the original

---

## 🎯 **Post-Conversion Priority Features**

After successfully converting Joystick Gremlin to Linux and confirming it works, we need to add these critical Windows-equivalent features:

### **1. 🕶️ Device Hiding (Linux HidHide equivalent)**

**Problem**: Without device hiding, games see both:
- Original physical joystick  
- Virtual joystick created by Joystick Penguin
- This causes duplicate/conflicting inputs

**Windows Solution**: HidHide
- Hides physical devices from specific applications
- Allows selective device visibility per application
- Game only sees the virtual joystick

**Linux Implementation Needed**:
- **udev rules** to control device visibility
- **Device namespace isolation** per application
- **Application-specific device filtering**
- **GUI for managing which apps see which devices**

**Technical Approach**:
```bash
# Possible methods:
- udev rules + custom device management
- cgroups device access control
- LD_PRELOAD library to filter input devices
- Custom input device proxy/filter daemon
```

### **2. 🎮 Enhanced Virtual Joysticks (Linux vJoy equivalent)**

**Problem**: Current virtual joystick limitations
- Need support for many more buttons (Windows vJoy supports ~127 buttons)
- Need multiple virtual devices simultaneously
- Need advanced axis/hat configurations

**Windows Solution**: vJoy
- Creates virtual joystick devices with custom configurations
- Supports up to 127 buttons per device
- Multiple devices (8+ virtual joysticks)
- Advanced axis and hat configurations

**Linux Enhancement Needed**:
- **Expand current `linput/virtual_output.py`**
- **Support 127+ buttons per virtual device**
- **Multiple simultaneous virtual joysticks**
- **Advanced device configurations**
- **Device persistence across reboots**

**Technical Expansion**:
```python
# Enhanced VirtualJoystickManager features:
- create_virtual_joystick(buttons=127, axes=8, hats=4)
- support multiple devices (joystick1, joystick2, etc.)
- device configuration persistence
- hot-plug/unplug virtual devices
```

---

## 📋 **Implementation Priority**

### **Phase 1: Complete Linux Conversion** ✅ In Progress
- ✅ Linux input backend
- 🔄 Linux output backend  
- ⏳ Linux mapping engine
- ⏳ Linux UI

### **Phase 2: Rebrand to Joystick Penguin**
- Update all branding, documentation, icons
- New logo with penguin theme
- Update repository name

### **Phase 3: Advanced Features**
1. **Enhanced Virtual Joysticks** (expand existing `linput/virtual_output.py`)
2. **Device Hiding System** (new subsystem)

---

## 🔧 **Technical Notes for Future Implementation**

### **Device Hiding Research**:
- Study `/dev/input` device management
- Research udev rules for device filtering
- Investigate LD_PRELOAD approaches for per-app filtering
- Look into existing Linux solutions (if any)

### **Enhanced Virtual Joysticks**:
- Current `uinput` supports many buttons - just need to expand our wrapper
- Test maximum button limits on Linux
- Design multiple device management system
- Create device persistence mechanism

---

## 🎯 **Success Criteria**

**Joystick Penguin will be feature-complete when**:
1. ✅ Full Linux joystick configuration (like Windows Joystick Gremlin)
2. 🎮 127+ button virtual joysticks (like vJoy) 
3. 🕶️ Per-application device hiding (like HidHide)
4. 🐧 Polished Linux-native experience

**Target**: Become the definitive Linux joystick configuration tool - better than Windows equivalents!

---

*Remember: These advanced features come AFTER we complete the core Linux conversion and confirm everything works. But documenting now so we don't forget the vision!*
