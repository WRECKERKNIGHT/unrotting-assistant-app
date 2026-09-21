"""Tests for configuration module"""
import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import load_config, save_config, validate_config, DEFAULT_CONFIG

class TestConfig(unittest.TestCase):
    def test_default_config(self):
        cfg = DEFAULT_CONFIG.copy()
        self.assertEqual(cfg["focus_duration_minutes"], 45)
        self.assertEqual(cfg["break_duration_minutes"], 15)
        self.assertTrue(cfg["strict_mode"])
    
    def test_validate_config_valid(self):
        cfg = DEFAULT_CONFIG.copy()
        is_valid, errors = validate_config(cfg)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_config_invalid_timing(self):
        cfg = DEFAULT_CONFIG.copy()
        cfg["focus_duration_minutes"] = 30
        is_valid, errors = validate_config(cfg)
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)

if __name__ == "__main__":
    unittest.main()
