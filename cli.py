import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import IntPrompt, Confirm, Prompt
from generator_core import DEFAULTS, run_generation

console = Console()
console.rule("[bold green]Clever Demo District Generator (CLI)[/bold green]")

config = DEFAULTS.copy()

if not Confirm.ask("Apply ALL default settings?", default=False):
    config["ID_MODE"] = Prompt.ask("Select ID Mode", choices=["sequential", "alphanumeric"], default=DEFAULTS["ID_MODE"])
    config["OUTPUT_SCHEMA"] = Prompt.ask("Output Schema", choices=["standard", "anyschool", "both"], default="standard")
    config["NUM_DISTRICTS"] = IntPrompt.ask("Districts", default=DEFAULTS["NUM_DISTRICTS"])
    config["SCHOOLS_PER_DISTRICT"] = IntPrompt.ask("Schools per District", default=DEFAULTS["SCHOOLS_PER_DISTRICT"])
    
    console.print("\n[bold cyan]-- Ranges & Ratios --[/bold cyan]")
    config["TEACHERS_PER_SCHOOL"] = Prompt.ask("Teachers per School (e.g. '15-40')", default=str(DEFAULTS["TEACHERS_PER_SCHOOL"]))
    config["STUDENTS_PER_SECTION"] = Prompt.ask("Students per Section (e.g. '15-30')", default=str(DEFAULTS["STUDENTS_PER_SECTION"]))
    config["SECTIONS_PER_TEACHER_TERM"] = IntPrompt.ask("Sections per Teacher (per Term)", default=DEFAULTS["SECTIONS_PER_TEACHER_TERM"])
    
    config["SCHOOL_START_YEAR"] = Prompt.ask("School Start Year (YYYY)", default=DEFAULTS["SCHOOL_START_YEAR"])
    config["NUM_TERMS"] = IntPrompt.ask("Terms per Year", choices=["2", "3", "4"], default=DEFAULTS["NUM_TERMS"])
    config["INCLUDE_SUMMER"] = Confirm.ask("Include Summer Session?", default=DEFAULTS["INCLUDE_SUMMER"])
    
    console.print("\n[bold yellow]-- Demographics --[/bold yellow]")
    if Confirm.ask("Use default demographic probabilities?", default=True):
        pass # Defaults are already stored in the config dictionary!
    else:
        from rich.prompt import FloatPrompt
        config["PROB_FRL"] = FloatPrompt.ask("Prob. FRL", default=DEFAULTS["PROB_FRL"])
        config["PROB_IEP"] = FloatPrompt.ask("Prob. IEP", default=DEFAULTS["PROB_IEP"])
        config["PROB_ELL"] = FloatPrompt.ask("Prob. ELL", default=DEFAULTS["PROB_ELL"])
        config["PROB_504"] = FloatPrompt.ask("Prob. 504", default=DEFAULTS["PROB_504"])
        config["PROB_GIFTED"] = FloatPrompt.ask("Prob. Gifted", default=DEFAULTS["PROB_GIFTED"])
        config["PROB_DISABILITY"] = FloatPrompt.ask("Prob. Disability", default=DEFAULTS["PROB_DISABILITY"])

if not Confirm.ask("Ready to generate?", default=True): exit()

base_output_dir = 'district_data_output'

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
    main_task = progress.add_task("[green]Initializing...", total=config["NUM_DISTRICTS"])
    
    # Define how the core updates Rich's CLI UI
    def update_status(msg): progress.update(main_task, description=f"[green]{msg}[/green]")
    def update_progress(val): progress.update(main_task, completed=val * config["NUM_DISTRICTS"])

    # Trigger the Brain
    run_generation(config, base_output_dir, status_callback=update_status, progress_callback=update_progress)

console.print("\n[bold blue]Generation Complete! Check the 'district_data_output' folder.[/bold blue]")