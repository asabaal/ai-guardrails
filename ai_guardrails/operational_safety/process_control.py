from __future__ import annotations

import os
import signal
import subprocess
import time
from typing import Optional


class ChildProcess:
    def __init__(self, command: list[str]) -> None:
        self.command = command
        self.proc: Optional[subprocess.Popen] = None
        self.pgid: Optional[int] = None

    def start(self) -> None:
        self.proc = subprocess.Popen(
            self.command,
            preexec_fn=os.setpgrp,
        )
        self.pgid = self.proc.pid

    @property
    def pid(self) -> Optional[int]:
        return self.proc.pid if self.proc else None

    @property
    def running(self) -> bool:
        if self.proc is None:
            return False
        return self.proc.poll() is None

    @property
    def exit_code(self) -> Optional[int]:
        if self.proc is None:
            return None
        return self.proc.returncode

    def pause(self) -> None:
        if self.pgid is not None:
            try:
                os.killpg(self.pgid, signal.SIGSTOP)
            except ProcessLookupError:
                pass

    def resume(self) -> None:
        if self.pgid is not None:
            try:
                os.killpg(self.pgid, signal.SIGCONT)
            except ProcessLookupError:
                pass

    def terminate(self) -> None:
        if self.pgid is not None:
            try:
                os.killpg(self.pgid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    def kill(self) -> None:
        if self.pgid is not None:
            try:
                os.killpg(self.pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def wait(self, timeout: Optional[float] = None) -> int:
        if self.proc is None:
            return -1
        return self.proc.wait(timeout=timeout)

    def terminate_with_grace(self, grace_period: float = 10.0) -> int:
        self.terminate()
        try:
            self.proc.wait(timeout=grace_period)
        except subprocess.TimeoutExpired:
            self.kill()
            self.proc.wait(timeout=5)
        return self.proc.returncode if self.proc else -1
