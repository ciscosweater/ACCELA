# This file contains constants and assets used throughout the UI.

# --- Blacklist ---
DEPOT_BLACKLIST = [
    228981, 228982, 228983, 228984, 228985, 228986, 228987, 228988,
    228989, 229000, 229001, 229002, 229003, 229004, 229005, 229006,
    229007, 229010, 229011, 229012, 229020, 229030, 229031, 229032,
    229033, 228990
]

# --- SVG Icons ---
# Using raw string literals (r"""...""") to avoid issues with backslashes
POWER_SVG = r"""
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path>
  <line x1="12" y1="2" x2="12" y2="12"></line>
</svg>
"""

GEAR_SVG = r"""
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 20.94c-4.94 0-8.94-4-8.94-8.94S7.06 3.06 12 3.06s8.94 4 8.94 8.94-4 8.94-8.94 8.94z"></path>
  <path d="M12 15.94c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"></path>
  <path d="M12 3.06L12 1"></path>
  <path d="M12 23L12 20.94"></path>
  <path d="M4.22 4.22L5.64 5.64"></path>
  <path d="M18.36 18.36L19.78 19.78"></path>
  <path d="M1 12L3.06 12"></path>
  <path d="M20.94 12L23 12"></path>
  <path d="M4.22 19.78L5.64 18.36"></path>
  <path d="M18.36 5.64L19.78 4.22"></path>
</svg>
"""
