from __future__ import annotations

import pytest

from ai_guardrails.operational_safety.ai_watchdog import Action, evaluate_readings
from ai_guardrails.operational_safety.config import WatchdogConfig
from ai_guardrails.operational_safety.sensors_parser import SensorReadings


@pytest.fixture
def cfg() -> WatchdogConfig:
    return WatchdogConfig()


def _readings(**kwargs) -> SensorReadings:
    defaults = dict(
        cpu_package_temp=None,
        gpu_edge_temp=None,
        gpu_junction_temp=None,
        gpu_mem_temp=None,
        nvme_composite_temp=None,
        gpu_power_watts=None,
        fan_rpm=None,
        ram_percent=None,
        swap_percent=None,
    )
    defaults.update(kwargs)
    return SensorReadings(**defaults)


class TestNoThresholdExceeded:
    def test_all_none(self, cfg):
        r = _readings()
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.NONE
        assert reasons == []

    def test_all_below_warning(self, cfg):
        r = _readings(
            cpu_package_temp=40.0,
            gpu_edge_temp=50.0,
            gpu_junction_temp=60.0,
            gpu_mem_temp=50.0,
            nvme_composite_temp=40.0,
            ram_percent=50.0,
            swap_percent=20.0,
        )
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.NONE
        assert reasons == []


class TestWarningThresholds:
    def test_cpu_warning(self, cfg):
        r = _readings(cpu_package_temp=81.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("CPU package" in reason for reason in reasons)

    def test_gpu_edge_warning(self, cfg):
        r = _readings(gpu_edge_temp=83.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("GPU edge" in reason for reason in reasons)

    def test_gpu_junction_warning(self, cfg):
        r = _readings(gpu_junction_temp=96.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("GPU junction" in reason for reason in reasons)

    def test_gpu_mem_warning(self, cfg):
        r = _readings(gpu_mem_temp=83.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("GPU memory" in reason for reason in reasons)

    def test_nvme_warning(self, cfg):
        r = _readings(nvme_composite_temp=71.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("NVMe" in reason for reason in reasons)

    def test_ram_warning(self, cfg):
        r = _readings(ram_percent=86.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("RAM" in reason for reason in reasons)

    def test_swap_warning(self, cfg):
        r = _readings(swap_percent=51.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert any("Swap" in reason for reason in reasons)


class TestPauseThresholds:
    def test_cpu_pause(self, cfg):
        r = _readings(cpu_package_temp=89.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.PAUSE
        assert any("CPU package" in reason for reason in reasons)

    def test_gpu_edge_pause(self, cfg):
        r = _readings(gpu_edge_temp=89.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.PAUSE
        assert any("GPU edge" in reason for reason in reasons)

    def test_gpu_junction_pause(self, cfg):
        r = _readings(gpu_junction_temp=103.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.PAUSE
        assert any("GPU junction" in reason for reason in reasons)

    def test_gpu_mem_pause(self, cfg):
        r = _readings(gpu_mem_temp=89.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.PAUSE
        assert any("GPU memory" in reason for reason in reasons)

    def test_nvme_pause(self, cfg):
        r = _readings(nvme_composite_temp=79.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.PAUSE
        assert any("NVMe" in reason for reason in reasons)


class TestKillThresholds:
    def test_cpu_kill(self, cfg):
        r = _readings(cpu_package_temp=96.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("CPU package" in reason for reason in reasons)

    def test_gpu_edge_kill(self, cfg):
        r = _readings(gpu_edge_temp=96.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("GPU edge" in reason for reason in reasons)

    def test_gpu_junction_kill(self, cfg):
        r = _readings(gpu_junction_temp=109.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("GPU junction" in reason for reason in reasons)

    def test_gpu_mem_kill(self, cfg):
        r = _readings(gpu_mem_temp=96.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("GPU memory" in reason for reason in reasons)

    def test_nvme_kill(self, cfg):
        r = _readings(nvme_composite_temp=83.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("NVMe" in reason for reason in reasons)

    def test_ram_kill(self, cfg):
        r = _readings(ram_percent=96.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("RAM" in reason for reason in reasons)

    def test_swap_kill(self, cfg):
        r = _readings(swap_percent=86.0)
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL
        assert any("Swap" in reason for reason in reasons)


class TestBoundaryConditions:
    def test_cpu_exactly_at_warning(self, cfg):
        r = _readings(cpu_package_temp=80.0)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.WARNING

    def test_cpu_exactly_at_pause(self, cfg):
        r = _readings(cpu_package_temp=88.0)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.PAUSE

    def test_cpu_exactly_at_kill(self, cfg):
        r = _readings(cpu_package_temp=95.0)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.KILL

    def test_cpu_one_below_warning(self, cfg):
        r = _readings(cpu_package_temp=79.9)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.NONE

    def test_gpu_edge_one_above_warning(self, cfg):
        r = _readings(gpu_edge_temp=82.1)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.WARNING

    def test_multiple_warnings_takes_highest(self, cfg):
        r = _readings(
            cpu_package_temp=81.0,
            gpu_edge_temp=83.0,
        )
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.WARNING
        assert len(reasons) == 2

    def test_kill_takes_priority_over_pause(self, cfg):
        r = _readings(
            cpu_package_temp=89.0,
            gpu_edge_temp=96.0,
        )
        action, reasons = evaluate_readings(r, cfg)
        assert action == Action.KILL

    def test_pause_takes_priority_over_warning(self, cfg):
        r = _readings(
            cpu_package_temp=81.0,
            gpu_edge_temp=89.0,
        )
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.PAUSE


class TestCustomConfig:
    def test_custom_thresholds(self):
        from ai_guardrails.operational_safety.config import ThresholdSet
        cfg = WatchdogConfig(
            cpu_temp=ThresholdSet(warning=60.0, pause=70.0, kill=80.0),
        )
        r = _readings(cpu_package_temp=65.0)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.WARNING

    def test_lowered_kill_threshold(self):
        from ai_guardrails.operational_safety.config import ThresholdSet
        cfg = WatchdogConfig(
            gpu_edge_temp=ThresholdSet(warning=50.0, pause=60.0, kill=70.0),
        )
        r = _readings(gpu_edge_temp=71.0)
        action, _ = evaluate_readings(r, cfg)
        assert action == Action.KILL
