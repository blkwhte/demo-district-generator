import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import IntPrompt, Confirm, Prompt
from rich.table import Table
from generator_core import DEFAULTS, EDGE_CASE_REGISTRY, STATIC_CASES, THREE_DAY_CASES, run_generation

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
        pass
    else:
        from rich.prompt import FloatPrompt
        config["PROB_FRL"] = FloatPrompt.ask("Prob. FRL", default=DEFAULTS["PROB_FRL"])
        config["PROB_IEP"] = FloatPrompt.ask("Prob. IEP", default=DEFAULTS["PROB_IEP"])
        config["PROB_HISPANIC"] = FloatPrompt.ask("Prob. Hispanic/Latino (also drives Spanish home language and ELL)", default=DEFAULTS["PROB_HISPANIC"])
        config["PROB_504"] = FloatPrompt.ask("Prob. 504", default=DEFAULTS["PROB_504"])
        config["PROB_GIFTED"] = FloatPrompt.ask("Prob. Gifted", default=DEFAULTS["PROB_GIFTED"])
        config["PROB_DISABILITY"] = FloatPrompt.ask("Prob. Disability", default=DEFAULTS["PROB_DISABILITY"])

# --- EDGE CASE SELECTION ---
console.print("\n[bold magenta]-- Edge Cases --[/bold magenta]")
selected_edge_cases = []

if Confirm.ask("Include any edge case scenarios?", default=False):
    # Show static scenarios
    console.print("\n[bold]📋 Static Scenarios[/bold] [dim](work in a single-day dataset)[/dim]")
    static_table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    static_table.add_column("Sc #", style="dim", width=5)
    static_table.add_column("Label", width=38)
    static_table.add_column("Description")
    for ec in STATIC_CASES:
        static_table.add_row(str(ec["number"]), ec["label"], ec["description"])
    console.print(static_table)

    if Confirm.ask("Select ALL static scenarios?", default=False):
        selected_edge_cases.extend([ec["key"] for ec in STATIC_CASES])
        console.print(f"[green]✓ All {len(STATIC_CASES)} static scenarios selected.[/green]")
    else:
        console.print("[dim]Enter scenario numbers to include, separated by commas (e.g. 1,4,10). Leave blank to skip.[/dim]")
        raw = Prompt.ask("Static scenarios", default="").strip()
        if raw:
            chosen_nums = {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}
            for ec in STATIC_CASES:
                if ec["number"] in chosen_nums:
                    selected_edge_cases.append(ec["key"])
                    console.print(f"  [green]✓[/green] Sc {ec['number']}: {ec['label']}")

    # Show 3-day scenarios
    console.print("\n[bold]🔄 3-Day Rotation Scenarios[/bold] [dim](require Day 1/2/3 output structure)[/dim]")
    day3_table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    day3_table.add_column("Sc #", style="dim", width=5)
    day3_table.add_column("Label", width=38)
    day3_table.add_column("Description")
    for ec in THREE_DAY_CASES:
        day3_table.add_row(str(ec["number"]), ec["label"], ec["description"])
    console.print(day3_table)

    if Confirm.ask("Select ALL 3-day scenarios?", default=False):
        selected_edge_cases.extend([ec["key"] for ec in THREE_DAY_CASES])
        console.print(f"[green]✓ All {len(THREE_DAY_CASES)} 3-day scenarios selected.[/green]")
    else:
        console.print("[dim]Enter scenario numbers to include, separated by commas. Leave blank to skip.[/dim]")
        raw = Prompt.ask("3-day scenarios", default="").strip()
        if raw:
            chosen_nums = {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}
            for ec in THREE_DAY_CASES:
                if ec["number"] in chosen_nums:
                    selected_edge_cases.append(ec["key"])
                    console.print(f"  [green]✓[/green] Sc {ec['number']}: {ec['label']}")

config["EDGE_CASES"] = selected_edge_cases

if selected_edge_cases:
    needs_3day = any(ec["key"] in selected_edge_cases for ec in THREE_DAY_CASES)
    console.print(f"\n[bold green]{len(selected_edge_cases)} edge case(s) selected.[/bold green]" +
                  (" [yellow]3-day output will be generated.[/yellow]" if needs_3day else ""))
else:
    console.print("\n[dim]No edge cases selected — a clean dataset will be generated.[/dim]")

console.print("\n[bold cyan]-- Optional Data Files --[/bold cyan]")
config["DO_ATTENDANCE"] = Confirm.ask("Generate Attendance Data?", default=DEFAULTS.get("DO_ATTENDANCE", False))
config["DO_RESOURCES"] = Confirm.ask(
    "Generate Resources Data? (1-3 synthetic resources per course for content mapping)",
    default=DEFAULTS.get("DO_RESOURCES", False)
)

if not Confirm.ask("\nReady to generate?", default=True):
    exit()

base_output_dir = 'district_data_output'

with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
    main_task = progress.add_task("[green]Initializing...", total=config["NUM_DISTRICTS"])

    def update_status(msg): progress.update(main_task, description=f"[green]{msg}[/green]")
    def update_progress(val): progress.update(main_task, completed=val * config["NUM_DISTRICTS"])

    run_generation(config, base_output_dir, status_callback=update_status, progress_callback=update_progress)

console.print("\n[bold blue]Generation Complete! Check the 'district_data_output' folder.[/bold blue]")