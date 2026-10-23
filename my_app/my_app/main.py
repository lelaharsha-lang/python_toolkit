import asyncio
import httpx
import random


async def fetch_data(url: str, max_tries: int = 3):
    async with httpx.AsyncClient(timeout=5.0) as client:
        for attempt in range(max_tries + 1):
            try:
                response = await client.get(url)
                if response.status_code not in (429, 500, 502, 503, 504):
                    return response
                if attempt == max_tries:
                    return response
            except httpx.RequestError:
                if attempt == max_tries:
                    return None
            delay = min(2**attempt, 10) + random.uniform(0, 1)
            await asyncio.sleep(delay)


async def main():
    url = "https://httpbin.org/status/503"
    response = await fetch_data(url)
    if response is None:
        print("Failed to fetch data.")
    else:
        print(f"Response:{response}")
        print(f"Status_code:{response.status_code}")
        # print(f"Response_json:{response.text}")


asyncio.run(main())
