# gui/window_state.py
"""
Global window state manager to preserve window state (maximized/normal) 
across interface transitions.
"""

from PyQt5 import QtCore, QtWidgets


class WindowStateManager:
    """
    Singleton class to track and apply window state across interface transitions.
    When user is in fullscreen and switches interface, new window opens fullscreen.
    When user is in normal/minimized, new window opens in that state.
    """
    _instance = None
    _is_maximized = True  # Default to maximized
    _geometry = None  # Store geometry for normal state
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def save_state(cls, window):
        """Save the current window state before closing"""
        cls._is_maximized = window.isMaximized()
        if not cls._is_maximized:
            cls._geometry = window.geometry()
    
    @classmethod
    def apply_state(cls, window):
        """Apply the saved state to a new window"""
        # Set window flags for proper window controls
        window.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        
        if cls._is_maximized:
            window.showMaximized()
        else:
            if cls._geometry:
                window.setGeometry(cls._geometry)
            window.showNormal()
    
    @classmethod
    def is_maximized(cls):
        """Check if windows should open maximized"""
        return cls._is_maximized
    
    @classmethod
    def set_maximized(cls, maximized):
        """Set the maximized state"""
        cls._is_maximized = maximized


def save_window_state(window):
    """Convenience function to save window state"""
    WindowStateManager.save_state(window)


def apply_window_state(window):
    """Convenience function to apply window state"""
    WindowStateManager.apply_state(window)
