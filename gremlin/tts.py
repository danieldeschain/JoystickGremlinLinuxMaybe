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

"""
This module provides convenient access to text to speech systems.
On Linux, it uses espeak or festival for speech synthesis.
"""

import logging
import subprocess
import shutil
import threading

from . import event_handler, util


class TextToSpeech:

    def __init__(self):
        """Creates a new instance."""
        # Check for available TTS engines on Linux
        self._tts_command = None
        
        if shutil.which("espeak"):
            self._tts_command = ["espeak"]
        elif shutil.which("festival"):
            self._tts_command = ["festival", "--tts"]
        elif shutil.which("spd-say"):
            self._tts_command = ["spd-say"]
        else:
            logging.getLogger("system").warning(
                "No TTS engine found. Install espeak, festival, or speech-dispatcher for text-to-speech support."
            )
        
        # Test the TTS system
        self.speak("")

    def speak(self, text):
        """Queues the given text to be spoken using Linux TTS.

        Since the text is queued asynchronously this method returns
        immediately.

        :param text the text to speak
        """
        if not text or not self._tts_command:
            return
            
        try:
            # Run TTS in a separate thread to avoid blocking
            def speak_async():
                subprocess.run(
                    self._tts_command + [text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10
                )
            
            thread = threading.Thread(target=speak_async, daemon=True)
            thread.start()
            
        except Exception as e:
            logging.getLogger("system").error(
                "TTS encountered a problem: {}".format(e)
            )

    def set_volume(self, value):
        """Sets the volume anywhere between 0 and 100.

        :param value the new volume value
        """
        # Linux TTS volume control would require additional setup
        # This is a placeholder for compatibility
        logging.getLogger("system").debug(f"TTS volume setting not implemented on Linux: {value}")

    def set_rate(self, value):
        """Sets the speaking speed between -10 and 10.

        Negative values slow speech down while positive values speed
        it up.

        :param value the new speaking rate
        """
        # Linux TTS rate control would require additional setup
        # This is a placeholder for compatibility
        logging.getLogger("system").debug(f"TTS rate setting not implemented on Linux: {value}")


def text_substitution(text):
    """Returns the provided text after running text substitution on it.

    :param text the text to substitute parts of
    :return original text with parts substituted
    """
    # Get current mode from mode manager instead of event handler
    from . import mode_manager
    current_mode = mode_manager.ModeManager().get_current_mode()
    text = text.replace("${current_mode}", current_mode)
    return text
