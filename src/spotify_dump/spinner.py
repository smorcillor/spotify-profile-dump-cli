"""Animated terminal spinner for progress feedback."""

import itertools
import sys
import threading
import time


BRAILLE_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class Spinner:
    """Context manager that shows an animated spinner while work is in progress.

    Usage:
        with Spinner("Fetching saved tracks") as s:
            data = do_work()
            s.done(f"{len(data)} saved tracks")
    """

    def __init__(self, message: str, interval: float = 0.08) -> None:
        self._message = message
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._done_text: str | None = None

    def __enter__(self) -> "Spinner":
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()

        # Clear the spinner line
        self._clear_line()

        if exc_type is not None:
            sys.stdout.write(f"\033[31m✗\033[0m {self._message}... failed\n")
            sys.stdout.flush()
        elif self._done_text:
            sys.stdout.write(f"\033[32m✓\033[0m {self._done_text}\n")
            sys.stdout.flush()

    def done(self, text: str) -> None:
        """Set the completion message shown after the spinner stops."""
        self._done_text = text

    def _spin(self) -> None:
        for frame in itertools.cycle(BRAILLE_FRAMES):
            if self._stop_event.is_set():
                break
            sys.stdout.write(f"\r\033[36m{frame}\033[0m {self._message}...")
            sys.stdout.flush()
            self._stop_event.wait(self._interval)

    def _clear_line(self) -> None:
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
