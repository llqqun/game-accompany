import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script])
        print(f"Started {self.script} with PID {self.process.pid}")

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"{event.src_path} has been modified, restarting script...")
            self.start_script()

def start_dev_server(script):
    event_handler = ReloadHandler(script)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    print(f"Starting development server for {script} with hot reload...")
    event_handler.start_script()  # 启动应用程序
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # start_dev_server("./src/main.py")
    start_dev_server("./src/copilot.py")

