import sys
import os

src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_path)
print(f"Added to Python path: {src_path}")