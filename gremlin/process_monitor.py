# -*- coding: utf-8; -*-

# Copyright (C) 2015 - 2024 Lionel Ott
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

import os
import time
import threading
import subprocess
import logging

from PySide6 import QtCore


class ProcessMonitor(QtCore.QObject):

    """Monitors the currently active window process.

    This class continuously monitors the active window and whenever
    it changes the path to the executable is retrieved and signaled
    to the rest of the system using Qt's signal / slot mechanism.
    """

    # Signal emitted when the active window changes
    process_changed = QtCore.Signal(str)

    def __init__(self):
        """Creates a new instance."""
        QtCore.QObject.__init__(self)
        self._current_path = ""
        self._current_pid = -1
        self.running = False
        self._update_thread = None

    def start(self):
        """Starts monitoring the current process."""
        if not self.running:
            self.running = True
            self._update_thread = threading.Thread(
                target=self._update
            )
            self._update_thread.start()

    def stop(self):
        """Stops monitoring the current process."""
        self.running = False
        if self._update_thread is not None:
            self._update_thread.join()

    def _get_active_window_pid(self):
        """Get the PID of the currently active window using xdotool or xprop."""
        try:
            # Try xdotool first
            result = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowpid"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        try:
            # Try xprop as fallback
            result = subprocess.run(
                ["xprop", "-root", "_NET_ACTIVE_WINDOW"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                window_id = result.stdout.split()[-1]
                if window_id != "0x0":
                    pid_result = subprocess.run(
                        ["xprop", "-id", window_id, "_NET_WM_PID"],
                        capture_output=True,
                        text=True,
                        timeout=1
                    )
                    if pid_result.returncode == 0:
                        return int(pid_result.stdout.split()[-1])
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass

        return -1

    def _get_process_path(self, pid):
        """Get the executable path for a given PID."""
        try:
            # Read the executable path from /proc/pid/exe
            exe_path = os.readlink(f"/proc/{pid}/exe")
            return os.path.normpath(exe_path)
        except (OSError, FileNotFoundError):
            return ""

    def _update(self):
        """Monitors the active process for changes."""
        while self.running:
            pid = self._get_active_window_pid()

            if pid != self._current_pid and pid != -1:
                self._current_pid = pid
                path = self._get_process_path(pid)
                
                if path and path != self._current_path:
                    self._current_path = path
                    self.process_changed.emit(self.current_path)

            time.sleep(1.0)

    @property
    def current_path(self):
        """Returns the path to the currently active executable.

        :return path to the currently active executable
        """
        return self._current_path


def list_current_processes():
    """Returns a list of executable paths to currently active processes.

    :return list of active process executable paths
    """
    process_list = []
    try:
        # Read all processes from /proc
        for pid_dir in os.listdir("/proc"):
            if pid_dir.isdigit():
                try:
                    exe_path = os.readlink(f"/proc/{pid_dir}/exe")
                    if exe_path and os.path.exists(exe_path):
                        process_list.append(os.path.normpath(exe_path))
                except (OSError, FileNotFoundError):
                    continue
    except OSError:
        logging.getLogger("system").error("Failed to read process list from /proc")
    
    return sorted(set(process_list))
