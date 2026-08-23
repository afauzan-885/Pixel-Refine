import os

# Centralized Taichi Configuration Settings
# AOT_MODE: "1" (AOT engine active, JIT disabled), "0" (JIT compilation fallback active)
AOT_MODE = os.environ.get("AOT_MODE", "1")
