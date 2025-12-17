# -*- coding: utf-8; -*-

# Copyright (C) 2025 Linux Port Contributors
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

"""
Platform-Agnostic Keyboard Interface

This module provides a unified keyboard interface that works across platforms.
On Linux, it uses linput; on Windows, it would use the old win32 implementation.

For the Linux-native version, this is the primary keyboard interface.
"""

import logging
import platform
from typing import Tuple, Optional


_logger = logging.getLogger(__name__)


class Key:
    """Represents a single keyboard key in a platform-agnostic way."""
    
    def __init__(self, name: str, scan_code: int = 0, is_extended: bool = False, virtual_code: int = 0):
        """Creates a new Key instance.
        
        Args:
            name: Human-readable key name (e.g., "A", "Space", "Enter")
            scan_code: Platform-specific scan code (optional)
            is_extended: Extended key flag (Windows-specific, optional)
            virtual_code: Virtual key code (optional)
        """
        self._name = name
        self._scan_code = scan_code
        self._is_extended = is_extended
        self._virtual_code = virtual_code
    
    @property
    def name(self) -> str:
        """Human-readable key name."""
        return self._name
    
    @property
    def scan_code(self) -> int:
        """Platform-specific scan code."""
        return self._scan_code
    
    @property
    def is_extended(self) -> bool:
        """Extended key flag (Windows-specific)."""
        return self._is_extended
    
    @property
    def virtual_code(self) -> int:
        """Virtual key code."""
        return self._virtual_code
    
    def __repr__(self) -> str:
        return f"Key(name={self._name!r}, scan_code={self._scan_code})"
    
    def __str__(self) -> str:
        return self._name


def key_from_code(scan_code: int, is_extended: bool) -> Key:
    """Create a Key object from a scan code.
    
    This is a platform-agnostic wrapper. On Linux, scan codes from evdev
    can be converted to key names. On Windows, this would use the old
    win32 API.
    
    Args:
        scan_code: The keyboard scan code
        is_extended: Whether this is an extended key (Windows-specific)
    
    Returns:
        Key object with name and code information
    """
    if platform.system() == "Linux":
        return _key_from_code_linux(scan_code, is_extended)
    else:
        # Fallback: return a generic key with the scan code as name
        _logger.warning(f"Platform {platform.system()} not fully supported, using generic key mapping")
        return Key(name=f"Key_{scan_code}", scan_code=scan_code, is_extended=is_extended)


def _key_from_code_linux(scan_code: int, is_extended: bool) -> Key:
    """Linux-specific key mapping using evdev codes.
    
    Args:
        scan_code: Linux evdev key code
        is_extended: Ignored on Linux (Windows compatibility parameter)
    
    Returns:
        Key object with evdev key name
    """
    try:
        import evdev
        from evdev import ecodes
        
        # Map scan code to evdev key name
        key_name = None
        for name, code in ecodes.keys.items():
            if code == scan_code:
                # Remove KEY_ prefix if present
                key_name = name.replace("KEY_", "") if name.startswith("KEY_") else name
                break
        
        if key_name is None:
            key_name = f"UNKNOWN_{scan_code}"
            _logger.debug(f"Unknown scan code {scan_code}, using generic name")
        
        return Key(name=key_name, scan_code=scan_code, is_extended=False, virtual_code=0)
    
    except ImportError:
        _logger.warning("evdev not available, using generic key mapping")
        return Key(name=f"Key_{scan_code}", scan_code=scan_code, is_extended=is_extended)
    except Exception as e:
        _logger.error(f"Error mapping key from code {scan_code}: {e}")
        return Key(name=f"Key_{scan_code}", scan_code=scan_code, is_extended=is_extended)


def key_from_name(name: str) -> Optional[Key]:
    """Create a Key object from a key name.
    
    Args:
        name: Human-readable key name (e.g., "A", "Space", "Enter")
    
    Returns:
        Key object, or None if name is not recognized
    """
    if platform.system() == "Linux":
        return _key_from_name_linux(name)
    else:
        _logger.warning(f"Platform {platform.system()} not fully supported")
        return Key(name=name, scan_code=0)


def _key_from_name_linux(name: str) -> Optional[Key]:
    """Linux-specific key lookup by name.
    
    Args:
        name: Key name to look up
    
    Returns:
        Key object or None
    """
    try:
        import evdev
        from evdev import ecodes
        
        # Try with KEY_ prefix
        key_name_variants = [
            name,
            f"KEY_{name}",
            f"KEY_{name.upper()}",
            name.upper()
        ]
        
        for variant in key_name_variants:
            if hasattr(ecodes, variant):
                scan_code = getattr(ecodes, variant)
                return Key(name=name, scan_code=scan_code, is_extended=False, virtual_code=0)
        
        _logger.warning(f"Key name '{name}' not found in evdev ecodes")
        return None
    
    except ImportError:
        _logger.warning("evdev not available")
        return Key(name=name, scan_code=0)
    except Exception as e:
        _logger.error(f"Error looking up key name '{name}': {e}")
        return None


# Convenience exports
__all__ = [
    'Key',
    'key_from_code',
    'key_from_name',
]
