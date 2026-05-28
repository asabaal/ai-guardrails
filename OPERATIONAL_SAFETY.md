# AI Watchdog - Operational Safety Utility

## What It Does

The AI watchdog is a reusable command-line utility that wraps long-running local AI workloads and monitors system health to prevent overheating, excessive memory pressure, or machine instability.

It reads hardware sensor data from `sensors` (lm-sensors), tracks RAM and swap usage, and intervenes when configurable thresholds are exceeded:

- **Warning**: Logs an alert, continues running
- **Pause**: Sends SIGSTOP to the entire process group, waits for a cooldown period, then resumes with SIGCONT
- **Kill**: Sends SIGTERM, waits a grace period, then SIGKILL if the process hasn't exited

## When Agents Must Use It

For any long-running local AI workload involving vision, image transcription, model inference, batch generation, video rendering, audio processing, embeddings, local LLMs, VLMs, or GPU acceleration, **do not run the command directly**. Run it through the AI watchdog.

Required form:

```
ai-watchdog run -- <command>
```

## Installation

### Editable install (recommended)

```bash
cd /path/to/ai-guardrails
pip install -e .
```

This makes `ai-watchdog` available as a command anywhere on the system.

### Without install

Use the module directly:

```bash
python -m ai_guardrails.operational_safety.ai_watchdog run -- <command>
```

Or use the shell wrapper:

```bash
/path/to/ai-guardrails/scripts/ai-watchdog-run <command>
```

### Symlink for other repos

```bash
ln -s /path/to/ai-guardrails/scripts/ai-watchdog-run /usr/local/bin/ai-watchdog-run
```

## Usage

### Basic usage

```bash
ai-watchdog run -- python transcribe_images.py
ai-watchdog run -- python -m my_batch_inference
ai-watchdog run -- ./render_video.sh
```

### With custom config

```bash
ai-watchdog run --config ./my_watchdog.yaml -- python heavy_job.py
```

### With CLI overrides

```bash
ai-watchdog run --log-dir ./logs --poll-interval 2 -- python job.py
```

### Show current sensor readings

```bash
ai-watchdog show-sensors
```

### Dump default config

```bash
ai-watchdog dump-config
```

## Monitored Signals

| Signal | Source | Notes |
|--------|--------|-------|
| CPU package temperature | `sensors` (coretemp) | Package id 0 |
| AMD GPU edge temperature | `sensors` (amdgpu) | |
| AMD GPU junction temperature | `sensors` (amdgpu) | |
| AMD GPU memory temperature | `sensors` (amdgpu) | |
| NVMe composite temperature | `sensors` (nvme-pci) | |
| GPU power draw | `sensors` (PPT) | AMD |
| Fan RPM | `sensors` (fan1) | |
| RAM usage | `/proc/meminfo` | |
| Swap usage | `/proc/meminfo` | |
| Process CPU and memory | `/proc/<pid>/stat` | Child process |

## Default Thresholds

| Signal | Warning | Pause | Kill |
|--------|---------|-------|------|
| CPU package | 80 C | 88 C | 95 C |
| GPU edge | 82 C | 88 C | 95 C |
| GPU junction | 95 C | 102 C | 108 C |
| GPU memory | 82 C | 88 C | 95 C |
| NVMe | 70 C | 78 C | 82 C |
| RAM | 85% | 95% | 95% |
| Swap | 50% | 85% | 85% |

## Configuration

Create a YAML config file to override defaults:

```yaml
cpu_temp:
  warning: 75.0
  pause: 85.0
  kill: 92.0

gpu_edge_temp:
  warning: 78.0
  pause: 85.0
  kill: 92.0

poll_interval: 3.0
cooldown_seconds: 20.0
grace_period: 8.0
log_dir: ./watchdog_logs
```

Use it with `--config`:

```bash
ai-watchdog run --config ./my_config.yaml -- python job.py
```

## Logs

Logs are written as JSON-lines files to the configured log directory (default: `./watchdog_logs/`).

File naming: `<timestamp>_<command_slug>.jsonl`

Each line is a JSON object:

```json
{
  "ts": "2026-05-28T10:30:00+00:00",
  "elapsed_s": 15.2,
  "action": "none",
  "reason": "",
  "readings": {
    "cpu_package_temp": 57.0,
    "gpu_edge_temp": 61.0,
    "ram_percent": 45.2
  }
}
```

Actions logged: `none`, `warning`, `pause`, `kill`, `summary`

The final line is always a `summary` entry with exit code and intervention count.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Child exited successfully |
| N | Child exited with code N (forwarded) |
| 137 | Child was killed by watchdog (SIGKILL after grace period) |

## How Interventions Work

1. **Warning**: A yellow message is printed. The process continues. The warning is logged.
2. **Pause**: SIGSTOP is sent to the process group (includes all child subprocesses). The watchdog waits for the configured cooldown period (default 30s), then sends SIGCONT to resume.
3. **Kill**: SIGTERM is sent to the process group. If the process hasn't exited after the grace period (default 10s), SIGKILL is sent.

Kill always takes priority over pause, which takes priority over warning.

## Architecture

```
ai_guardrails/operational_safety/
  __init__.py          # Package entry
  ai_watchdog.py       # CLI + main watchdog loop
  sensors_parser.py    # Parse `sensors` output + /proc/meminfo
  config.py            # Threshold dataclasses + YAML loading
  process_control.py   # Child process group lifecycle
  logging_utils.py     # Structured JSONL logging + terminal display
  configs/
    ai_watchdog.default.yaml
scripts/
  ai-watchdog-run      # Shell wrapper
tests/operational_safety/
  test_sensors_parser.py
  test_threshold_decisions.py
  test_smoke.py
```

## Dependencies

- Python 3.10+
- PyYAML
- Linux with `sensors` (lm-sensors) installed for temperature readings
- No GPU vendor lock-in: supports AMD GPU readings, NVMe, and any sensors output
