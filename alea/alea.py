import json
import random
import string
import pyperclip
from pathlib import Path
from typing import Dict, List

class PasswordGenerator:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        config_file = Path(__file__).parent / config_path
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at {config_file}")
    
    def _get_character_pool(self) -> List[str]:
        """Generate the pool of characters based on configuration."""
        chars = []
        similar_chars = self.config.get('similar_chars', '')
        
        if self.config.get('use_lowercase', True):
            chars.extend(string.ascii_lowercase)
        if self.config.get('use_uppercase', True):
            chars.extend(string.ascii_uppercase)
        if self.config.get('use_numbers', True):
            chars.extend(string.digits)
        if self.config.get('use_special_chars', True):
            chars.extend(self.config.get('special_chars', ''))
            
        if self.config.get('exclude_similar_chars', True):
            chars = [c for c in chars if c not in similar_chars]
            
        return chars
    
    def generate_password(self) -> str:
        """Generate a random password based on configuration."""
        chars = self._get_character_pool()
        if not chars:
            raise ValueError("No character types selected in configuration")
            
        length = self.config.get('length', 16)
        password = ''.join(random.choice(chars) for _ in range(length))
        return password


def main():
    try:
        generator = PasswordGenerator()
        password = generator.generate_password()
        pyperclip.copy(password)
        print("Password has been copied to clipboard!")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main()) 