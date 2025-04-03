import unittest
from alea import PasswordGenerator
import json
from pathlib import Path


class TestPasswordGenerator(unittest.TestCase):
    def setUp(self):
        self.test_config = {
            "length": 12,
            "use_uppercase": True,
            "use_lowercase": True,
            "use_numbers": True,
            "use_special_chars": True,
            "special_chars": "@#$%",
            "exclude_similar_chars": True
        }
        
        # Create a temporary test config file
        self.config_path = "test_config.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
            
        self.generator = PasswordGenerator(self.config_path)
    
    def tearDown(self):
        # Clean up the test config file
        Path(self.config_path).unlink()
    
    def test_password_length(self):
        password = self.generator.generate_password()
        self.assertEqual(len(password), self.test_config["length"])
    
    def test_password_characters(self):
        password = self.generator.generate_password()
        # Check that password contains at least one of each required character type
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
       
    def test_invalid_config_path(self):
        with self.assertRaises(FileNotFoundError):
            PasswordGenerator("nonexistent_config.json")
    
    def test_empty_character_pool(self):
        # Create a config with all character types disabled
        empty_config = {
            "length": 12,
            "use_uppercase": False,
            "use_lowercase": False,
            "use_numbers": False,
            "use_special_chars": False,
            "special_chars": "",
            "exclude_similar_chars": True
        }
        
        with open("empty_config.json", 'w') as f:
            json.dump(empty_config, f)
            
        generator = PasswordGenerator("empty_config.json")
        with self.assertRaises(ValueError):
            generator.generate_password()
            
        Path("empty_config.json").unlink()

if __name__ == '__main__':
    unittest.main() 
