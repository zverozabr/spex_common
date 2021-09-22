from threading import main_thread
import time
import traceback


def every(delay, task):
    next_time = time.time() + delay
    while main_thread().is_alive():
        time.sleep(max(0, next_time - time.time()))
        try:
            if main_thread().is_alive():
                task()
        except Exception:
            traceback.print_exc()
        #  in production code you might want to have this instead of course:
        #  logger.exception("Problem while executing repetitive task.")
        #  skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay
