#!/usr/bin/env python
"""
Create a .env file in this folder that has BUILD_PATH defined, otherwise the _build will be used.
Then run ./buildme.py
It will remove the contents of the BUILD_PATH folder and recreate it.
"""
import os
import datetime
import shutil
from dotenv import load_dotenv
from sphinx.cmd.build import main as sphinx_main

CACHE_PATH = '/tmp/sphinx_doctree'


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def delete_dir_contents(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


if __name__ == "__main__":
    load_dotenv(override=True)
    build_path = os.environ.get('BUILD_PATH', '_build')
    doc_version = os.environ.get('DOC_VERSION', '')
    if not build_path.endswith('/'):
        build_path = build_path + '/'
    build_path += doc_version
    argv = ['-b', 'html', '-d', CACHE_PATH, '.', build_path]
    ensure_dir(build_path)
    delete_dir_contents(build_path)
    delete_dir_contents('/tmp/sphinx_doctree')  # Disable this for faster build time but it might not properly invalidate the cache
    sphinx_main(argv)
