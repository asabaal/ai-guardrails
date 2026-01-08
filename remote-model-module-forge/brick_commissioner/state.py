import json
import hashlib
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BrickState(BaseModel):
    run_id: str = Field(description="Unique run identifier")
    module_name: str = Field(description="Module being implemented")
    module_spec_path: Optional[str] = Field(default=None, description="Path to module spec file")
    module_spec_hash: Optional[str] = Field(default=None, description="Hash of spec content")
    enumerated_functions: List[Dict[str, Any]] = Field(default_factory=list, description="All functions required")
    selected_function: Optional[str] = Field(default=None, description="Current brick function name")
    files_touched: List[str] = Field(default_factory=list, description="Files modified/created")
    test_command: str = Field(default="pytest", description="Command to run tests")
    coverage_command: str = Field(default="coverage run -m pytest && coverage report", description="Command to run coverage")
    ui_path: Optional[str] = Field(default=None, description="Path to UI HTML file")
    ui_runner_path: Optional[str] = Field(default=None, description="Path to UI runner script")
    current_step: int = Field(default=0, description="Current protocol step (0-8)")
    blocking_questions: List[str] = Field(default_factory=list, description="Blocking questions")
    report_path: Optional[str] = Field(default=None, description="Path to generated report")
    start_time: float = Field(default_factory=time.time, description="Start timestamp")
    last_step_time: float = Field(default_factory=time.time, description="Last step completion time")
    llm_calls_made: int = Field(default=0, description="Count of LLM calls made")
    wall_time_elapsed: float = Field(default=0.0, description="Wall time elapsed in seconds")
    diff_summary: List[Dict[str, Any]] = Field(default_factory=list, description="Diff summaries")
    status: str = Field(default="in_progress", description="Run status: in_progress, paused, completed, failed, halted")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class StateManager:
    def __init__(self, runs_dir: str = "runs"):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

    def generate_run_id(self, module_name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{module_name}_{timestamp}"

    def create_state(self, module_name: str, module_spec_path: Optional[str] = None) -> BrickState:
        run_id = self.generate_run_id(module_name)
        
        spec_hash = None
        if module_spec_path and Path(module_spec_path).exists():
            with open(module_spec_path, "r") as f:
                spec_hash = hashlib.sha256(f.read().encode()).hexdigest()

        state = BrickState(
            run_id=run_id,
            module_name=module_name,
            module_spec_path=module_spec_path,
            module_spec_hash=spec_hash,
            current_step=0,
            status="in_progress"
        )
        self.save_state(state)
        return state

    def save_state(self, state: BrickState) -> None:
        state_file = self.runs_dir / f"{state.run_id}.json"
        with open(state_file, "w") as f:
            json.dump(state.model_dump(), f, indent=2)

    def load_state(self, run_id: str) -> Optional[BrickState]:
        state_file = self.runs_dir / f"{run_id}.json"
        if not state_file.exists():
            return None
        with open(state_file, "r") as f:
            return BrickState(**json.load(f))

    def update_wall_time(self, state: BrickState) -> None:
        state.wall_time_elapsed = time.time() - state.start_time

    def list_runs(self) -> List[str]:
        return sorted([f.stem for f in self.runs_dir.glob("*.json")])
