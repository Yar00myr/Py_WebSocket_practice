import asyncio
import websockets


async def vote_client():
    uri = "ws://localhost:8000/vote"
    try:
        async with websockets.connect(uri) as ws:

            vote = "photo 1"
            await ws.send(vote)
            response = await ws.recv()
            print(f"Vote WebSocket received: {response}")
    except Exception as e:
        print(f"Error in vote_client: {e}")


async def chat_client():
    user_id = "user123"
    uri = f"ws://localhost:8000/chat/{user_id}"

    try:
        async with websockets.connect(uri) as ws:

            message = "Hello, this is a test message!"
            await ws.send(message)

            response = await ws.recv()
            print(f"Chat WebSocket received: {response}")
    except Exception as e:
        print(f"Error in chat_client: {e}")


async def main():

    await asyncio.gather(vote_client(), chat_client())


if __name__ == "__main__":
    asyncio.run(main())
