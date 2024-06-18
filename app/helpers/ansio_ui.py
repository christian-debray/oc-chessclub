# ansio: alpha revision
# detect keyboard events.
# see https://github.com/nineteendo/ansio.git
import ansio
import ansio.input
import app.helpers.ansi as ansi


def proceed_any_key(msg="Press any key to proceed", timeout: float = None):
    print(ansi.Formatter.format(msg, ansi.Formatter.CYAN))
    with ansio.raw_input:
        ansio.input.get_input_event(timeout=timeout)


def confirm(msg="press Y to confirm", timeout: float = None) -> bool:
    """Prompts user to confirm an action y pressing a specific key ('y').

    Returns True if user confirmed, False otherwise."""
    print(ansi.Formatter.format(msg, ansi.Formatter.CYAN))
    evt = None
    with ansio.raw_input:
        evt = ansio.input.get_input_event(timeout=timeout)
    if evt:
        return evt.upper() == "Y"
    return False
