# -*- coding: utf-8 -*-
import asyncio
import csv
import json
import os
import re
import sys
import signal
from types import SimpleNamespace
from io import StringIO
from typing import Any, Awaitable, Callable, Dict, List, Tuple


__all__ = [
    "request",
    "request_async",
    "formatter",
    "gather_dict",
    "gather_list",
    "to_csv",
    "to_json",
    "validate_path",
    "writer",
    "normalize_keys",
    "ProcessHandler",
    "NestedNamespace",
]

PROJECT_ROOT: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
)
APP_ROOT: str = os.path.realpath(os.path.join(PROJECT_ROOT, os.pardir))
PLUGIN_PATH: str = os.path.realpath(os.path.join(PROJECT_ROOT, "plugins"))


async def gather_list(tasks: List[Awaitable]):
    async def mark(coro: Awaitable) -> Tuple[str, str]:
        return await coro

    return await asyncio.gather(*tasks)


async def gather_dict(tasks: Dict[str, Awaitable[str]]) -> Dict[str, str]:
    async def mark(key: str, coro: Awaitable[str]) -> Tuple[str, str]:
        return key, await coro

    return {
        key: result
        for key, result in await asyncio.gather(
            *(mark(key, coro) for key, coro in tasks.items())
        )
    }


def stdout(data: str) -> int:
    return sys.stdout.write(data)


def _format_complex(record: dict) -> dict:
    # don't want to get rid of non-csv values, so we will
    #  simply write them as a JSON string instead

    json_opts = (",", ":")
    cast_types = (list, tuple, dict)

    return {
        k: (v if not isinstance(v, cast_types) else json.dumps(v, separators=json_opts))
        for k, v in record.items()
    }


def to_json(records: List[dict]) -> str:
    return json.dumps(records, indent=4)


def formatter(data: List[dict], output_type: str) -> str:
    formats = {"json": to_json, "csv": to_csv}

    return formats[output_type](data)


def writer(data: str, destination: str):
    if not destination:
        stdout(data)
    else:
        fs(data, destination)


def fs(data: str, filename: str) -> None:
    with open(filename, "w") as f:
        f.write(data)


def to_csv(records: List[dict]) -> str:
    if not records:
        return ""

    defaults = {
        "delimiter": ",",
        "quoting": csv.QUOTE_MINIMAL,
        "dialect": "excel",
        "lineterminator": "\n",
    }

    handler = StringIO()

    header = records[0].keys()

    writer = csv.DictWriter(handler, fieldnames=header, **defaults)
    writer.writeheader()
    for record in records:
        writer.writerow(_format_complex(record))

    return handler.getvalue()


# pre-compile regex
# there is a small bug in this where if you pass SomethingIs_Okay you will get two _ between is and okay
first_cap_re = re.compile("(.)([A-Z][a-z]+)")
all_cap_re = re.compile("([a-z0-9])([A-Z])")


async def normalize_keys(suspect, snake_case=True):
    """
    take a dict and turn all of its type string keys into snake_case
    """
    if not isinstance(suspect, dict):
        raise TypeError("you must pass a dict.")

    for key in list(suspect):
        if not isinstance(key, str):
            continue

        if snake_case:
            s1 = first_cap_re.sub(r"\1_\2", key)
            new_key = all_cap_re.sub(r"\1_\2", s1).lower()  # .replace('-', '_')
        else:
            new_key = key.lower()

        value = suspect.pop(key)
        if isinstance(value, dict):
            suspect[new_key] = normalize_keys(value, snake_case)

        elif isinstance(value, list):
            for i in range(0, len(value)):

                if isinstance(value[i], dict):
                    await normalize_keys(value[i], snake_case)

            suspect[new_key] = value
        else:
            suspect[new_key] = value

    return suspect


def request(url: str, callback: Callable) -> Any:
    return asyncio.run(request_async(url=url, callback=callback))


async def request_async(url: str, callback: Callable):
    """async GET wrapper"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
            return callback(response)


async def validate_path(path):
    if os.path.exists(path):
        return path
    else:
        raise SystemError("{0} doesn't exist.".format(path))


class ProcessHandler:
    def __init__(self, exit_on_term: bool = True):
        self.received_term_signal = self.received_signal = False
        self.exit_on_term = exit_on_term

        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT):
            signal.signal(sig, self.__handler)

    def __handler(self, signum, frame):
        self.last_signal = signum
        self.received_signal = True

        if signum in [2, 3, 15]:
            # print 'is being terminated with signum: {1}.\n'.format(self.name, signum)
            self.received_term_signal = True

            if self.exit_on_term:
                exit(signum)


class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)
