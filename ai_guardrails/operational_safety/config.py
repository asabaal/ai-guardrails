from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


_CONFIG_DIR = Path(__file__).parent / "configs"
_DEFAULT_CONFIG_PATH = _CONFIG_DIR / "ai_watchdog.default.yaml"


@dataclass
class ThresholdSet:
    warning: float
    pause: float
    kill: float


@dataclass
class WatchdogConfig:
    cpu_temp: ThresholdSet = field(default_factory=lambda: ThresholdSet(80.0, 88.0, 95.0))
    gpu_edge_temp: ThresholdSet = field(default_factory=lambda: ThresholdSet(82.0, 88.0, 95.0))
    gpu_junction_temp: ThresholdSet = field(default_factory=lambda: ThresholdSet(95.0, 102.0, 108.0))
    gpu_mem_temp: ThresholdSet = field(default_factory=lambda: ThresholdSet(82.0, 88.0, 95.0))
    nvme_temp: ThresholdSet = field(default_factory=lambda: ThresholdSet(70.0, 78.0, 82.0))
    ram_percent: ThresholdSet = field(default_factory=lambda: ThresholdSet(85.0, 95.0, 95.0))
    swap_percent: ThresholdSet = field(default_factory=lambda: ThresholdSet(50.0, 85.0, 85.0))

    poll_interval: float = 5.0
    cooldown_seconds: float = 30.0
    grace_period: float = 10.0
    log_dir: str = "./watchdog_logs"


def _threshold_set_from_dict(d: dict) -> ThresholdSet:
    return ThresholdSet(
        warning=float(d.get("warning", 0)),
        pause=float(d.get("pause", 0)),
        kill=float(d.get("kill", 0)),
    )


def _dict_to_threshold_set(ts: ThresholdSet) -> dict:
    return {"warning": ts.warning, "pause": ts.pause, "kill": ts.kill}


def load_config(path: Optional[str | Path] = None) -> WatchdogConfig:
    cfg = WatchdogConfig()

    target = Path(path) if path else _DEFAULT_CONFIG_PATH
    if not target.exists():
        return cfg

    with open(target) as f:
        raw = yaml.safe_load(f) or {}

    for attr in (
        "cpu_temp",
        "gpu_edge_temp",
        "gpu_junction_temp",
        "gpu_mem_temp",
        "nvme_temp",
        "ram_percent",
        "swap_percent",
    ):
        if attr in raw and isinstance(raw[attr], dict):
            setattr(cfg, attr, _threshold_set_from_dict(raw[attr]))

    for key in ("poll_interval", "cooldown_seconds", "grace_period", "log_dir"):
        if key in raw:
            setattr(cfg, key, raw[key])

    return cfg


def default_config_as_dict() -> dict:
    cfg = WatchdogConfig()
    return {
        "cpu_temp": _dict_to_threshold_set(cfg.cpu_temp),
        "gpu_edge_temp": _dict_to_threshold_set(cfg.gpu_edge_temp),
        "gpu_junction_temp": _dict_to_threshold_set(cfg.gpu_junction_temp),
        "gpu_mem_temp": _dict_to_threshold_set(cfg.gpu_mem_temp),
        "nvme_temp": _dict_to_threshold_set(cfg.nvme_temp),
        "ram_percent": _dict_to_threshold_set(cfg.ram_percent),
        "swap_percent": _dict_to_threshold_set(cfg.swap_percent),
        "poll_interval": cfg.poll_interval,
        "cooldown_seconds": cfg.cooldown_seconds,
        "grace_period": cfg.grace_period,
        "log_dir": cfg.log_dir,
    }
