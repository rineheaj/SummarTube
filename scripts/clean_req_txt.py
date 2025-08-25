from pathlib import Path
from rich.console import Console

console = Console()

req_file = Path(__file__).parent.parent / "requirements.txt"


strip_these_lines = []
cleaned_lines = []


def get_file_lines(filepath):
    with open(filepath, "r", encoding="utf-8") as infile:
        text = infile.read()
        lines = text.split("\n")
        if lines:
            for line in lines:
                console.print(f"[yellow]LINE: {line}")

        return lines


def strip_versions(req_lines: list):
    for line in req_lines:
        if not line.strip():
            continue
        console.print(f"[red]LINES TO STRIP: {line}")
        strip_these_lines.append(line)


def strip_me_daddy(lines_to_be_stripped):
    for line in lines_to_be_stripped:
        name = line.split("==")[0]
        console.print(f"[green]PACKAGE NAME: {name}")
        cleaned_lines.append(name)


def write_cleaned_lines_file(cleaned_name_lines):
    with open(req_file, mode="w", encoding="utf-8") as outfile:
        for line in cleaned_name_lines:
            if not line.split():
                continue
            outfile.write(f"{line}\n")

        console.print("[magenta]requirements.txt file has been cleaned[/]")


def main():
    if req_file.exists() and req_file.is_file():
        console.print("[blue]Found requirements.txt[/]")
        lines = get_file_lines(filepath=req_file)
        strip_versions(req_lines=lines)
        strip_me_daddy(lines_to_be_stripped=strip_these_lines)
        write_cleaned_lines_file(cleaned_name_lines=cleaned_lines)
    else:
        console.print(f"[red]Missing unable to find requirements.txt ➡️  {req_file}[/]")


if __name__ == "__main__":
    main()
