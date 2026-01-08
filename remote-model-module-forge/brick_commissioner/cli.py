import click
import json
from pathlib import Path
from brick_commissioner.config import get_config
from brick_commissioner.state import StateManager
from brick_commissioner.orchestrator import BrickOrchestrator
from brick_commissioner.llm_client import LLMClient
from brick_commissioner.schemas import SPEC_GENERATION_SCHEMA, validate_output
from brick_commissioner.prompts import PROMPTS


@click.group()
def cli():
    pass


@cli.command()
@click.argument('description', nargs=-1)
@click.option('--output-spec', '-s', default=None, help='Save generated spec to this file')
@click.option('--dry-run', is_flag=True, help='Show pipeline steps without executing')
def build(description, output_spec, dry_run):
    """Run entire pipeline from description to finished code.
    
    DESCRIPTION can be:
    - Free-form text (e.g., "A function that adds two numbers")
    - A file path containing description (e.g., description.txt)
    
    This command:
    1. Generates a module specification from your description
    2. Commissions a brick (implements ONE function)
    3. Shows generated code and test results
    
    Example:
        brick build "A function that calculates area of a circle"
        brick build --output-spec my_spec.json "Calculate area of circle"
    """
    config = get_config()
    
    if not description:
        click.echo("Error: Description is required")
        return
    
    description_text = ' '.join(description)
    
    if Path(description_text).exists():
        description_text = Path(description_text).read_text()
    
    click.echo(f"\n{'='*70}")
    click.echo("STEP 0: Generating Module Specification")
    click.echo('='*70)
    
    client = LLMClient(config)
    system_prompt = PROMPTS[0]
    user_prompt = f"""
Human Description:
{description_text}

Create a module specification for this module.
"""
    
    try:
        spec_response = client.call(system_prompt, user_prompt, SPEC_GENERATION_SCHEMA)
        
        if not spec_response.get('is_complete'):
            questions = spec_response.get('questions', [])
            if questions:
                click.echo("⚠️  The AI has some questions before proceeding:")
                for q in questions:
                    click.echo(f"  - {q}")
                click.echo("\nPlease clarify and try again.")
                return
        
        spec = {
            'module_name': spec_response.get('module_name'),
            'module_description': spec_response.get('module_description'),
            'required_public_functions': spec_response.get('required_public_functions', [])
        }
        
        if output_spec:
            spec_path = output_spec
        else:
            spec_path = f"{spec['module_name']}_spec.json"
        
        if not dry_run:
            with open(spec_path, 'w') as f:
                json.dump(spec, f, indent=2)
            
            click.echo(f"✅ Specification saved to: {spec_path}")
            click.echo(f"\nModule: {spec['module_name']}")
            click.echo(f"Functions: {[f['name'] for f in spec['required_public_functions']]}")
        else:
            click.echo(f"[DRY RUN] Would save spec to: {spec_path}")
            click.echo(f"  Module: {spec['module_name']}")
            click.echo(f"  Functions: {[f['name'] for f in spec['required_public_functions']]}")
        
        if not dry_run:
            click.echo(f"\n{'='*70}")
            click.echo("STEP 1: Running Brick Commission")
            click.echo('='*70)
            
            state_manager = StateManager(config.runs_dir)
            state = state_manager.create_state(spec['module_name'], spec_path)
            orchestrator = BrickOrchestrator(config, state_manager, state)
            
            orchestrator.run_brick(spec)
            
            if state.report_path and Path(state.report_path).exists():
                click.echo(f"\n{'='*70}")
                click.echo("FINAL SUMMARY")
                click.echo('='*70)
                click.echo(Path(state.report_path).read_text())
                
                if state.files_touched:
                    for file_path in state.files_touched:
                        if Path(file_path).exists():
                            if file_path.endswith('.py') and 'test_' not in file_path:
                                click.echo(f"\n📄 Generated Code ({file_path}):")
                                click.echo('-' * 70)
                                click.echo(Path(file_path).read_text())
            
    except Exception as e:
        click.echo(f"❌ Pipeline error: {e}")
        if config.dry_run:
            click.echo("\nTry: DRY_RUN=true brick build <description>")


@cli.command()
@click.argument('spec_path')
def run(spec_path):
    """Commission a brick from a module specification file."""
    config = get_config()
    state_manager = StateManager(config.runs_dir)
    
    spec = json.loads(Path(spec_path).read_text())
    module_name = spec.get('module_name')
    
    state = state_manager.create_state(module_name, spec_path)
    orchestrator = BrickOrchestrator(config, state_manager, state)
    
    try:
        orchestrator.run_brick(spec)
    except Exception as e:
        click.echo(f"Error: {e}")
        state_manager.save_state(state)


@cli.command()
@click.argument('run_id')
def status(run_id):
    """Check the status of a brick run."""
    config = get_config()
    state_manager = StateManager(config.runs_dir)
    state = state_manager.load_state(run_id)
    
    if not state:
        click.echo(f"Run {run_id} not found")
        return
    
    click.echo(json.dumps(state.model_dump(), indent=2))


@cli.command()
@click.argument('run_id')
def report(run_id):
    """View the full report for a completed brick."""
    config = get_config()
    state_manager = StateManager(config.runs_dir)
    state = state_manager.load_state(run_id)
    
    if not state:
        click.echo(f"Run {run_id} not found")
        return
    
    if state.report_path and Path(state.report_path).exists():
        click.echo(Path(state.report_path).read_text())
    else:
        click.echo(f"No report found for run {run_id}")


@cli.command()
@click.argument('run_id')
def ui(run_id):
    """Open the verification UI for a brick."""
    config = get_config()
    state_manager = StateManager(config.runs_dir)
    state = state_manager.load_state(run_id)
    
    if not state:
        click.echo(f"Run {run_id} not found")
        return
    
    if state.ui_path and Path(state.ui_path).exists():
        from brick_commissioner.runners import start_ui_runner
        click.echo(f"Opening UI at {state.ui_path}")
        click.echo(f"Or run: python {state.ui_runner_path} to start the local server")
    else:
        click.echo(f"No UI found for run {run_id}")


if __name__ == "__main__":
    cli()
