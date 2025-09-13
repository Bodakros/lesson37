import asyncio
import signal
import contextlib
from src.Client import Logic


# pip install cryptg
async def main():
    stop = asyncio.Event()

    # Windows-friendly SIGINT handler to trigger shutdown
    def _handle_sigint(sig, frame):
        stop.set()

    try:
        signal.signal(signal.SIGINT, _handle_sigint)
    except Exception:
        # If signal setup fails in certain environments (e.g., restricted debuggers), fallback to KeyboardInterrupt handling
        pass

    logic = Logic()
    worker = asyncio.create_task(logic.run())
    stop_task = asyncio.create_task(stop.wait())

    try:
        await asyncio.wait({worker, stop_task}, return_when=asyncio.FIRST_COMPLETED)
    finally:
        # Cancel whichever is still running
        if not worker.done():
            worker.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await worker

        if not stop_task.done():
            stop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await stop_task

        # Optional cleanup if Logic has a close() method
        if hasattr(logic, "close") and callable(getattr(logic, "close")):
            maybe_awaitable = logic.close()
            if asyncio.iscoroutine(maybe_awaitable):
                with contextlib.suppress(Exception):
                    await maybe_awaitable


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Swallow the Ctrl+C so it doesn't print a traceback
        pass