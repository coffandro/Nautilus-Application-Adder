import sys
import os
import gi

gi.require_version("Gtk", "4.0")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'NautilusApplications'))
from NautilusApplications import NautilusAddDesktopFile

