from __future__ import annotations

import pytest

from ai_guardrails.operational_safety.sensors_parser import (
    SensorReadings,
    parse_sensors_output,
)


SAMPLE_SENSORS_OUTPUT = """\
amdgpu-pci-0300
Adapter: PCI adapter
vddgfx:      856.00 mV
fan1:           0 RPM  (min =    0 RPM, max = 3900 RPM)
edge:         +61.0°C  (crit = +100.0°C, hyst = -273.1°C)
                       (emerg = +105.0°C)
junction:     +64.0°C  (crit = +110.0°C, hyst = -273.1°C)
                       (emerg = +115.0°C)
mem:          +62.0°C  (crit = +100.0°C, hyst = -273.1°C)
                       (emerg = +105.0°C)
PPT:          25.00 W  (cap = 255.00 W)

coretemp-isa-0000
Adapter: ISA adapter
Package id 0:  +57.0°C  (high = +80.0°C, crit = +100.0°C)
Core 0:        +50.0°C  (high = +80.0°C, crit = +100.0°C)
Core 4:        +53.0°C  (high = +80.0°C, crit = +100.0°C)

nvme-pci-e100
Adapter: PCI adapter
Composite:    +33.9°C  (low  = -273.1°C, high = +82.8°C)
                       (crit = +84.8°C)
Sensor 1:     +33.9°C  (low  = -273.1°C, high = +65261.8°C)
"""


class TestParseSensorsOutput:
    def test_parses_cpu_package_temp(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.cpu_package_temp == 57.0

    def test_parses_gpu_edge_temp(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.gpu_edge_temp == 61.0

    def test_parses_gpu_junction_temp(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.gpu_junction_temp == 64.0

    def test_parses_gpu_mem_temp(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.gpu_mem_temp == 62.0

    def test_parses_nvme_composite_temp(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.nvme_composite_temp == 33.9

    def test_parses_gpu_power(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.gpu_power_watts == 25.0

    def test_parses_fan_rpm(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.fan_rpm == 0.0

    def test_ignores_core_temps(self):
        r = parse_sensors_output(SAMPLE_SENSORS_OUTPUT)
        assert r.cpu_package_temp == 57.0

    def test_empty_input_returns_none(self):
        r = parse_sensors_output("")
        assert r.cpu_package_temp is None
        assert r.gpu_edge_temp is None
        assert r.gpu_junction_temp is None
        assert r.gpu_mem_temp is None
        assert r.nvme_composite_temp is None
        assert r.gpu_power_watts is None
        assert r.fan_rpm is None

    def test_malformed_input_returns_none(self):
        r = parse_sensors_output("garbage input nothing to parse here")
        assert r.cpu_package_temp is None

    def test_partial_output_only_gpu(self):
        text = "edge:         +75.0°C  (crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.gpu_edge_temp == 75.0
        assert r.cpu_package_temp is None

    def test_partial_output_only_cpu(self):
        text = "Package id 0:  +45.0°C  (high = +80.0°C, crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.cpu_package_temp == 45.0
        assert r.gpu_edge_temp is None

    def test_negative_temp_not_matched(self):
        text = "edge:         -5.0°C  (crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.gpu_edge_temp is None

    def test_high_temp_values(self):
        text = "edge:         +105.0°C  (crit = +110.0°C)\n"
        r = parse_sensors_output(text)
        assert r.gpu_edge_temp == 105.0

    def test_no_fan_returns_none(self):
        text = "Package id 0:  +50.0°C  (high = +80.0°C, crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.fan_rpm is None

    def test_no_power_returns_none(self):
        text = "Package id 0:  +50.0°C  (high = +80.0°C, crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.gpu_power_watts is None


class TestSensorsWithRealFormatVariants:
    def test_format_without_hyst(self):
        text = "edge:         +60.0°C  (crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.gpu_edge_temp == 60.0

    def test_format_with_spaces_in_label(self):
        text = "Package id 0:  +50.0°C  (high = +80.0°C, crit = +100.0°C)\n"
        r = parse_sensors_output(text)
        assert r.cpu_package_temp == 50.0

    def test_multiple_fans_picks_first(self):
        text = "fan1:         1200 RPM\nfan2:         1500 RPM\n"
        r = parse_sensors_output(text)
        assert r.fan_rpm == 1200.0
