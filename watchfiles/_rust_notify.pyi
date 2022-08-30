from typing import Any, List, Literal, Optional, Protocol, Set, Tuple, Union

__all__ = 'RustNotify', 'WatchfilesRustInternalError'

__version__: str
"""The package version as defined in `Cargo.toml`, modified to match python's versioning semantics."""

class AbstractEvent(Protocol):
    def is_set(self) -> bool: ...

class RustNotify:
    """
    Interface to the Rust [notify](https://crates.io/crates/notify) crate which does
    the heavy lifting of watching for file changes and grouping them into events.
    """

    def __init__(
        self, watch_paths: List[str], debug: bool, force_polling: bool, poll_delay_ms: int, recursive: bool
    ) -> None:
        """
        Create a new `RustNotify` instance and start a thread to watch for changes.

        `FileNotFoundError` is raised if any of the paths do not exist.

        Args:
            watch_paths: file system paths to watch for changes, can be directories or files
            debug: if true, print details about all events to stderr
            force_polling: if true, always use polling instead of file system notifications
            poll_delay_ms: delay between polling for changes, only used if `force_polling=True`
            recursive: if `True`, watch for changes in sub-directories recursively, otherwise watch only for changes in
                the top-level directory, default is `True`.
        """
    def watch(
        self,
        debounce_ms: int,
        step_ms: int,
        timeout_ms: int,
        stop_event: Optional[AbstractEvent],
    ) -> Union[Set[Tuple[int, str]], Literal['signal', 'stop', 'timeout']]:
        """
        Watch for changes.

        This method will wait `timeout_ms` milliseconds for changes, but once a change is detected,
        it will group changes and return in no more than `debounce_ms` milliseconds.

        The GIL is released during a `step_ms` sleep on each iteration to avoid
        blocking python.

        Args:
            debounce_ms: maximum time in milliseconds to group changes over before returning.
            step_ms: time to wait for new changes in milliseconds, if no changes are detected
                in this time, and at least one change has been detected, the changes are yielded.
            timeout_ms: maximum time in milliseconds to wait for changes before returning,
                `0` means wait indefinitely, `debounce_ms` takes precedence over `timeout_ms` once
                a change is detected.
            stop_event: event to check on every iteration to see if this function should return early.
                The event should be an object which has an `is_set()` method which returns a boolean.

        Returns:
            See below.

        Return values have the following meanings:

        * Change details as a `set` of `(event_type, path)` tuples, the event types are ints which match
          [`Change`][watchfiles.Change], `path` is a string representing the path of the file that changed
        * `'signal'` string, if a signal was received
        * `'stop'` string, if the `stop_event` was set
        * `'timeout'` string, if `timeout_ms` was exceeded
        """
    def __enter__(self) -> 'RustNotify':
        """
        Does nothing, but allows `RustNotify` to be used as a context manager.

        !!! note

            The watching thead is created when an instance is initiated, not on `__enter__`.
        """
    def __exit__(self, *args: Any) -> None:
        """
        Calls [`close`][watchfiles._rust_notify.RustNotify.close].
        """
    def close(self) -> None:
        """
        Stops the watching thread. After `close` is called, the `RustNotify` instance can no
        longer be used, calls to [`watch`][watchfiles._rust_notify.RustNotify.watch] will raise a `RuntimeError`.

        !!! note

            `close` is not required, just deleting the `RustNotify` instance will kill the thread
            implicitly.

            As per [#163](https://github.com/samuelcolvin/watchfiles/issues/163) `close()` is only required because
            in the event of an error, the traceback in `sys.exc_info` keeps a reference to `watchfiles.watch`'s
            frame, so you can't rely on the `RustNotify` object being deleted, and thereby stopping
            the watching thread.
        """

class WatchfilesRustInternalError(RuntimeError):
    """
    Raised when RustNotify encounters an unknown error.

    If you get this a lot, please check [github](https://github.com/samuelcolvin/watchfiles/issues) issues
    and create a new issue if your problem is not discussed.
    """
