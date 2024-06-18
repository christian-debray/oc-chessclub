from pathlib import Path
APPDIR: Path = Path(__file__).parent.resolve()
DATADIR = Path(APPDIR.parent, 'data')
# Setup keyboard event detection.
# support for keyboard events in the chessclub app remains optional.
# the ansio package is still in early alpha,
# You can deactivate ansio by changing the KEYBOARD_MODULE to None or ""
#
# KEYBOARD_MODULE= None
KEYBOARD_MODULE = "ansio"
