from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass


class Step(Enum):
    INITIAL = 0
    ENUMERATE_FUNCTIONS = 1
    SELECT_FUNCTION = 2
    IMPLEMENT_FUNCTION = 3
    DEFINE_TEST_PLAN = 4
    IMPLEMENT_TESTS = 5
    CONFIRM_COVERAGE = 6
    BUILD_UI = 7
    PAUSE_REPORT = 8


class TransitionError(Exception):
    pass


@dataclass
class StepInfo:
    step: Step
    name: str
    description: str
    allowed_next: List[Step]


STEPS = {
    Step.INITIAL: StepInfo(
        Step.INITIAL,
        "Initial",
        "Starting point of protocol",
        [Step.ENUMERATE_FUNCTIONS]
    ),
    Step.ENUMERATE_FUNCTIONS: StepInfo(
        Step.ENUMERATE_FUNCTIONS,
        "Enumerate Required Functions",
        "Identify every function required to implement the module",
        [Step.SELECT_FUNCTION]
    ),
    Step.SELECT_FUNCTION: StepInfo(
        Step.SELECT_FUNCTION,
        "Select One Function",
        "Choose exactly one function as the current brick",
        [Step.IMPLEMENT_FUNCTION]
    ),
    Step.IMPLEMENT_FUNCTION: StepInfo(
        Step.IMPLEMENT_FUNCTION,
        "Implement the Function",
        "Implement the function with a clear contract",
        [Step.DEFINE_TEST_PLAN]
    ),
    Step.DEFINE_TEST_PLAN: StepInfo(
        Step.DEFINE_TEST_PLAN,
        "Define Test Coverage",
        "Design test plan achieving 100.00% statement coverage",
        [Step.IMPLEMENT_TESTS]
    ),
    Step.IMPLEMENT_TESTS: StepInfo(
        Step.IMPLEMENT_TESTS,
        "Implement Tests",
        "Implement deterministic offline tests",
        [Step.CONFIRM_COVERAGE]
    ),
    Step.CONFIRM_COVERAGE: StepInfo(
        Step.CONFIRM_COVERAGE,
        "Confirm Coverage",
        "Run tests and confirm 100.00% statement coverage",
        [Step.BUILD_UI, Step.IMPLEMENT_TESTS]
    ),
    Step.BUILD_UI: StepInfo(
        Step.BUILD_UI,
        "Build Verification UI",
        "Create minimal local HTML UI for interactive verification",
        [Step.PAUSE_REPORT]
    ),
    Step.PAUSE_REPORT: StepInfo(
        Step.PAUSE_REPORT,
        "Pause and Report",
        "Stop work and report back",
        []
    ),
}


def validate_transition(current_step: int, next_step: int) -> bool:
    current = Step(current_step)
    next_s = Step(next_step)
    
    current_info = STEPS.get(current)
    if not current_info:
        raise TransitionError(f"Invalid current step: {current_step}")
    
    if next_s not in current_info.allowed_next:
        raise TransitionError(
            f"Cannot transition from step {current_info.name} ({current_step}) "
            f"to step {next_step}"
        )
    
    return True


def get_step_info(step: int) -> Optional[StepInfo]:
    return STEPS.get(Step(step))


def get_step_name(step: int) -> str:
    info = get_step_info(step)
    return info.name if info else "Unknown"


def is_terminal_step(step: int) -> bool:
    return step == Step.PAUSE_REPORT.value
