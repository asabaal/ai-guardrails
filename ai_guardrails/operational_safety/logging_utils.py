from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .sensors_parser import SensorReadings


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(command: list[str]) -> str:
    s = "_".join(command)
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in s)[:60]


class WatchdogLogger:
    def __init__(self, log_dir: str, command: list[str]) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        slug = _slug(command)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = self.log_dir / f"{ts}_{slug}.jsonl"
        self.start_time = time.monotonic()
        self.intervention_count = 0
        self.command = command
        self._log_file = open(self.log_path, "a")

    def log_poll(
        self,
        readings: SensorReadings,
        action: str,
        reason: str = "",
    ) -> None:
        elapsed = round(time.monotonic() - self.start_time, 2)
        entry = {
            "ts": _ts(),
            "elapsed_s": elapsed,
            "action": action,
            "reason": reason,
            "readings": {
                k: v for k, v in asdict(readings).items() if v is not None
            },
        }
        self._log_file.write(json.dumps(entry) + "\n")
        self._log_file.flush()

    def log_summary(
        self,
        exit_code: Optional[int],
        reason: str = "",
    ) -> None:
        elapsed = round(time.monotonic() - self.start_time, 2)
        entry = {
            "ts": _ts(),
            "elapsed_s": elapsed,
            "action": "summary",
            "reason": reason,
            "exit_code": exit_code,
            "intervention_count": self.intervention_count,
            "command": self.command,
        }
        self._log_file.write(json.dumps(entry) + "\n")
        self._log_file.flush()

    def close(self) -> None:
        self._log_file.close()

    @property
    def log_path_str(self) -> str:
        return str(self.log_path)


BOLD = "\033[1m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"


def _fmt_temp(value: Optional[float], warn: float, kill: float) -> str:
    if value is None:
        return "N/A"
    s = f"{value:.1f}C"
    if value >= kill:
        return f"{RED}{BOLD}{s}{RESET}"
    if value >= warn:
        return f"{YELLOW}{s}{RESET}"
    return f"{GREEN}{s}{RESET}"


def _fmt_pct(value: Optional[float], warn: float, kill: float) -> str:
    if value is None:
        return "N/A"
    s = f"{value:.1f}%"
    if value >= kill:
        return f"{RED}{BOLD}{s}{RESET}"
    if value >= warn:
        return f"{YELLOW}{s}{RESET}"
    return f"{GREEN}{s}{RESET}"


def print_status(
    readings: SensorReadings,
    elapsed: float,
    status: str,
    cfg: "WatchdogConfig",
) -> None:
    from .config import WatchdogConfig

    cpu = _fmt_temp(readings.cpu_package_temp, cfg.cpu_temp.warning, cfg.cpu_temp.kill)
    gpu_e = _fmt_temp(readings.gpu_edge_temp, cfg.gpu_edge_temp.warning, cfg.gpu_edge_temp.kill)
    gpu_j = _fmt_temp(readings.gpu_junction_temp, cfg.gpu_junction_temp.warning, cfg.gpu_junction_temp.kill)
    gpu_m = _fmt_temp(readings.gpu_mem_temp, cfg.gpu_mem_temp.warning, cfg.gpu_mem_temp.kill)
    nvme = _fmt_temp(readings.nvme_composite_temp, cfg.nvme_temp.warning, cfg.nvme_temp.kill)
    ram = _fmt_pct(readings.ram_percent, cfg.ram_percent.warning, cfg.ram_percent.kill)
    swap = _fmt_pct(readings.swap_percent, cfg.swap_percent.warning, cfg.swap_percent.kill)
    power = f"{readings.gpu_power_watts:.1f}W" if readings.gpu_power_watts is not None else "N/A"
    fan = f"{readings.fan_rpm:.0f}RPM" if readings.fan_rpm is not None else "N/A"

    status_color = GREEN
    if status == "PAUSED":
        status_color = YELLOW
    elif status in ("KILLED", "WARNING"):
        status_color = RED

    line = (
        f"{CYAN}[watchdog {elapsed:.0f}s]{RESET} "
        f"CPU:{cpu} GPU-E:{gpu_e} GPU-J:{gpu_j} GPU-M:{gpu_m} "
        f"NVMe:{nvme} RAM:{ram} Swap:{swap} "
        f"PWR:{power} FAN:{fan} "
        f"[{status_color}{status}{RESET}]"
    )
    sys.stderr.write(f"\r\033[K{line}")
    sys.stderr.flush()


def print_warning(msg: str) -> None:
    sys.stderr.write(f"\n{YELLOW}WARNING: {msg}{RESET}\n")
    sys.stderr.flush()


def print_intervention(msg: str) -> None:
    sys.stderr.write(f"\n{RED}INTERVENTION: {msg}{RESET}\n")
    sys.stderr.flush()


def print_summary(
    elapsed: float,
    exit_code: Optional[int],
    interventions: int,
    log_path: str,
) -> None:
    sys.stderr.write(f"\n")
    sys.stderr.write(f"{CYAN}{'='*60}{RESET}\n")
    sys.stderr.write(f"  Watchdog Summary\n")
    sys.stderr.write(f"  Duration: {elapsed:.1f}s\n")
    sys.stderr.write(f"  Exit code: {exit_code}\n")
    sys.stderr.write(f"  Interventions: {interventions}\n")
    sys.stderr.write(f"  Log: {log_path}\n")
    sys.stderr.write(f"{CYAN}{'='*60}{RESET}\n")
    sys.stderr.flush()
