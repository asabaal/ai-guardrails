import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import signal
import sys

from brick_commissioner.config import Config, check_stop_file
from brick_commissioner.state import StateManager, BrickState
from brick_commissioner.protocol import Step, validate_transition, get_step_name, is_terminal_step
from brick_commissioner.llm_client import LLMClient
from brick_commissioner.schemas import (
    ENUMERATION_SCHEMA, IMPLEMENTATION_PLAN_SCHEMA, 
    TEST_PLAN_SCHEMA, UI_GENERATION_SCHEMA, validate_output
)
from brick_commissioner.prompts import PROMPTS
from brick_commissioner.runners import run_pytest, run_coverage, start_ui_runner


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")


class BrickOrchestrator:
    def __init__(self, config: Config, state_manager: StateManager, state: BrickState):
        self.config = config
        self.state_manager = state_manager
        self.state = state
        self.llm_client = LLMClient(config)
        self.files_changed_count = 0

    def run_brick(self, spec: Dict[str, Any]) -> None:
        try:
            self._enforce_limits()
            self._check_stop_file()
            
            self._step_1_enumerate_functions(spec)
            self._step_2_select_function()
            self._step_3_implement_function(spec)
            self._step_4_define_test_plan()
            self._step_5_implement_tests()
            self._step_6_confirm_coverage()
            self._step_7_build_ui()
            self._step_8_pause_and_report()
            
        except TimeoutError as e:
            self._halt(str(e), "timeout")
        except Exception as e:
            self._halt(str(e), "error")

    def _enforce_limits(self) -> None:
        self.state_manager.update_wall_time(self.state)
        
        if self.state.wall_time_elapsed >= self.config.limits.max_brick_wall_time:
            raise TimeoutError(
                f"Max brick wall time ({self.config.limits.max_brick_wall_time}s) exceeded. "
                f"Adjust limits.max_brick_wall_time in config."
            )
        
        if self.files_changed_count > self.config.limits.max_file_changes:
            raise TimeoutError(
                f"Max file changes ({self.config.limits.max_file_changes}) exceeded. "
                f"Adjust limits.max_file_changes in config."
            )

    def _check_stop_file(self) -> None:
        if check_stop_file(self.config):
            raise TimeoutError("STOP file detected. Halting immediately.")

    def _transition_step(self, next_step: int) -> None:
        validate_transition(self.state.current_step, next_step)
        self.state.current_step = next_step
        self.state.last_step_time = time.time()
        self.state_manager.save_state(self.state)

    def _step_1_enumerate_functions(self, spec: Dict[str, Any]) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 1: {get_step_name(1)}")
        print('='*60)
        
        self._transition_step(1)
        
        required_functions = spec.get('required_public_functions')
        if required_functions and isinstance(required_functions, list):
            self.state.enumerated_functions = required_functions
            print(f"Using provided functions from spec:")
            for func in required_functions:
                print(f"  - {func.get('name')}")
            self._transition_step(2)
            return
        
        system_prompt = PROMPTS[1]
        user_prompt = f"""
Module Specification:
Name: {spec.get('module_name')}
Description: {spec.get('module_description')}

Enumerate all functions required to implement this module.
"""
        
        response = self._call_llm_with_timeout(system_prompt, user_prompt, ENUMERATION_SCHEMA)
        
        if not response.get('is_complete'):
            self.state.blocking_questions = response.get('questions', [])
            self._halt("Blocking questions in step 1", "questions")
        
        self.state.enumerated_functions = response.get('functions', [])
        implementation_order = response.get('implementation_order', [])
        
        print(f"\nEnumerated {len(self.state.enumerated_functions)} functions:")
        for func in self.state.enumerated_functions:
            print(f"  - {func.get('name')}")
        
        print(f"\nSuggested implementation order: {implementation_order}")
        
        self.state.enumerated_functions = response.get('functions', [])
        self._transition_step(2)

    def _step_2_select_function(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 2: {get_step_name(2)}")
        print('='*60)
        
        if not self.state.enumerated_functions:
            self._halt("No functions enumerated", "error")
        
        system_prompt = PROMPTS[1]
        
        functions_list = json.dumps(self.state.enumerated_functions, indent=2)
        user_prompt = f"""
Available functions:
{functions_list}

Select the function to implement in this brick.
Return JSON with:
- implementation_order: ordered list of function names
- selected_function: the first function in the order (to implement now)
"""
        
        try:
            from brick_commissioner.schemas import ENUMERATION_SCHEMA
            response = self._call_llm_with_timeout(system_prompt, user_prompt, ENUMERATION_SCHEMA)
        except Exception:
            response = {
                "implementation_order": [f["name"] for f in self.state.enumerated_functions],
                "selected_function": self.state.enumerated_functions[0]["name"],
                "is_complete": True
            }
        
        implementation_order = response.get('implementation_order', [])
        if not implementation_order:
            implementation_order = [f["name"] for f in self.state.enumerated_functions]
        
        self.state.selected_function = implementation_order[0]
        
        print(f"\nAI-chosen implementation order: {implementation_order}")
        print(f"Selected function for this brick: {self.state.selected_function}")
        
        self._transition_step(3)

    def _step_3_implement_function(self, spec: Dict[str, Any]) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 3: {get_step_name(3)}")
        print('='*60)
        
        function_spec = None
        for func in self.state.enumerated_functions:
            if func.get('name') == self.state.selected_function:
                function_spec = func
                break
        
        system_prompt = PROMPTS[3]
        user_prompt = f"""
Function Specification:
{json.dumps(function_spec, indent=2)}

Implement this function.
"""
        
        response = self._call_llm_with_timeout(system_prompt, user_prompt, IMPLEMENTATION_PLAN_SCHEMA)
        
        if response.get('dry_run'):
            print("\n[DRY RUN: Would implement function and write files]")
            self._transition_step(4)
            return
        
        if not response.get('is_complete'):
            self.state.blocking_questions = response.get('questions', [])
            self._halt("Blocking questions in step 3", "questions")
        
        file_path = response.get('file_path')
        file_content = response.get('file_content')
        
        if file_path and file_content:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(file_content)
            self.state.files_touched.append(file_path)
            self.files_changed_count += 1
        
        print(f"\nImplemented function: {response.get('function_name')}")
        print(f"Written to: {file_path}")
        
        for file_info in response.get('files_to_create', []):
            path = file_info.get('path')
            content = file_info.get('content')
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            self.state.files_touched.append(path)
            self.files_changed_count += 1
            print(f"Additional file: {path}")
        
        self._transition_step(4)

    def _step_4_define_test_plan(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 4: {get_step_name(4)}")
        print('='*60)
        
        function_spec = None
        for func in self.state.enumerated_functions:
            if func.get('name') == self.state.selected_function:
                function_spec = func
                break
        
        system_prompt = PROMPTS[4]
        user_prompt = f"""
Function Specification:
{json.dumps(function_spec, indent=2)}

Design test cases for 100.00% statement coverage.
"""
        
        response = self._call_llm_with_timeout(system_prompt, user_prompt, TEST_PLAN_SCHEMA)
        
        if response.get('dry_run'):
            print("\n[DRY RUN: Would design test plan for 100.00% coverage]")
            self._transition_step(5)
            return
        
        if not response.get('is_complete'):
            self.state.blocking_questions = response.get('questions', [])
            self._halt("Blocking questions in step 4", "questions")
        
        test_cases = response.get('test_cases', [])
        coverage_analysis = response.get('coverage_analysis', '')
        
        print(f"\nTest plan with {len(test_cases)} test cases")
        print(f"Coverage analysis: {coverage_analysis}")
        
        self.state_manager.save_state(self.state)
        self._transition_step(5)

    def _step_5_implement_tests(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 5: {get_step_name(5)}")
        print('='*60)
        
        function_spec = None
        for func in self.state.enumerated_functions:
            if func.get('name') == self.state.selected_function:
                function_spec = func
                break
        
        test_system_prompt = """You are an expert Python testing specialist. Your task is to implement deterministic pytest tests for the specified function.

REQUIREMENTS:
1. Implement tests in a test_*.py file.
2. Tests must achieve 100.00% statement coverage.
3. Tests must be deterministic and offline.
4. Use pytest framework.

OUTPUT JSON:
{
    "test_file_path": "path/to/test_file.py",
    "test_content": "full Python test code as string",
    "is_complete": true
}

Return valid JSON only."""

        user_prompt = f"""
Function Specification:
{json.dumps(function_spec, indent=2)}

Implement tests for this function.
"""
        
        response = self._call_llm_with_timeout(test_system_prompt, user_prompt, IMPLEMENTATION_PLAN_SCHEMA)
        
        if response.get('dry_run'):
            print("\n[DRY RUN: Would implement pytest tests]")
            self._transition_step(6)
            return
        
        test_file_path = response.get('file_path') or f"tests/test_{self.state.module_name}.py"
        test_content = response.get('file_content') or response.get('implementation', '')
        
        if test_file_path:
            Path(test_file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(test_file_path, 'w') as f:
                f.write(test_content)
            self.state.files_touched.append(test_file_path)
            self.files_changed_count += 1
        
        print(f"\nTests written to: {test_file_path}")
        self.state.test_command = f"pytest {test_file_path} -v"
        
        self._transition_step(6)

    def _step_6_confirm_coverage(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 6: {get_step_name(6)}")
        print('='*60)
        
        if self.config.dry_run:
            print("\n[DRY RUN: Would run coverage and enforce 100.00%]")
            self._transition_step(7)
            return
        
        max_retries = 1
        coverage_achieved = False
        
        for attempt in range(max_retries):
            try:
                coverage_result = run_coverage(self.state.test_command)
                
                if coverage_result.get('percent_covered') >= 100.00:
                    coverage_achieved = True
                    break
                else:
                    print(f"Coverage: {coverage_result.get('percent_covered'):.2f}% (below 100.00%)")
                    if attempt < max_retries - 1:
                        self._transition_step(5)
                        self._step_5_implement_tests()
            except Exception as e:
                print(f"Coverage check failed: {e}")
                if attempt < max_retries - 1:
                    self._transition_step(5)
                    self._step_5_implement_tests()
        
        if not coverage_achieved:
            self._halt("Could not achieve 100.00% coverage. Consider adjusting tests.", "coverage")
        
        print(f"\nCoverage confirmed: 100.00%")
        self.state.coverage_command = f"coverage run -m pytest && coverage report"
        self._transition_step(7)

    def _step_7_build_ui(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 7: {get_step_name(7)}")
        print('='*60)
        
        function_spec = None
        for func in self.state.enumerated_functions:
            if func.get('name') == self.state.selected_function:
                function_spec = func
                break
        
        system_prompt = PROMPTS[7]
        user_prompt = f"""
Function Specification:
{json.dumps(function_spec, indent=2)}

Function file path: {self.state.files_touched[0] if self.state.files_touched else 'N/A'}

Create a verification UI for this function.
"""
        
        response = self._call_llm_with_timeout(system_prompt, user_prompt, UI_GENERATION_SCHEMA)
        
        if response.get('dry_run'):
            print("\n[DRY RUN: Would build verification UI]")
            self._transition_step(8)
            return
        
        if not response.get('is_complete'):
            self.state.blocking_questions = response.get('questions', [])
            self._halt("Blocking questions in step 7", "questions")
        
        html_content = response.get('html_content', '')
        ui_path = str(self.state_manager.runs_dir / f"{self.state.run_id}_ui.html")
        
        with open(ui_path, 'w') as f:
            f.write(html_content)
        
        self.state.ui_path = ui_path
        self.files_changed_count += 1
        
        runner_path = str(self.state_manager.runs_dir / f"{self.state.run_id}_runner.py")
        runner_content = self._generate_runner_script()
        with open(runner_path, 'w') as f:
            f.write(runner_content)
        
        self.state.ui_runner_path = runner_path
        self.files_changed_count += 1
        
        print(f"\nUI written to: {ui_path}")
        print(f"Runner script: {runner_path}")
        
        self._transition_step(8)

    def _step_8_pause_and_report(self) -> None:
        print(f"\n{'='*60}")
        print(f"STEP 8: {get_step_name(8)}")
        print('='*60)
        
        self.state.status = "completed"
        self.state_manager.update_wall_time(self.state)
        
        report_content = self._generate_report()
        
        report_path = str(self.state_manager.runs_dir / f"{self.state.run_id}_report.txt")
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        self.state.report_path = report_path
        self.state_manager.save_state(self.state)
        
        print("\n" + report_content)

    def _call_llm_with_timeout(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        original_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.config.limits.per_call_timeout)
        
        try:
            response = self.llm_client.call(system_prompt, user_prompt, schema)
            if not self.config.dry_run:
                validate_output(response, schema)
            self.state.llm_calls_made = self.llm_client.call_count
            self.state_manager.save_state(self.state)
            return response
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)

    def _generate_runner_script(self) -> str:
        module_file = self.state.files_touched[0] if self.state.files_touched else ""
        func_name = self.state.selected_function or "unknown_function"
        
        return f'''#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_function(request: Request):
    try:
        data = await request.json()
        inputs = data.get("inputs", {{}})
        
        module_path = "{module_file}"
        
        module = __import__(Path(module_path).stem)
        func_name = "{func_name}"
        func = getattr(module, func_name)
        
        result = func(**inputs)
        
        return JSONResponse({{
            "success": True,
            "output": result,
            "function": func_name
        }})
    except Exception as e:
        return JSONResponse({{
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }}, status_code=400)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''

    def _generate_report(self) -> str:
        report = f"""
{'='*60}
BRICK COMMISSION REPORT
{'='*60}

Module: {self.state.module_name}
Brick Function: {self.state.selected_function}
Run ID: {self.state.run_id}
Status: {self.state.status}

FUNCTION CONTRACT
------------------
{json.dumps(self.state.enumerated_functions, indent=2)}

FILES CHANGED
-------------
{chr(10).join(f"  - {f}" for f in self.state.files_touched)}

TEST COMMAND
------------
{self.state.test_command}

COVERAGE COMMAND
----------------
{self.state.coverage_command}

UI RUN COMMAND
--------------
python {self.state.ui_runner_path}

UI URL
------
http://127.0.0.1:8000

UI FILE
-------
{self.state.ui_path}

SAMPLE INPUTS TO TRY
--------------------
(See UI for sample input buttons)

RUNTIME METRICS
---------------
Wall Time: {self.state.wall_time_elapsed:.2f}s
LLM Calls: {self.state.llm_calls_made}

NEXT STEPS
----------
1. Run tests: {self.state.test_command}
2. Run UI server: python {self.state.ui_runner_path}
3. Open UI in browser: http://127.0.0.1:8000
4. Try the sample inputs
5. Verify function behavior matches expectations

{'='*60}
"""
        return report

    def _halt(self, reason: str, halt_type: str) -> None:
        self.state.status = "halted"
        self.state_manager.update_wall_time(self.state)
        
        report_content = f"""
{'='*60}
BRICK COMMISSION HALTED - {halt_type.upper()}
{'='*60}

Reason: {reason}
Module: {self.state.module_name}
Current Step: {self.state.current_step} - {get_step_name(self.state.current_step)}
Wall Time Elapsed: {self.state.wall_time_elapsed:.2f}s
LLM Calls Made: {self.state.llm_calls_made}

BLOCKING QUESTIONS
------------------
{chr(10).join(f"  - {q}" for q in self.state.blocking_questions) if self.state.blocking_questions else "  None"}

FILES TOUCHED
-------------
{chr(10).join(f"  - {f}" for f in self.state.files_touched) if self.state.files_touched else "  None"}

WHAT TO ADJUST
--------------
- If timeout: increase limits.per_call_timeout or limits.max_brick_wall_time
- If max calls: increase limits.max_calls_per_brick
- If max files: increase limits.max_file_changes
- If questions: clarify the specification and retry
- If coverage: review test coverage requirements

Current Limits:
- Per call timeout: {self.config.limits.per_call_timeout}s
- Max calls per brick: {self.config.limits.max_calls_per_brick}
- Max brick wall time: {self.config.limits.max_brick_wall_time}s
- Max file changes: {self.config.limits.max_file_changes}

{'='*60}
"""
        
        report_path = str(self.state_manager.runs_dir / f"{self.state.run_id}_halted_report.txt")
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        self.state.report_path = report_path
        self.state_manager.save_state(self.state)
        
        print("\n" + report_content)
        raise TimeoutError(f"Brick halted: {reason}")
