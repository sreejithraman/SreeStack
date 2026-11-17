"""Harmless process-tree fixture used only by the isolated fitness gate."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def emit(path, token, event):
    entry = {"token": token, "event": event, "time": time.monotonic(),
             "pid": os.getpid(), "pgid": os.getpgrp()}
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(descriptor, (json.dumps(entry) + "\n").encode())
    finally:
        os.close(descriptor)


def main():
    path, token, mode, duration = sys.argv[1:]
    duration = float(duration)
    ready = Path(path).with_name(token + '.ready')
    if mode in {"leaf", "detached-leaf"}:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        emit(path, token, "descendant_start")
        ready.touch()
        time.sleep(duration)
        emit(path, token, "descendant_end")
        return
    emit(path, token, "start")
    if mode in {"linger", "exit-linger", "detach"}:
        subprocess.Popen(
            [sys.executable, __file__, path, token,
             "detached-leaf" if mode == "detach" else "leaf", "20"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=mode == "detach",
        )
        deadline = time.monotonic() + 5
        while not ready.exists():
            if time.monotonic() > deadline:
                raise TimeoutError("descendant did not become ready")
            time.sleep(.01)
        emit(path, token, "descendant_ready")
        if mode == "exit-linger":
            emit(path, token, "end")
            return
    time.sleep(duration)
    emit(path, token, "end")


if __name__ == "__main__":
    main()
