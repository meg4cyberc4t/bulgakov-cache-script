#!/usr/bin/env python3
#
# Copyright (c) 2024, Igor Molchanov.  Please see the AUTHORS file
# for details. All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.

import argparse
from ctypes import ArgumentError
from email.mime import base
import io
import json
import os
from re import sub
import subprocess
import sys
import time
import json
from typing import Coroutine

import aiohttp
from requests import head
import nrequests as requests
import asyncio
import utils as utils

def build_options():
    parser = argparse.ArgumentParser(
        prog='bulgakov-cache-script',
        description='Downloads the topic (or full disciplines) you are studying from LXP IThub',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-o', '--out', 
                        type=str,
                        help='The output directory where your topic will be saved',
                        default='./out')

    parser.add_argument('-c', '--credentials', 
                        type=str,
                        help="""The path to the file with your login information.
                        The following file formats are possible (.env, json).
                        
                        Example (json):
                        { "login": "myemail@gmail.com", "password": "yoursecretpassword" }
                        """,
                        required=True)

    parser.add_argument('-m', '--mode', 
                        type=str,
                        help="Topic output format.",
                        choices=['json', 'md'])
    
    parser.add_argument('--subject', 
                        type=int,
                        help="Id of the subject to be downloaded. If nothing is transmitted, content in all disciplines will be downloaded!")
    
    return parser

   
async def download_image(session: aiohttp.ClientSession, subject_asset_path: str, link: str, id: int) -> str:
        print(f"Image loading: {link}")
        last_part =  link.split('/')[-1]
        extension = last_part.split('.')[-1] if len(last_part.split('.')) > 1 else None
        filename = f"photo_{id}"
        if extension is not None:
            filename += f".{extension}"
        photo_bytes = await requests.load_file(session=session, link=link)
        photo_path = os.path.join(subject_asset_path, filename)
        with open(photo_path, "wb") as file:
            file.write(photo_bytes)
        return filename
        
async def download_document(session: aiohttp.ClientSession, subject_asset_path: str, link: str, id: int) -> str:
    print(f"Document loading: {link}")
    extension = link.split('.')[-1]
    filename = f"document_{id}.{extension}"
    photo_bytes = await requests.load_file(session=session, link=link)
    photo_path = os.path.join(subject_asset_path, filename)
    with open(photo_path, "wb") as file:
        file.write(photo_bytes)
    return filename


@utils.SequenceLimit()
async def download_step(
        session: aiohttp.ClientSession,
        step_id: int,
        chapter_path: str,
        mode: str,
        subject_asset_path: str,
    ):
        step = await requests.step(session=session, step_id=step_id)
        step_title = step['title']
        print(f"Step loading: {step_title}")
        
        step_path = os.path.abspath(os.path.join(os.path.abspath(chapter_path),  utils.santize_path(f"{step_title}-{step_id}.{mode}")))
        with open(step_path, 'w', encoding="utf-8") as file:
            if mode == "md":
                public_text = step['public_text']
                public_photos = step['public_photos']
                private_text = step['private_text']
                private_videos = step['private_videos']
                private_links = step['private_links']
                private_documents = step['private_documents']
                sections = step['sections'] 
                content: str = ""
                content += f"# {step_title}\n"
                content += f"\n"
                content += "### Зачем это учить??\n"
                content += f"{public_text}\n"
                content += '\n'
                for photo in public_photos:
                    photo_id = photo['id']
                    photo_link = photo['normal']
                    filename = await download_image(session=session, subject_asset_path=subject_asset_path, link=photo_link, id=photo_id)
                    photo_path_rellative = os.path.join("../assets/", filename)
                    content += f"![{photo_id}]({photo_path_rellative})\n"
                content += "### Как это учить???\n"
                content += f"{private_text}\n"
                content += '\n'
                for photo in private_videos:
                    photo_id = photo['id']
                    photo_link = photo['normal']
                    filename = await download_image(session=session, subject_asset_path=subject_asset_path, link=photo_link, id=photo_id)
                    photo_path_rellative = os.path.join("../assets/", filename)
                    content += f"![{photo_id}]({photo_path_rellative})\n"
                for link in private_links:
                    link_title = link['title']
                    link_url = link['url']
                    content += f"[Ссылка: {link_title}]({link_url})\n"
                for video in private_videos:
                    video_description = video['description']
                    video_path = video['path']
                    content += f"[Видео: {video_description}]({video_path})\n"
                for document in private_documents:
                    document_id = document['id']
                    document_path = document['path']
                    document_description = document['description']
                    filename = await download_document(session=session, subject_asset_path=subject_asset_path, link=document_path, id=document_id)
                    document_path_rellative = os.path.join("../assets/", filename)
                    content += f"[Документ {document_description}]({document_path_rellative})\n"
            
                for section in sections:
                    content += f"### {section['title']}\n"
                    if section['content'] is not None:
                        content += section['content'] + "\n"
                    for photo in section['photos']:
                        photo_id = photo['id']
                        photo_link = photo['normal']
                        filename = await download_image(session=session, subject_asset_path=subject_asset_path, link=photo_link, id=photo_id)
                        photo_path_rellative = os.path.join("../assets/", filename)
                        content += f"![{photo_id}]({photo_path_rellative})\n"
                    for link in section['links']:
                        link_title = link['title']
                        link_url = link['url']
                        content += f"[Ссылка: {link_title}]({link_url})\n"
                    for video in section['videos']:
                        video_description = video['description']
                        video_path = video['path']
                        content += f"[Видео: {video_description}]({video_path})\n"
                    for document in section['documents']:
                        document_id = document['id']
                        document_path = document['path']
                        document_description = document['description']
                        filename = await download_document(session=session, subject_asset_path=subject_asset_path, link=document_path, id=document_id)
                        document_path_rellative = os.path.join("../assets/", filename)
                        content += f"[Документ {document_description}]({document_path_rellative})\n"
                file.write(content)
            elif mode == "json":
                file.write(json.dumps(step, ensure_ascii=False, indent=4, sort_keys=True))
    
    
@utils.SequenceLimit()
async def download_subject(
    session: aiohttp.ClientSession,
    subject_id: int,
    out_dir: str,
    mode: str
):
    subject = await requests.subject(session=session, subject_id=subject_id)
    code = subject['code']
    title = subject['title']
    print(f"Subject loading: {title}")
        
    subject_path = os.path.join(out_dir, utils.santize_path(" ".join([title, code,  str(subject_id)])))
    if not os.path.exists(os.path.abspath(out_dir)):
        os.mkdir(os.path.abspath(out_dir))
    if not os.path.exists(os.path.abspath(subject_path)):
        os.mkdir(os.path.abspath(subject_path))
    subject_asset_path = os.path.join(subject_path, "assets")
    if not os.path.exists(os.path.abspath(subject_asset_path)):
        os.mkdir(os.path.abspath(subject_asset_path))
    
    intro_path = os.path.abspath(os.path.join(os.path.abspath(subject_path),  f"intro.{mode}"))
    with open(intro_path, 'w', encoding="utf-8") as file:
        if mode == "md":
            content: str = ""
            content += f"# {title}\n"
            content += f"## {code}\n"
            content += "### О чём эта дисциплина?\n"
            content += f"> {subject['description']}\n"
            content += '\n'
            content += "### Преподаватели:\n"
            for teacher in subject['teachers']:
                content += " ".join([teacher['first_name'], teacher['last_name'], teacher['middle_name']]) + "\n"
            content += '\n'
            content += "### Группы:\n"
            for group in subject['groups']:
                content += " - " + group['name'] + "\n"
            file.write(content)
        elif mode == "json":
            file.write(json.dumps(subject, ensure_ascii=False, indent=4, sort_keys=True))
    
    chapters = {} # chapter_id: chapter_title
    chapters_topics_mapper = {} # chapter_id: [topic_id, topic_id...]
    
    for chapter in subject['chapters']:
        id = chapter['id']
        title = chapter['title']
        chapters[id] = title
        chapters_topics_mapper[id] = []
        
    for step in subject['steps']:
        id = step['id']
        chapter_id = step['chapter_id']
        hidden = step['hidden']
        if chapter_id in chapters_topics_mapper and not hidden:
            chapters_topics_mapper[chapter_id].append(id)
    
    for chapter_id, chapter_title in chapters.items():
        print(f"Chapter loading: {chapter_title}")
        chapter_path = os.path.abspath(os.path.join(subject_path, utils.santize_path(chapter_title)))
        if not os.path.exists(chapter_path):
            os.mkdir(chapter_path)
        for step_id in chapters_topics_mapper[chapter_id]:
            await download_step(
                session=session,
                chapter_path = chapter_path, 
                step_id=step_id, 
                mode=mode,
                subject_asset_path = subject_asset_path
            )    

# Returns the user's authorization token and id
async def login(session: aiohttp.ClientSession, credentials_file_path: str) -> tuple[str, int]:
    with open(credentials_file_path, 'r') as file:
        file_name, file_extension = os.path.splitext(credentials_file_path)
        if file_extension == ".json":
            loads = json.loads(file.read())
            login = loads['login']
            password = loads['password']
        elif file_name == ".env":
            for line in file.read():
                if line.startswith('#') or not line.strip():
                    continue
                key, value = line.strip().split('=', 1)
                if key == "login":
                    login = value
                if key == "password":
                    password = value
        else:
            raise ArgumentError(f"An unfamiliar file type for credentials {file_extension} from the {file_name} file")
    if login is None or password is None:
        raise ArgumentError(f"Login or password was not provided! {file=} {password=}")
    return await requests.login(session=session, login=login, password=password)

async def get_list_of_subject_ids(session: aiohttp.ClientSession, user_id: int, token: str) -> list[int]:
    page = 1
    subject_ids = []
    while True:
        result = await requests.student_subjects_per_page(
            session= session,
            page=page, 
            user_id=user_id, 
        )
        for subject in result['data']:
            subject_ids.append(subject['id'])
        last_page = result['last_page']
        print(f'Getting a list of all disciplines: {page} page ({len(subject_ids)} total)')
        if last_page == page:
            break
        page += 1
    return subject_ids

async def main():
    # Parse the options.
    parser = build_options()
    options = parser.parse_args()
    
    with aiohttp.TCPConnector(limit_per_host=10, limit=10) as base_connector:
        async with aiohttp.ClientSession(
            base_url="https://ithub.bulgakov.app/",
            connector_owner=False,
            connector=base_connector,
        ) as session:
            token, user_id = await login(session=session, credentials_file_path=options.credentials)
            
        async with aiohttp.ClientSession(
            base_url="https://ithub.bulgakov.app/",
            headers={'Authorization': f"Bearer {token}"},
            connector_owner=False,
            connector=base_connector
        ) as session:
            if options.subject is None:
                subjects: list[int] = await get_list_of_subject_ids(session=session, token=token, user_id=user_id)
            else:
                subjects: list[int] = [options.subject]
                
            reqs: list[Coroutine] = []
            for subject_id in subjects:
                reqs.append(download_subject(session=session, out_dir=options.out, subject_id=subject_id, mode=options.mode))

            await asyncio.gather(*reqs)
            base_connector.close()
            return 0
    
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop_policy().get_event_loop()
    sys.exit(loop.run_until_complete(main()))
