import asyncio

async def f1():
    print("f1 is running")
    await asyncio.sleep(2)  # Simulate some asynchronous work
    print("f1 is done")
    print("f1 done after f2 has returned, but it can't return a value!")

async def f2():
    print("f2 is running")
    await asyncio.sleep(1)  # Simulate some asynchronous work
    print("f2 is done")

    # Call f1 inside f2 and let it run concurrently
    asyncio.create_task(f1())
    
    return "SUCCESS"

async def main():
    # Start f2 and wait for it to finish
    status = await f2()

    # Continue with other tasks or code after f2 has finished
    print("Status:" + status)
    

if __name__ == "__main__":
    asyncio.run(main())