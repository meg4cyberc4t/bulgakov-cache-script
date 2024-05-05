"""
Network requests to LXP IThub. Return specific values or dict.

Copyright (c) 2024, Igor Molchanov.  Please see the AUTHORS file
for details. All rights reserved. Use of this source code is governed by a
BSD-style license that can be found in the LICENSE file.
"""

import aiohttp


async def sign_in(session: aiohttp.ClientSession, login: str, password: str) -> tuple[str, int]:
    """
    Authorization in the system.
    
    Returns the user's authorization token and id.
    """
    data = {
        "login": login,
        "password": password,
    }
    async with session.post('/api/v2/auth/sign-in', data=data) as response:
        response_json = await response.json()
        if not response.ok:
            message = response_json['message']
            raise RuntimeError(f"Not getting the authorization key: {message}")
        return response_json['token'], response_json['data']['id']


async def subject(session: aiohttp.ClientSession, subject_id: int) -> dict:
    """Getting a subject from LXP IThub."""
    async with session.get(f'/api/v2/subjects/{subject_id}') as response:
        response_json = await response.json()
        if not response.ok:
            message = response_json['message']
            raise RuntimeError(f"Not getting the subject: {message}")
        return response_json['data']


async def step(session: aiohttp.ClientSession, step_id: int) -> dict:
    """Getting a step from LXP IThub."""
    async with session.get(f'/api/v2/lessons/{step_id}') as response:
        response_json = await response.json()
        if not response.ok:
            message = response_json['message']
            raise RuntimeError(f"Not getting the step: {message}")
        return response_json['data']


async def load_file(session: aiohttp.ClientSession, link: str) -> bytes:
    """Getting a file from LXP IThub."""
    if "https" not in link:
        async with session.get(link, allow_redirects=True) as response:
            return await response.content.read()
    async with aiohttp.ClientSession() as session:
        async with session.get(link, allow_redirects=True) as response:
            return await response.content.read()


async def student_subjects_per_page(
    session: aiohttp.ClientSession,
    page: int,
    user_id: int
) -> dict:
    """Lazy load request to get a list of the user's subjects by student role."""
    address = f'/api/v2/users/{user_id}/subjects?role=student&page={page}'
    async with session.get(address) as response:
        response_json = await response.json()
        if not response.ok:
            message = response_json['message']
            raise RuntimeError(f"Not getting the subjects: {message}")
        return response_json['data']
    