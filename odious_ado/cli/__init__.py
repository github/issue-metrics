# -*- coding: utf-8 -*-
"""
Command Line Interface
"""
import sys
import asyncio
import uvloop

from multiprocessing import freeze_support
from odious_ado.cli.commands import main


if __name__ == "__main__":
    freeze_support()
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(main())
    else:
        uvloop.install()
        asyncio.run(main())
