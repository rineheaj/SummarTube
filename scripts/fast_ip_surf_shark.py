import asyncio
from rich.progress import Progress
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import httpx


console = Console()

url = "https://api.ipify.org?format=json"


async def fetch_ip():
    async with httpx.AsyncClient(timeout=5) as a_client:
        resp = await a_client.get(url)

        return resp.json().get("ip", "HUH???")


async def main():
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching your public IP...", total=None)

        ip = await fetch_ip()

        progress.remove_task(task)

    text = f"[green]Public IP:[/] [yellow]{ip}[/]\n"

    panel = Panel(
        Align.center(text),
        title="IP Info",
        title_align="center",
        width=50
    )
    console.print(panel)


if __name__ == "__main__":
    asyncio.run(main=main())
