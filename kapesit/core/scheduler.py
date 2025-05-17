import threading
import queue
class Scheduler:
    def __init__(self):
        self.tasks = queue.Queue()
        self.running = False
    def add_task(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))
    def run(self):
        self.running = True
        while self.running:
            if not self.tasks.empty():
                func, args, kwargs = self.tasks.get()
                threading.Thread(target=func, args=args, kwargs=kwargs).start()
    def stop(self):
        self.running = False 