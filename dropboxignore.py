#!/usr/bin/env python3.7
from collections import defaultdict
import re
import logging
from pathlib import Path

import click
from gitignore_parser import parse_gitignore
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xattr

IGNORE_FILENAME_RE = re.compile(r".*?\.(git|dropbox)ignore$")


@click.command()
@click.argument("dropbox-dir")
@click.option("--debug", is_flag=True)
def main(dropbox_dir, debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    dropbox_dir = Path(dropbox_dir).resolve()
    watchdog_event_handler = DropboxIgnoreEventHandler(dropbox_dir)
    watchdog_observer = Observer()
    watchdog_observer.schedule(watchdog_event_handler, str(dropbox_dir), recursive=True)
    watchdog_observer.start()
    watchdog_observer.join()


class DropboxIgnoreEventHandler(FileSystemEventHandler):
    def __init__(self, dropbox_dir: Path):
        super().__init__()
        self.dropbox_dir = dropbox_dir
        self.ignorefiles_by_dir = defaultdict(dict)

    def on_created(self, event):
        logging.debug("Created %s: %s", 'directory' if event.is_directory else 'file', event.src_path)

        fullpath = Path(event.src_path)
        parent_dir = fullpath.parent

        if not event.is_directory and IGNORE_FILENAME_RE.match(event.src_path):
            logging.debug("Found new ignore file at %s", event.src_path);
            matcher = parse_gitignore(event.src_path)
            self.ignorefiles_by_dir[parent_dir][fullpath] = matcher

        else:
            dir_matchers = self.ignorefiles_by_dir.get(parent_dir)
            if len(dir_matchers) == 0:
                return

            matches_any = any(m(str(fullpath)) for m in dir_matchers.values())
            logging.debug("New file matches ignore rule!");

    def on_deleted(self, event):
        logging.debug("Deleted %s: %s", 'directory' if event.is_directory else 'file', event.src_path)

        if not event.is_directory and IGNORE_FILENAME_RE.match(event.src_path):
            logging.debug("Deleted ignore file at %s", event.src_path);
            fullpath = Path(event.src_path)
            dir_matchers = self.ignorefiles_by_dir[fullpath.parent]
            if fullpath in dir_matchers:
                del dir_matchers[fullpath]
            if len(dir_matchers) == 0:
                del self.ignorefiles_by_dir[fullpath.parent]


if __name__ == '__main__':
    main()
