#!/usr/bin/env python3.7
import logging

import click
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


@click.command()
@click.argument("dropbox-dir")
def main(dropbox_dir):
    watchdog_event_handler = LoggingEventHandler()
    watchdog_observer = Observer()
    watchdog_observer.schedule(watchdog_event_handler, dropbox_dir, recursive=True)
    watchdog_observer.start()
    watchdog_observer.join()


if __name__ == '__main__':
    main()
