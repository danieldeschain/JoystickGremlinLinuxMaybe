# -*- coding: utf-8; -*-

"""
Linux VJoy compatibility module.

This module provides the same interface as the Windows VJoy module,
but uses our Linux virtual joystick implementation.
"""

# Re-export VJoyProxy from our Linux implementation
from gremlin.vjoy_proxy import VJoyProxy

__all__ = ['VJoyProxy']
