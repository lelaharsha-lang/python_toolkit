import asyncio
import httpx
import random
import typer
from pathlib import Path

app = typer.Typer()
retryable_status_codes = [429, 500, 502, 503, 504]


async def check_urls(
    client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore, retries: int
) -> tuple[str, int | None, str]:
    for attempt in range(retries + 1):
        try:
            async with semaphore:
                response = await client.get(url)
                status = response.status_code

                if status not in retryable_status_codes:
                    result = "OK" if status < 400 else "FAILED"
                    return url, status, result

                if attempt == retries:
                    return url, status, "Failed"

        except httpx.RequestError:
            if attempt == retries:
                return url, status, "ERROR"

        delay = (2**attempt) + random.uniform(0, 1)

        await asyncio.sleep(delay)

        print(f"{attempt}:{semaphore}")

    return url, None, "failed"


async def run_checker(urls: list[str], concurrency: int, retries: int) -> None:
    semaphore = asyncio.Semaphore(concurrency)
    timeout = httpx.Timeout(10.0)

    limits = httpx.Limits(
        max_connections=concurrency, max_keepalive_connections=concurrency
    )
    async with httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        follow_redirects=True,
    ) as client:
        results = await asyncio.gather(
            *[check_urls(client, url, semaphore, retries) for url in urls]
        )
        successful = 0
        for url, status, result in results:
            print(f"{result:6} | {status:4} | {url}")

            if result == "OK":
                successful += 1
        print(f"checked_urls:{len(results)}")
        print(f"successful_urls:{successful}")
        print(f"unsuccessful:{len(results) - successful}")


@app.command()
def main(
    file: Path = typer.Argument(..., exists=True),
    concurrency: int = typer.Option(10, min=1, max=100),
    retries: int = typer.Option(3, min=0, max=5),
) -> None:
    urls = [
        line.strip()
        for line in file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print("file is empty")

    if len(urls) > 100:
        print("urls must less than 100")

    asyncio.run(run_checker(urls, concurrency, retries))


if __name__ == "__main__":
    app()
