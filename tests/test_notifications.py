"""Tests for notification module"""
import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.notifications import NotificationManager

class TestNotificationManager(unittest.TestCase):
    def setUp(self):
        self.manager = NotificationManager()
    
    @patch('app.notifications.NotificationManager._notify_windows')
    def test_notify_calls_windows_on_win32(self, mock_win):
        self.manager.platform = 'win32'
        self.manager.notify("Title", "Message")
        mock_win.assert_called_once_with("Title", "Message", 5)
    
    @patch('app.notifications.NotificationManager._notify_macos')
    def test_notify_calls_macos_on_darwin(self, mock_mac):
        self.manager.platform = 'darwin'
        self.manager.notify("Title", "Message")
        mock_mac.assert_called_once_with("Title", "Message", 5)
    
    @patch('app.notifications.NotificationManager._notify_linux')
    def test_notify_calls_linux_on_other(self, mock_linux):
        self.manager.platform = 'linux'
        self.manager.notify("Title", "Message")
        mock_linux.assert_called_once_with("Title", "Message", 5)

if __name__ == "__main__":
    unittest.main()
