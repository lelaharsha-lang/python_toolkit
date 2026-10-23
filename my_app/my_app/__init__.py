import asyncio


async def fetch_data(delay, id):
    print("fetching data for id:", id)
    await asyncio.sleep(delay)
    print("data fetched for id:", id)
    return {"data": "some data", "id": id}


async def main():
    task1 = fetch_data(2, 1)
    task2 = fetch_data(3, 2)

    result1 = await task1
    print("received result:", result1)

    result2 = await task2
    print("received result:", result2)


asyncio.run(main())
