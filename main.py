from app.controllers.chessclubapp import ChessclubApp
import argparse
import logging
from pathlib import Path
import app
logger = logging.getLogger()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser("chessclub_app")
    parser.add_argument("--script", help="Execute a sequence of commands from a file")
    parser.add_argument(
        "--debug",
        "-D",
        const=logging.DEBUG,
        action="store_const",
        help="Set logger debugging level to DEBUG.",
    )
    parser.add_argument(
        "--log",
        default="logs/debug.log",
        help="Set the logfile path. Defaults to logs/debug.log. Set to 0 or empty string to disable logging."
    )
    return parser.parse_args()


def load_script(script_path: str = None) -> list[str]:
    """Loads a script from a path"""
    if not (script_path and Path(script_path).exists()):
        return None
    script = None
    try:
        with open(script_path) as sf:
            script = sf.readlines()
    except Exception as e:
        logger.error(f"Failed to open script file {script_path}: {e}")
    return script


def setup_logging(logfile: str = None, debug: bool = False):
    """Setup the logger.

    Logfile should be a path relative to APPDIR."""
    if logfile is not None:
        log_path = Path(app.APPDIR.parent, logfile).resolve()
        loglvl = logging.ERROR
        if not log_path.exists():
            if not log_path.parent.exists():
                log_path.parent.mkdir(mode=0o777)
        if debug:
            loglvl = logging.DEBUG
        logging.basicConfig(filename=log_path, level=loglvl)


if __name__ == "__main__":
    # parse command line arguments and load script
    #
    args = parse_args()
    script = load_script(args.script)

    # setup logging: write logs to logs/debug.log
    #
    setup_logging(args.log or None, args.debug)

    # now launch the app
    #
    chessclub_app = ChessclubApp()
    chessclub_app.run(cmd_script=script)
