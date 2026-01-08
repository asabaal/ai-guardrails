import subprocess
import json
from typing import Dict, Any
from pathlib import Path


def run_pytest(command: str) -> Dict[str, Any]:
    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True
    )
    
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }


def run_coverage(command: str) -> Dict[str, Any]:
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True
        )
        
        coverage_output = result.stdout + result.stderr
        
        return {
            "success": result.returncode == 0,
            "stdout": coverage_output,
            "percent_covered": _parse_coverage_percent(coverage_output),
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "percent_covered": 0.0
        }


def _parse_coverage_percent(output: str) -> float:
    for line in output.split('\n'):
        if 'TOTAL' in line:
            parts = line.split()
            for part in parts:
                try:
                    percent = float(part.replace('%', ''))
                    return percent
                except ValueError:
                    continue
    return 0.0


def start_ui_runner(runner_path: str) -> None:
    import subprocess
    subprocess.run(["python", runner_path])


def check_coverage_file() -> bool:
    return Path(".coverage").exists()
