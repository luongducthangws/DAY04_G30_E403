from pathlib import Path
from env_loader import load_lab_env
from tools import TOOL_FUNCTIONS as T

# Load lab environment (.env)
load_lab_env(Path.cwd())

print("=" * 50)
print("--- 1. TESTING TOOL: text_stats ---")
r1 = T['text_stats'](text="Hello research agent https://openai.com contact test@example.com")
print(r1)

print("\n--- 2. TESTING TOOL: math_eval ---")
r2 = T['math_eval'](expression="(150 + 50) / 2")
print(r2)

print("\n--- 3. TESTING TOOL: datetime_utils ---")
r3 = T['datetime_utils'](action="current_time")
print(r3)
print("=" * 50)
print("ALL QUICKTESTS EXECUTED SUCCESSFULLY!")
