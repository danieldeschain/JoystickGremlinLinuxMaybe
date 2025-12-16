"""pytest configuration and shared fixtures for refactoring tests."""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


@pytest.fixture(scope="session")
def project_root_path():
    """Provide absolute path to project root."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def gremlin_package_path(project_root_path):
    """Provide path to gremlin package."""
    return project_root_path / "gremlin"


@pytest.fixture(scope="session")
def all_extracted_modules():
    """List of all modules extracted in Phases 5-9."""
    return {
        # Phase 5 - device.py
        "device_information": ["gremlin.device_information"],
        "device_query": ["gremlin.device_query"],
        "device_registry": ["gremlin.device_registry"],
        "device_manager": ["gremlin.device_manager"],
        "device_constants": ["gremlin.device_constants"],
        "device_data": ["gremlin.device_data"],
        "device_joystick": ["gremlin.device_joystick"],
        
        # Phase 5 - code_runner.py
        "code_runner_modules.callback_registry": ["gremlin.code_runner_modules.callback_registry"],
        "code_runner_modules.event_loop": ["gremlin.code_runner_modules.event_loop"],
        "code_runner_modules.runner": ["gremlin.code_runner_modules.runner"],
        
        # Phase 5 - map_to_vjoy
        "map_to_vjoy_modules.axis_handler": ["action_plugins.map_to_vjoy.map_to_vjoy_modules.axis_handler"],
        "map_to_vjoy_modules.button_handler": ["action_plugins.map_to_vjoy.map_to_vjoy_modules.button_handler"],
        "map_to_vjoy_modules.hat_handler": ["action_plugins.map_to_vjoy.map_to_vjoy_modules.hat_handler"],
        
        # Phase 5 - ui/profile.py
        "profile_modules.device_widget": ["gremlin.ui.profile_modules.device_widget"],
        "profile_modules.input_item_widget": ["gremlin.ui.profile_modules.input_item_widget"],
        "profile_modules.tree_model": ["gremlin.ui.profile_modules.tree_model"],
        "profile_modules.widget_registry": ["gremlin.ui.profile_modules.widget_registry"],
        "profile_modules.delegates": ["gremlin.ui.profile_modules.delegates"],
        
        # Phase 7 - user_script.py
        "user_script_modules.registries": ["gremlin.user_script_modules.registries"],
        "user_script_modules.plugins": ["gremlin.user_script_modules.plugins"],
        "user_script_modules.script": ["gremlin.user_script_modules.script"],
        "user_script_modules.variables": ["gremlin.user_script_modules.variables"],
        
        # Phase 8 - config.py
        "config_modules.core": ["gremlin.config_modules.core"],
        "config_modules.persistence": ["gremlin.config_modules.persistence"],
        "config_modules.registry": ["gremlin.config_modules.registry"],
        "config_modules.accessors": ["gremlin.config_modules.accessors"],
        "config_modules.metadata": ["gremlin.config_modules.metadata"],
        "config_modules.structure": ["gremlin.config_modules.structure"],
        "config_modules.calibration": ["gremlin.config_modules.calibration"],
        
        # Phase 9 - cheatsheet.py
        "cheatsheet_modules.data": ["gremlin.cheatsheet_modules.data"],
        "cheatsheet_modules.layout": ["gremlin.cheatsheet_modules.layout"],
        "cheatsheet_modules.generators": ["gremlin.cheatsheet_modules.generators"],
        "cheatsheet_modules.helpers": ["gremlin.cheatsheet_modules.helpers"],
    }
