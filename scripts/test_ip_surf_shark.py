import requests
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress


console = Console()

url = "https://api.ipify.org?format=json"


start_time = time.perf_counter()

with Progress() as progress:
    task = progress.add_task("[cyan]Fetching your public IP...", total=None)
    resp = requests.get(url, timeout=5)
    progress.remove_task(task)

elapsed_time = time.perf_counter() - start_time

ip = resp.json()["ip"]

panel = Panel(
    f"[yellow]Public IP:[/] {ip}\n[green]Request time:[/] {elapsed_time:.3f} seconds",
    title="IP Info",
    title_align="center",
)

console.print(panel)
