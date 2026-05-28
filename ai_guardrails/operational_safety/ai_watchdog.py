from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from dataclasses import asdict
from enum import Enum
from typing import Optional

from .config import WatchdogConfig, load_config
from .logging_utils import (
    WatchdogLogger,
    print_intervention,
    print_status,
    print_summary,
    print_warning,
)
from .process_control import ChildProcess
from .sensors_parser import SensorReadings, enrich_with_process_stats, read_sensors_live


class Action(Enum):
    NONE = "none"
    WARNING = "warning"
    PAUSE = "pause"
    KILL = "kill"


def evaluate_readings(readings: SensorReadings, cfg: WatchdogConfig) -> tuple[Action, list[str]]:
    reasons: list[str] = []
    kill = False
    pause = False
    warn = False

    checks: list[tuple[Optional[float], object, str]] = [
        (readings.cpu_package_temp, cfg.cpu_temp, "CPU package"),
        (readings.gpu_edge_temp, cfg.gpu_edge_temp, "GPU edge"),
        (readings.gpu_junction_temp, cfg.gpu_junction_temp, "GPU junction"),
        (readings.gpu_mem_temp, cfg.gpu_mem_temp, "GPU memory"),
        (readings.nvme_composite_temp, cfg.nvme_temp, "NVMe"),
    ]

    for value, thresholds, label in checks:
        if value is None:
            continue
        if value >= thresholds.kill:
            reasons.append(f"{label} temp {value:.1f}C >= kill threshold {thresholds.kill}C")
            kill = True
        elif value >= thresholds.pause:
            reasons.append(f"{label} temp {value:.1f}C >= pause threshold {thresholds.pause}C")
            pause = True
        elif value >= thresholds.warning:
            reasons.append(f"{label} temp {value:.1f}C >= warning threshold {thresholds.warning}C")
            warn = True

    for value, thresholds, label in [
        (readings.ram_percent, cfg.ram_percent, "RAM"),
        (readings.swap_percent, cfg.swap_percent, "Swap"),
    ]:
        if value is None:
            continue
        if value >= thresholds.kill:
            reasons.append(f"{label} usage {value:.1f}% >= kill threshold {thresholds.kill}%")
            kill = True
        elif value >= thresholds.pause:
            pause = True
            reasons.append(f"{label} usage {value:.1f}% >= pause threshold {thresholds.pause}%")
        if value >= thresholds.warning:
            reasons.append(f"{label} usage {value:.1f}% >= warning threshold {thresholds.warning}%")
            warn = True

    if kill:
        return Action.KILL, reasons
    if pause:
        return Action.PAUSE, reasons
    if warn:
        return Action.WARNING, reasons
    return Action.NONE, []


def run_watchdog(command: list[str], cfg: WatchdogConfig) -> int:
    logger = WatchdogLogger(cfg.log_dir, command)
    child = ChildProcess(command)
    child.start()

    def _forward_signal(signum: int, frame) -> None:
        if child.pgid is not None:
            try:
                os.killpg(child.pgid, signum)
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGTERM, _forward_signal)
    signal.signal(signal.SIGINT, _forward_signal)

    exit_code: Optional[int] = None
    killed = False
    paused = False
    intervention_count = 0

    try:
        while child.running:
            readings = read_sensors_live()
            if child.pid:
                enrich_with_process_stats(readings, child.pid)

            action, reasons = evaluate_readings(readings, cfg)
            reason_text = "; ".join(reasons)

            elapsed = time.monotonic() - logger.start_time

            if action == Action.KILL:
                status_label = "KILLED"
                logger.log_poll(readings, "kill", reason_text)
                print_intervention(f"Killing process: {reason_text}")
                exit_code = child.terminate_with_grace(cfg.grace_period)
                killed = True
                intervention_count += 1
                break

            elif action == Action.PAUSE:
                status_label = "PAUSED"
                if not paused:
                    child.pause()
                    paused = True
                    intervention_count += 1
                    print_intervention(f"Pausing process: {reason_text}")
                logger.log_poll(readings, "pause", reason_text)

                print_status(readings, elapsed, status_label, cfg)
                time.sleep(cfg.cooldown_seconds)
                child.resume()
                paused = False
                print_warning(f"Resuming process after cooldown ({cfg.cooldown_seconds}s)")
                continue

            elif action == Action.WARNING:
                status_label = "WARNING"
                if reasons:
                    print_warning(reason_text)
                logger.log_poll(readings, "warning", reason_text)
                intervention_count += 1

            else:
                status_label = "RUNNING"
                logger.log_poll(readings, "none", "")

            print_status(readings, elapsed, status_label, cfg)
            time.sleep(cfg.poll_interval)

    except KeyboardInterrupt:
        print_intervention("KeyboardInterrupt received, terminating child")
        child.terminate_with_grace(cfg.grace_period)
        exit_code = child.exit_code
        killed = True

    if not killed and child.running:
        child.wait()
    if exit_code is None:
        exit_code = child.exit_code if child.exit_code is not None else -1

    elapsed = time.monotonic() - logger.start_time
    summary_reason = "watchdog kill" if killed else ("keyboard interrupt" if killed else "normal exit")
    logger.log_summary(exit_code, summary_reason)
    print_summary(elapsed, exit_code, intervention_count, logger.log_path_str)
    logger.close()

    return exit_code


def show_sensors(cfg: WatchdogConfig) -> None:
    readings = read_sensors_live()
    action, reasons = evaluate_readings(readings, cfg)
    elapsed = 0.0
    print_status(readings, elapsed, action.value.upper(), cfg)
    sys.stderr.write("\n")
    if reasons:
        for r in reasons:
            sys.stderr.write(f"  {r}\n")
    sys.stderr.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-watchdog",
        description="AI Workload Watchdog - monitor and protect long running AI jobs",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a command under watchdog monitoring")
    run_parser.add_argument("--config", "-c", default=None, help="Path to YAML config file")
    run_parser.add_argument("--log-dir", default=None, help="Directory for log files (overrides config)")
    run_parser.add_argument("--poll-interval", type=float, default=None, help="Poll interval in seconds")
    run_parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run (use -- before command)")

    show_parser = subparsers.add_parser("show-sensors", help="Show current sensor readings and exit")
    show_parser.add_argument("--config", "-c", default=None, help="Path to YAML config file")

    subparsers.add_parser("dump-config", help="Print default config as YAML")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "dump-config":
        from .config import default_config_as_dict
        import yaml
        print(yaml.dump(default_config_as_dict(), default_flow_style=False, sort_keys=False))
        return 0

    cfg = load_config(args.config)

    if args.command == "show-sensors":
        show_sensors(cfg)
        return 0

    if args.command == "run":
        cmd = args.cmd
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        if not cmd:
            parser.error("No command specified. Usage: ai-watchdog run -- <command>")
            return 1

        if args.log_dir is not None:
            cfg.log_dir = args.log_dir
        if args.poll_interval is not None:
            cfg.poll_interval = args.poll_interval

        return run_watchdog(cmd, cfg)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
