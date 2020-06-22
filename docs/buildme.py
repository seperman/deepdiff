#!/usr/bin/env python
"""
Create a .env file in this folder that has BUILD_PATH defined, otherwise the _build will be used.
Then run ./buildme.py
It will remove the contents of the BUILD_PATH folder and recreate it.
"""
import os
import time
import datetime
import shutil
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sphinx.cmd.build import main as sphinx_main


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def delete_dir_contents(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


class MyHandler(FileSystemEventHandler):

    def __init__(self):
        self.last_modified = datetime.datetime.now()

    def on_any_event(self, event):
        load_dotenv(override=True)
        build_path = os.environ.get('BUILD_PATH', '_build')
        if event is None:
            print('initial build')
        else:
            print(f'event type: {event.event_type}  path : {event.src_path}')
        if event is not None and (
                datetime.datetime.now() - self.last_modified < datetime.timedelta(seconds=2)):
            return
        else:
            self.last_modified = datetime.datetime.now()
        argv = ['-b', 'html', '.', build_path]
        ensure_dir(build_path)
        delete_dir_contents(build_path)
        # argv = ['-b', 'html', '-d', f'{build_path}/doctrees', '.', f'{build_path}/html']
        sphinx_main(argv)
        print('waiting for file changes. Press Ctrl+c to cancel.')


if __name__ == "__main__":
    event_handler = MyHandler()
    event_handler.on_any_event(event=None)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
