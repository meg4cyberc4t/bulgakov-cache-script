"""
Additional functionality.

Copyright (c) 2024, Igor Molchanov.  Please see the AUTHORS file
for details. All rights reserved. Use of this source code is governed by a
BSD-style license that can be found in the LICENSE file.
"""

import re
import asyncio
import time


def santize_path(source: str) -> str:
    """Clearing a string of characters prohibited for use in a file path"""
    return re.sub(r'[^\w\-_\. ]', '_', source)


class SequenceLimit:
    """
    A decorator that slows down the function call. 
    No more often than calls_limit per period.
    
    Prevents 429 (Too Many Requests) network error.
    """
    def __init__(self, calls_limit: int = 5, period: int = 1):
        self.calls_limit = calls_limit
        self.period = period
        self.semaphore = asyncio.Semaphore(calls_limit)
        self.requests_finish_time = []

    async def sleep(self):
        """Waiting in the queue if the restriction is passed"""
        if len(self.requests_finish_time) >= self.calls_limit:
            sleep_before = self.requests_finish_time.pop(0)
            if sleep_before >= time.monotonic():
                await asyncio.sleep(sleep_before - time.monotonic())

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            async with self.semaphore:
                await self.sleep()
                res = await func(*args, **kwargs)
                self.requests_finish_time.append(time.monotonic() + self.period)
            return res
        return wrapper
    