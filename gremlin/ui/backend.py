# -*- coding: utf-8; -*-

# Copyright (C) 2019 Lionel Ott
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import sys
from typing import List
import uuid

from PySide6 import QtCore, QtQml, QtGui
from PySide6.QtCore import Property, Signal, Slot

import linput
from linput.types import UUID_Intermediate_Output

from gremlin import code_runner, common, config, device_initialization, error, \
    event_handler, mode_manager, profile, shared_state, types
from gremlin.intermediate_output import IntermediateOutput
from gremlin.signal import signal
from gremlin.virtual_joystick_manager import VirtualJoystickManager, VirtualJoystickPermissionError

from gremlin.ui.device import InputIdentifier, IODeviceManagementModel
from gremlin.ui.profile import InputItemModel, ModeHierarchyModel
from gremlin.ui.script import ScriptListModel
from gremlin.audio_player import AudioPlayer


QML_IMPORT_NAME = "Gremlin.UI"
QML_IMPORT_MAJOR_VERSION = 1


@QtQml.QmlElement
class UIState(QtCore.QObject):

    """Holds the state of the UI to simplify complex interactions.

    The various UI elements retrieve the state they should be in from this
    instance while being able to set state only via method calls.
    """

    deviceChanged = Signal()
    inputChanged = Signal()
    modeChanged = Signal()
    tabChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._current_device = linput.UUID_Invalid
        self._current_input = {}
        self._current_mode = "Default"
        self._current_tab = "physical"
        self._is_shutting_down = False

        event_handler.EventListener().device_change_event.connect(
            self._device_change
        )
        signal.profileChanged.connect(self._device_change)

    def _device_change(self):
        # We only care about this in case we've selected a physical device
        if self._current_tab != "physical":
            return

        devices = device_initialization.joystick_devices()
        # Filter out intermediate output device to prevent it from appearing as a tab
        devices = [dev for dev in devices if dev.device_guid != UUID_Intermediate_Output]
        selection_valid = False
        for dev in devices:
            if dev.device_guid == self._current_device:
                selection_valid = True
                break

        if not selection_valid:
            if len(devices) > 0:
                self.setCurrentDevice(str(devices[0].device_guid))
            else:
                self.setCurrentDevice(str(linput.UUID_Invalid))
                self.setCurrentTab("intermediate")


    @Slot(str)
    def setCurrentDevice(self, device_name: str) -> None:
        device_uuid = uuid.UUID(device_name)
        if device_uuid != self._current_device:
            self._current_device = device_uuid
            self.deviceChanged.emit()
            self.inputChanged.emit()

    @Slot(InputIdentifier, int)
    def setCurrentInput(self, input: InputIdentifier, index: int) -> None:
        # Add null check to prevent crashes when input is None
        if input is None:
            print("ERROR: setCurrentInput called with None input")
            return
        
        try:
            value = (input, index)
            if value != self._current_input.get(input.device_guid, None):
                self._current_input[input.device_guid] = value
                self.inputChanged.emit()
        except AttributeError as e:
            error_msg = f"AttributeError in setCurrentInput: {e}, input: {input}"
            print(f"ERROR: {error_msg}")
            logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in setCurrentInput: {e}"
            print(f"ERROR: {error_msg}")
            logging.error(error_msg)

    @Slot(str)
    def setCurrentMode(self, mode_name: str) -> None:
        if mode_name != self._current_mode:
            self._current_mode = mode_name
            self.modeChanged.emit()
            self.deviceChanged.emit()
            self.inputChanged.emit()

    @Slot(str)
    def setCurrentTab(self, tab: str) -> None:
        if tab != self._current_tab:
            self._current_tab = tab
            self.tabChanged.emit()

    @Property(str, notify=deviceChanged)
    def currentDevice(self) -> str:
        try:
            if self._is_shutting_down:
                return ""
            return str(self._current_device).upper()
        except:
            return ""

    @Property(InputIdentifier, notify=inputChanged)
    def currentInput(self):
        try:
            if self._is_shutting_down:
                return InputIdentifier()
            return self._current_input.get(
                self._current_device,
                (InputIdentifier(), 0)
            )[0]
        except:
            return InputIdentifier()

    @Property(int, notify=inputChanged)
    def currentInputIndex(self) -> int:
        try:
            if self._is_shutting_down:
                return 0
            return self._current_input.get(
                self._current_device,
                (InputIdentifier(), 0)
            )[1]
        except:
            return 0

    @Property(str, notify=modeChanged)
    def currentMode(self) -> str:
        try:
            if self._is_shutting_down:
                return ""
            return self._current_mode
        except:
            return ""

    @Property(str, notify=tabChanged)
    def currentTab(self) -> str:
        try:
            if self._is_shutting_down:
                return ""
            return self._current_tab
        except:
            return ""

    def __str__(self) -> str:
        cur_input = self._current_input.get(
            self._current_device,
            (InputIdentifier(), 0)
        )
        return f"{self._current_device} {cur_input[0].input_id} " + \
            f"{cur_input[1]}  {self._current_tab}"

    def shutdown(self):
        """Mark the UIState as shutting down to prevent QML errors during cleanup."""
        self._is_shutting_down = True


class Backend(QtCore.QObject):

    """Allows interfacing between the QML frontend and the Python backend."""

    windowTitleChanged = Signal()
    profileChanged = Signal()
    recentProfilesChanged = Signal()
    lastErrorChanged = Signal()
    inputConfigurationChanged = Signal()
    activityChanged = Signal()
    propertyChanged = Signal()
    uiChanged = Signal()

    def __init__(self, engine: QtQml.QQmlApplicationEngine, parent=None):
        super().__init__(parent)

        self.engine = engine
        self.profile = profile.Profile()
        self._last_error = ""
        self._action_state = {}
        self._mode_hierarchy = ModeHierarchyModel(self.profile.modes, self)
        self.runner = code_runner.CodeRunner()
        self.ui_state = UIState(self)
        self._is_shutting_down = False

        # Initialize virtual joystick manager
        self._virtual_joystick_manager = VirtualJoystickManager()
        
        # Check virtual joystick permissions and log status
        permission_status = self._virtual_joystick_manager.get_permission_status()
        if not permission_status['can_create_devices']:
            logging.warning("Virtual joystick creation not available due to permission issues")
            recommendations = self._virtual_joystick_manager.get_permission_recommendations()
            for rec in recommendations:
                logging.info(f"Recommendation: {rec}")

        # Hookup various mode change related callbacks
        mm = mode_manager.ModeManager()
        mm.mode_changed.connect(self._emit_change)
        self.profileChanged.connect(mm.reset)
        self.profileChanged.connect(
            lambda: self.ui_state.setCurrentMode(mm.current.name)
        )

        event_handler.EventHandler().is_active.connect(
            lambda: self.activityChanged.emit()
        )

    def _emit_change(self) -> None:
        """Emits the signal required for property changes to propagate."""
        self.propertyChanged.emit()

    @Property(UIState, notify=uiChanged)
    def uiState(self) -> UIState:
        return self.ui_state

    @Property(bool, notify=activityChanged)
    def gremlinPaused(self) -> bool:
        """Returns True if Gremlin is paused, False otherwise.

        Returns:
            True if Gremlin is paused, False otherwise.
        """
        if self._is_shutting_down:
            return False
        return not event_handler.EventHandler().process_callbacks

    @Property(bool, notify=activityChanged)
    def gremlinActive(self) -> bool:
        """Returns whether or not a Gremlin profile is active.

        Returns:
            True if a profile is active, False otherwise
        """
        if self._is_shutting_down:
            return False
        return self.runner.is_running()

    @Slot()
    def toggleActiveState(self):
        """Toggles Gremlin between active and inactive."""
        self.activate_gremlin(not self.runner.is_running())

    def activate_gremlin(self, activate: bool):
        """Sets the activity state of Gremlin.

        Args:
            activate: If True activates the profile, if False deactivates
                the profile if one is active
        """
        if activate:
            # Generate the code for the profile and run it
            # self._profile_auto_activated = False
            self.runner.start(
                self.profile,
                self.profile.modes.first_mode
            )
            #self.ui.tray_icon.setIcon(QtGui.QIcon("gfx/icon_active.ico"))
        else:
            # Stop running the code
            self.runner.stop()
            # self._update_statusbar_active(False)
            # self._profile_auto_activated = False
            # current_tab = self.ui.devices.currentWidget()
            # if type(current_tab) in [
            #     gremlin.ui.device_tab.JoystickDeviceTabWidget,
            #     gremlin.ui.device_tab.KeyboardDeviceTabWidget
            # ]:
            #     self.ui.devices.currentWidget().refresh()
            # self.ui.tray_icon.setIcon(QtGui.QIcon("gfx/icon.ico"))
        self.activityChanged.emit()

    def minimize(self) -> None:
        """Minimizes the application to the taskbar."""
        root_window = self.engine.rootObjects()[0]
        root_window.setVisibility(QtGui.QWindow.Visibility.Minimized)

    @Slot(InputIdentifier, result=int)
    def getActionCount(self, identifier: InputIdentifier) -> int:
        """Returns the number of actions associated with an input.

        Args:
            identifier: Identifier of a specific InputItem

        Returns:
            Number of actions associated with the InputItem specified by
            the provided identifier
        """
        if identifier is None:
            return 0

        try:
            item = self.profile.get_input_item(
                identifier.device_guid,
                identifier.input_type,
                identifier.input_id,
                self.ui_state.currentMode,
                False
            )
            return len(item.action_sequences)
        except error.ProfileError as e:
            return 0

    @Slot(InputIdentifier, int, result=InputItemModel)
    def getInputItem(
        self,
        identifier: InputIdentifier,
        enumeration_index: int
    ) -> InputItemModel | None:
        """Returns a model for a specified InputItem.

        Args:
            identifier: Identifier of a specific InputItem
            enumeration_index: Index of the model in the device input listing

        Returns:
            Model instance representing the specified InputItem
        """
        if identifier is None or not identifier.isValid:
            return None
        try:
            item = self.profile.get_input_item(
                identifier.device_guid,
                identifier.input_type,
                identifier.input_id,
                self.ui_state.currentMode,
                True
            )
            return InputItemModel(item, enumeration_index, self)
        except error.ProfileError as e:
            print(e)
            return None

    @Slot(result=IODeviceManagementModel)
    def getIODeviceManagementModel(self):
        try:
            if self._is_shutting_down:
                return None
            return IODeviceManagementModel(self)
        except:
            return None

    @Slot(str, int, result=bool)
    def isActionExpanded(self, uuid_str: str, index: int) -> bool:
        """Returns whether or not a specific action is expanded in the UI.

        Args:
            uuid: uuid of the action
            index: index of the particular action

        Returns:
            True if the action is expanded, False otherwise
        """
        return self._action_state.get((uuid.UUID(uuid_str), index), True)

    @Slot(str, int, bool)
    def setIsActionExpanded(
        self,
        uuid_str: str,
        index: int,
        is_expanded: bool
    ) -> None:
        """Sets a specific action's expanded state.

        Args:
            uuid: uuid of the action
            index: index of the particular action
            is_expanded: True if the action is expanded, False otherwise
        """
        self._action_state[(uuid.UUID(uuid_str), index)] = bool(is_expanded)

    @Property(type=list, notify=recentProfilesChanged)
    def recentProfiles(self) -> List[str]:
        """Returns a list of recently used profiles.

        Returns:
            List of recently used profiles
        """
        if self._is_shutting_down:
            return []
        return config.Configuration().value("global", "internal", "recent_profiles")

    @Slot()
    def newProfile(self) -> None:
        """Creates a new profile."""
        self.activate_gremlin(False)
        self.profile = profile.Profile()
        self._mode_hierarchy = ModeHierarchyModel(self.profile.modes, self)
        shared_state.current_profile = self.profile
        self.windowTitleChanged.emit()
        self.profileChanged.emit()
        signal.reloadUi.emit()

    @Slot(str)
    def saveProfile(self, fpath: str) -> None:
        """Saves the current profile in the given path.

        Args:
            path: Path to the file in which to store the current profile
        """
        self.profile.fpath = fpath
        self.profile.to_xml(self.profile.fpath)
        self.windowTitleChanged.emit()

    @Slot(result=str)
    def profilePath(self) -> str:
        """Returns the current profile's path.

        Returns:
            File path of the current profile
        """
        return self.profile.fpath

    @Slot(str)
    def loadProfile(self, fpath):
        """Loads a profile from the specified path.

        Args:
            fpath: Path to the file containing the profile to load
        """
        self._load_profile(fpath)
        config.Configuration().set("global", "internal", "last_profile", fpath)
        self._mode_hierarchy = ModeHierarchyModel(self.profile.modes, self)
        self.profileChanged.emit()
        signal.reloadUi.emit()
        signal.profileChanged.emit()

    @Property(type=ScriptListModel, notify=profileChanged)
    def scriptListModel(self):
        try:
            if self.profile is None:
                return None
            return ScriptListModel(self.profile.scripts, self)
        except:
            return None

    @Property(type=ModeHierarchyModel, notify=profileChanged)
    def modeHierarchy(self):
        try:
            return self._mode_hierarchy if self._mode_hierarchy else None
        except:
            return None

    @Property(type=str, notify=propertyChanged)
    def currentMode(self) -> str:
        try:
            return mode_manager.ModeManager().current.name
        except:
            return ""

    @Property(type=str, notify=windowTitleChanged)
    def windowTitle(self) -> str:
        """Returns the current window title.

        Returns:
            String to use as window title
        """
        try:
            if hasattr(self, 'profile') and self.profile and hasattr(self.profile, 'fpath') and self.profile.fpath:
                return self.profile.fpath
            else:
                return "Joystick Gremlin"
        except (AttributeError, TypeError):
            return "Joystick Gremlin"

    @Property(str, notify=lastErrorChanged)
    def lastError(self) -> str:
        """Returns the last error that occurred.

        Returns:
            Last error to occurr
        """
        try:
            return getattr(self, '_last_error', "")
        except (AttributeError, TypeError):
            return ""
        return self._last_error

    def display_error(self, msg: str) -> None:
        """Forces the display of a specific error message.

        Args:
            msg: The error message to display
        """
        self._last_error = msg
        self.lastErrorChanged.emit()

    def _load_profile(self, fpath):
        """Attempts to load the profile at the provided path.

        Args:
            fpath: The file path from which to load the profile
        """
        # Check if there exists a file with this path
        if not os.path.isfile(fpath):
            self.display_error(
                f"Unable to load profile '{fpath}', no such file."
            )
            return

        # Disable the program if it is running when we're loading a
        # new profile
        # TODO: implement this for QML
        #self.ui.actionActivate.setChecked(False)
        #self.activate(False)

        # Attempt to load the new profile
        try:
            # self.profile = profile.Profile()
            # self.profile.from_xml(fpath)
            IntermediateOutput().reset()
            new_profile = profile.Profile()
            profile_was_converted = new_profile.from_xml(fpath)

            profile_folder = os.path.dirname(fpath)
            if profile_folder not in sys.path:
                sys.path = list(set(sys.path))
                sys.path.insert(0, profile_folder)

            # self._sanitize_profile(new_profile)
            self.profile = new_profile
            # self._profile_fname = fname
            # self._update_window_title()
            shared_state.current_profile = self.profile
            self.windowTitleChanged.emit()

            # Save the profile at this point if it was converted from a prior
            # profile version, as otherwise the change detection logic will
            # trip over insignificant input item additions.
            if profile_was_converted:
                self.profile.to_xml(fpath)
        except (KeyError, TypeError) as e:
            # An error occurred while parsing an existing profile,
            # creating an empty profile instead
            logging.getLogger("system").exception(
                "Invalid profile content:\n{}".format(e)
            )
            self.newProfile()
        except error.ProfileError as e:
            # Parsing the profile went wrong, stop loading and start with an
            # empty profile
            #cfg = config.Configuration()
            self.newProfile()
            self.display_error(
                f"Failed to load the profile {fpath} due to:\n\n{e}"
            )

    @Slot()
    def createOneToOneMapping(self) -> None:
        """Creates a 1:1 mapping for all inputs of the current device."""
        try:
            # Get the current device
            current_device_guid = self.ui_state.currentDevice
            if current_device_guid == str(linput.UUID_Invalid):
                self.display_error("No device selected for 1:1 mapping")
                return
                
            # This matches the Windows implementation exactly
            from gremlin import plugin_manager, common
            import uuid
            
            device_guid = uuid.UUID(current_device_guid)
            
            # Find device profile in current profile
            device_profile = None
            for dev_guid, dev_profile in self.profile.devices.items():
                if dev_guid == device_guid:
                    device_profile = dev_profile
                    break
                    
            if not device_profile:
                self.display_error("Device not found in current profile")
                return
                
            if device_profile.type != gremlin.profile.DeviceType.Joystick:
                self.display_error("Selected device is not a joystick")
                return
                
            container_plugins = plugin_manager.ContainerPlugins()
            action_plugins = plugin_manager.ActionPlugins()
            
            current_mode = self.ui_state.currentMode
            mode = device_profile.modes[current_mode]
            input_types = [
                common.InputType.JoystickAxis,
                common.InputType.JoystickButton, 
                common.InputType.JoystickHat
            ]
            type_name = {
                common.InputType.JoystickAxis: 'axis',
                common.InputType.JoystickButton: 'button',
                common.InputType.JoystickHat: 'hat'
            }
            
            main_profile = device_profile.parent
            for input_type in input_types:
                for entry in mode.config[input_type].values():
                    item_list = main_profile.list_unused_vjoy_inputs()
                    container = container_plugins.repository['basic'](entry)
                    action = action_plugins.repository['remap'](container)
                    action.input_type = input_type
                    action.vjoy_device_id = 1
                    
                    if len(item_list[1][type_name[input_type]]) > 0:
                        action.vjoy_input_id = item_list[1][type_name[input_type]][0]
                    else:
                        action.vjoy_input_id = 1
                        
                    container.add_action(action)
                    entry.containers.append(container)
            
            # Signal UI update
            self.profileChanged.emit()
            signal.reloadUi.emit()
            
        except Exception as e:
            self.display_error(f"Failed to create 1:1 mapping: {str(e)}")
    
    @Slot()
    def modifyProfile(self) -> None:
        """Opens the modify profile dialog."""
        try:
            # TODO: Implement modify profile functionality
            # This should open a dialog to modify profile metadata
            self.display_error("Modify profile functionality is not yet implemented")
            
        except Exception as e:
            self.display_error(f"Failed to modify profile: {str(e)}")
    
    @Slot()
    def openInputRepeater(self) -> None:
        """Opens the Input Repeater dialog."""
        try:
            # TODO: Implement input repeater functionality
            # This should open a dialog for repeating input sequences
            self.display_error("Input Repeater functionality is not yet implemented")
            
        except Exception as e:
            self.display_error(f"Failed to open Input Repeater: {str(e)}")
    
    @Slot()
    def openMergeAxisDialog(self) -> None:
        """Opens the Merge Axis configuration dialog."""
        try:
            # The dialog is now implemented in QML
            # It will be opened via Helpers.createComponent in Main.qml
            pass
            
        except Exception as e:
            self.display_error(f"Failed to open Merge Axis dialog: {str(e)}")
            
    @Slot(str, int, int)
    def applyMergeAxisConfiguration(self, operation: str, vjoy_device: int, vjoy_axis: int) -> None:
        """Applies a merge axis configuration."""
        try:
            # TODO: Implement actual merge axis configuration logic
            # This should integrate with the merge axis action plugin system
            self.display_error(f"Applied merge configuration: {operation} to vJoy {vjoy_device} axis {vjoy_axis}")
            
        except Exception as e:
            self.display_error(f"Failed to apply merge axis configuration: {str(e)}")
    
    @Slot()
    def openSwapDevicesDialog(self) -> None:
        """Opens the Swap Devices configuration dialog."""
        try:
            # The dialog is now implemented in QML
            # It will be opened via Helpers.createComponent in Main.qml
            pass
            
        except Exception as e:
            self.display_error(f"Failed to open Swap Devices dialog: {str(e)}")
            
    @Slot(str, str)
    def swapDeviceConfigurations(self, device1_guid: str, device2_guid: str) -> None:
        """Swaps the configuration between two devices in the profile."""
        try:
            import uuid
            
            if not self._profile:
                self.display_error("No profile loaded")
                return
                
            # Convert string GUIDs to UUID objects
            guid1 = uuid.UUID(device1_guid)
            guid2 = uuid.UUID(device2_guid)
            
            # Check if both devices exist in the profile
            if guid1 not in self._profile.devices:
                self.display_error(f"Device {device1_guid} not found in profile")
                return
                
            if guid2 not in self._profile.devices:
                self.display_error(f"Device {device2_guid} not found in profile")
                return
                
            # Swap the device configurations
            device1_config = self._profile.devices[guid1]
            device2_config = self._profile.devices[guid2]
            
            # Store the original device names to preserve them
            device1_name = device1_config.name
            device2_name = device2_config.name
            
            # Swap all modes between devices
            temp_modes = device1_config.modes
            device1_config.modes = device2_config.modes
            device2_config.modes = temp_modes
            
            # Restore original device names (don't swap names, only configurations)
            device1_config.name = device1_name
            device2_config.name = device2_name
            
            # Mark profile as modified
            self._profile.is_modified = True
            
            # Emit signal to update UI
            self.profile_changed.emit()
            
            logging.info(f"Swapped configurations between devices {device1_name} and {device2_name}")
            
        except Exception as e:
            self.display_error(f"Failed to swap device configurations: {str(e)}")
    
    @Slot()
    def generatePDFCheatsheet(self) -> None:
        """Generates a PDF cheatsheet of the current profile."""
        try:
            from gremlin import cheatsheet
            import tempfile
            import os
            
            if not self.profile:
                self.display_error("No profile loaded to generate cheatsheet from")
                return
                
            # Generate PDF cheatsheet
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, "joystick_gremlin_cheatsheet.pdf")
            
            cheatsheet.generate_cheatsheet(pdf_path, self.profile)
            
            # Open the PDF with the default system application
            if os.path.exists(pdf_path):
                import subprocess
                subprocess.run(["xdg-open", pdf_path], check=False)
            else:
                self.display_error("Failed to generate PDF file")
                
        except Exception as e:
            self.display_error(f"Failed to generate PDF cheatsheet: {str(e)}")
    
    @Slot()
    def openLogDisplay(self) -> None:
        """Opens the log display dialog."""
        try:
            # TODO: Implement log display dialog
            # This should show system and user logs in a dialog
            self.display_error("Log Display dialog is not yet implemented")
            
        except Exception as e:
            self.display_error(f"Failed to open Log Display: {str(e)}")

    @Slot()
    def openMergeAxis(self) -> None:
        """Opens the merge axis dialog."""
        try:
            # The QML dialog should handle the UI, this method is called when it opens
            logging.info("Merge axis dialog opened")
            
        except Exception as e:
            self.display_error(f"Failed to open merge axis dialog: {str(e)}")

    @Slot()
    def openSwapDevices(self) -> None:
        """Opens the swap devices dialog."""
        try:
            # The QML dialog should handle the UI, this method is called when it opens
            logging.info("Swap devices dialog opened")
            
        except Exception as e:
            self.display_error(f"Failed to open swap devices dialog: {str(e)}")

    @Slot()
    def toggleInputRepeater(self, enabled: bool) -> None:
        """Toggles the input repeater functionality."""
        try:
            if not hasattr(self, 'repeater'):
                # Initialize repeater if not exists
                from gremlin import repeater
                self.repeater = repeater.Repeater([], self._update_repeater_status)
            
            # Get event listener
            from gremlin import event_handler
            el = event_handler.EventListener()
            
            if enabled:
                # Connect events to repeater
                el.keyboard_event.connect(self.repeater.process_event)
                el.joystick_event.connect(self.repeater.process_event)
                self._update_repeater_status("Waiting for input")
                logging.info("Input repeater enabled")
            else:
                # Disconnect events from repeater
                try:
                    el.keyboard_event.disconnect(self.repeater.process_event)
                    el.joystick_event.disconnect(self.repeater.process_event)
                except:
                    pass  # Ignore if not connected
                self.repeater.stop()
                self._update_repeater_status("")
                logging.info("Input repeater disabled")
                
        except Exception as e:
            self.display_error(f"Failed to toggle input repeater: {str(e)}")

    def _update_repeater_status(self, message: str) -> None:
        """Updates the repeater status message."""
        # TODO: Update status bar or emit signal for QML to display status
        logging.info(f"Repeater status: {message}")

    # Virtual Joystick Management Methods
    
    @Slot(result=bool)
    def canCreateVirtualJoysticks(self) -> bool:
        """Check if virtual joysticks can be created."""
        return self._virtual_joystick_manager.get_permission_status()['can_create_devices']
    
    @Slot(result=list)
    def getVirtualJoystickPermissionStatus(self) -> list:
        """Get virtual joystick permission status and recommendations."""
        status = self._virtual_joystick_manager.get_permission_status()
        recommendations = self._virtual_joystick_manager.get_permission_recommendations()
        
        return [
            {
                'status': status,
                'recommendations': recommendations
            }
        ]
    
    @Slot(str, int, int, int, result=int)
    def createVirtualJoystick(self, name: str, axis_count: int = 4, button_count: int = 8, hat_count: int = 1) -> int:
        """Create a new virtual joystick device.
        
        Args:
            name: Name for the virtual device
            axis_count: Number of axes (default 4)
            button_count: Number of buttons (default 8)
            hat_count: Number of hat switches (default 1)
            
        Returns:
            Device ID for the created device, or -1 if failed
        """
        try:
            logging.info(f"🎮 Creating virtual joystick '{name}' with {axis_count} axes, {button_count} buttons, {hat_count} hats")
            
            device_id = self._virtual_joystick_manager.create_virtual_joystick(
                name, axis_count, button_count, hat_count
            )
            logging.info(f"🎮 Created virtual joystick '{name}' with ID {device_id}")
            
            # Schedule device list refresh and UI update after a delay
            # This allows time for the system to register the virtual device
            logging.info("🎮 Scheduling delayed refresh in 1000ms...")
            QtCore.QTimer.singleShot(1000, self._refresh_device_list)
            
            return device_id
            
        except VirtualJoystickPermissionError as e:
            self.display_error(f"Permission error creating virtual joystick: {str(e)}")
            return -1
        except Exception as e:
            self.display_error(f"Failed to create virtual joystick: {str(e)}")
            logging.error(f"Exception creating virtual joystick: {e}")
            import traceback
            traceback.print_exc()
            return -1
    
    @Slot(int, result=bool)
    def destroyVirtualJoystick(self, device_id: int) -> bool:
        """Destroy a virtual joystick device."""
        try:
            success = self._virtual_joystick_manager.destroy_virtual_joystick(device_id)
            if success:
                logging.info(f"Destroyed virtual joystick ID {device_id}")
                
                # Schedule device list refresh and UI update after a delay
                QtCore.QTimer.singleShot(1000, self._refresh_device_list)
                
            else:
                logging.warning(f"Failed to destroy virtual joystick ID {device_id}")
            return success
            
        except Exception as e:
            self.display_error(f"Error destroying virtual joystick: {str(e)}")
            return False
    
    def _refresh_device_list(self):
        """Refresh the device list and trigger UI updates."""
        try:
            logging.info("🔄 Starting device list refresh...")
            
            # Force device reinitialization
            device_initialization.joystick_devices_initialization()
            devices = device_initialization.joystick_devices()
            logging.info(f"🔄 Device refresh found {len(devices)} devices:")
            for i, dev in enumerate(devices):
                logging.info(f"  {i}: {dev.name} (Virtual: {dev.is_virtual})")
            
            # Trigger device change event to update UI
            event_handler.EventListener().device_change_event.emit()
            logging.info("🔄 Device change event emitted")
            
        except Exception as e:
            logging.error(f"Failed to refresh device list: {e}")
            import traceback
            traceback.print_exc()

    @Slot(result=list)
    def listVirtualJoysticks(self) -> list:
        """List all created virtual joysticks."""
        try:
            devices = self._virtual_joystick_manager.list_virtual_joysticks()
            result = []
            
            for device_id, device_summary in devices:
                result.append({
                    'id': device_id,
                    'name': device_summary.name,
                    'axis_count': device_summary.axis_count,
                    'button_count': device_summary.button_count,
                    'hat_count': device_summary.hat_count
                })
            
            return result
            
        except Exception as e:
            self.display_error(f"Error listing virtual joysticks: {str(e)}")
            return []

    def shutdown(self):
        """Mark the backend as shutting down to prevent QML errors during cleanup."""
        self._is_shutting_down = True
        if hasattr(self, 'ui_state') and self.ui_state:
            self.ui_state.shutdown()
        if hasattr(self, 'runner') and self.runner:
            self.runner.stop()
