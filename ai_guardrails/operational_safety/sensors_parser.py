from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SensorReadings:
    cpu_package_temp: Optional[float] = None
    gpu_edge_temp: Optional[float] = None
    gpu_junction_temp: Optional[float] = None
    gpu_mem_temp: Optional[float] = None
    nvme_composite_temp: Optional[float] = None
    gpu_power_watts: Optional[float] = None
    fan_rpm: Optional[float] = None
    ram_total_mb: Optional[float] = None
    ram_used_mb: Optional[float] = None
    ram_percent: Optional[float] = None
    swap_total_mb: Optional[float] = None
    swap_used_mb: Optional[float] = None
    swap_percent: Optional[float] = None
    process_cpu_percent: Optional[float] = None
    process_mem_mb: Optional[float] = None


_TEMP_RE = re.compile(
    r"([a-zA-Z][a-zA-Z0-9 _]*?)\s*:\s*[+]?\s*([0-9.]+)\s*°?C"
)
_POWER_RE = re.compile(
    r"(PPT|power\d*)\s*:\s*([0-9.]+)\s*W"
)
_FAN_RE = re.compile(
    r"fan\d*\s*:\s*([0-9.]+)\s*RPM"
)

_SLOWDOWN_KEYS = {
    "Package id 0",
    "Package id0",
}
_GPU_EDGE_KEYS = {"edge"}
_GPU_JUNCTION_KEYS = {"junction"}
_GPU_MEM_KEYS = {"mem"}
_NVME_KEYS = {"Composite"}


def _match_key(label: str) -> Optional[str]:
    stripped = label.strip()
    if stripped in _SLOWDOWN_KEYS:
        return "cpu_package"
    if stripped in _GPU_EDGE_KEYS:
        return "gpu_edge"
    if stripped in _GPU_JUNCTION_KEYS:
        return "gpu_junction"
    if stripped in _GPU_MEM_KEYS:
        return "gpu_mem"
    if stripped in _NVME_KEYS:
        return "nvme_composite"
    return None


def parse_sensors_output(text: str) -> SensorReadings:
    readings = SensorReadings()
    temps: dict[str, float] = {}

    for m in _TEMP_RE.finditer(text):
        label = m.group(1)
        value = float(m.group(2))
        key = _match_key(label)
        if key:
            temps[key] = value

    readings.cpu_package_temp = temps.get("cpu_package")
    readings.gpu_edge_temp = temps.get("gpu_edge")
    readings.gpu_junction_temp = temps.get("gpu_junction")
    readings.gpu_mem_temp = temps.get("gpu_mem")
    readings.nvme_composite_temp = temps.get("nvme_composite")

    for m in _POWER_RE.finditer(text):
        readings.gpu_power_watts = float(m.group(2))
        break

    for m in _FAN_RE.finditer(text):
        readings.fan_rpm = float(m.group(1))
        break

    return readings


def parse_meminfo() -> tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    try:
        with open("/proc/meminfo") as f:
            info = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0].rstrip(":")
                    val = int(parts[1])
                    info[key] = val
    except (OSError, ValueError):
        return None, None, None, None, None, None

    mem_total = info.get("MemTotal", 0)
    mem_available = info.get("MemAvailable", 0)
    swap_total = info.get("SwapTotal", 0)
    swap_free = info.get("SwapFree", 0)

    mem_used = mem_total - mem_available
    swap_used = swap_total - swap_free

    kb_to_mb = 1.0 / 1024.0

    ram_total_mb = mem_total * kb_to_mb if mem_total else None
    ram_used_mb = mem_used * kb_to_mb if mem_total else None
    ram_pct = (mem_used / mem_total * 100.0) if mem_total else None

    swap_total_mb = swap_total * kb_to_mb if swap_total else None
    swap_used_mb = swap_used * kb_to_mb if swap_total else None
    swap_pct = (swap_used / swap_total * 100.0) if swap_total else None

    if swap_total == 0:
        swap_pct = 0.0

    return ram_total_mb, ram_used_mb, ram_pct, swap_total_mb, swap_used_mb, swap_pct


def get_process_stats(pid: int) -> tuple[Optional[float], Optional[float]]:
    try:
        with open(f"/proc/{pid}/stat") as f:
            stat_line = f.read()
    except (OSError, ValueError):
        return None, None

    fields = stat_line.split()
    if len(fields) < 24:
        return None, None

    try:
        utime = int(fields[13])
        stime = int(fields[14])
        total_ticks = utime + stime

        try:
            with open("/proc/stat") as f:
                cpu_line = f.readline()
            cpu_fields = cpu_line.split()[1:]
            cpu_total = sum(int(v) for v in cpu_fields)
        except (OSError, ValueError):
            cpu_total = None

        try:
            with open(f"/proc/{pid}/stat") as f:
                pass
            page_size = os.sysconf("SC_PAGE_SIZE")
            rss_pages = int(fields[23])
            rss_mb = rss_pages * page_size / (1024 * 1024)
        except (OSError, ValueError, IndexError):
            rss_mb = None

        cpu_pct = (total_ticks / cpu_total * 100.0) if cpu_total else None
        return cpu_pct, rss_mb
    except (ValueError, IndexError):
        return None, None


def read_sensors_live() -> SensorReadings:
    readings = SensorReadings()

    try:
        result = subprocess.run(
            ["sensors"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout:
            parsed = parse_sensors_output(result.stdout)
            readings.cpu_package_temp = parsed.cpu_package_temp
            readings.gpu_edge_temp = parsed.gpu_edge_temp
            readings.gpu_junction_temp = parsed.gpu_junction_temp
            readings.gpu_mem_temp = parsed.gpu_mem_temp
            readings.nvme_composite_temp = parsed.nvme_composite_temp
            readings.gpu_power_watts = parsed.gpu_power_watts
            readings.fan_rpm = parsed.fan_rpm
    except (OSError, subprocess.TimeoutExpired):
        pass

    ram_total, ram_used, ram_pct, swap_total, swap_used, swap_pct = parse_meminfo()
    readings.ram_total_mb = ram_total
    readings.ram_used_mb = ram_used
    readings.ram_percent = ram_pct
    readings.swap_total_mb = swap_total
    readings.swap_used_mb = swap_used
    readings.swap_percent = swap_pct

    return readings


def enrich_with_process_stats(readings: SensorReadings, pid: int) -> None:
    cpu_pct, rss_mb = get_process_stats(pid)
    readings.process_cpu_percent = cpu_pct
    readings.process_mem_mb = rss_mb
