import argparse
import os

from config import get_api_key, load_api_key, reset_api_key
from display import (
    console,
    print_banner,
    print_info_box,
    print_success,
    print_warning,
)
from gemini import generate_readme
from interview import run_interview
from writer import write_readme


def main():
    parser = argparse.ArgumentParser(
        prog="ichiran", description="AI-powered README generator"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset your saved Gemini API key"
    )
    parser.add_argument(
        "--version", action="store_true", help="Show the current version"
    )
    args = parser.parse_args()

    if args.reset:
        reset_api_key()
        return

    if args.version:
        try:
            from importlib.metadata import PackageNotFoundError, version
            console.print(f"[bold cyan]ichiran[/bold cyan] [white]v{version('ichiran')}[/white]")
        except PackageNotFoundError:
            console.print("[bold cyan]ichiran[/bold cyan] [white]v0.1.0[/white]")
        return

    # print banner — box 1
    print_banner()

    # print info box — box 2
    existing_key = load_api_key()
    print_info_box(cwd=os.getcwd(), api_key_loaded=bool(existing_key))

    # ensure API key is available (prompts if missing)
    get_api_key()

    # run the interview
    answers = run_interview()

    if answers is None:
        print_warning("Interview cancelled. No README was generated.")
        return

    # generate readme from answers + codebase scan
    console.print("\n[dim]Scanning codebase and generating README...[/dim]")
    readme_content = generate_readme(answers)

    # write to file
    write_readme(readme_content)

    print_success("Done. Your README is ready.")


if __name__ == "__main__":
    main()
