"""
Compatibility patches for Python 2 and 3.

Only to be maintained until it becomes too much of a pain, at which point I should
look at something like 2to3.
"""

try:
    # Python 2.7
    to_long = long
except NameError:
    # Python 3.3
    to_long = int
