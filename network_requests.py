from ctypes import ArgumentError
import requests


def login(login: str, password: str) -> tuple[str, int]:
    data = {
        "login": login,
        "password": password,
    }
    result = requests.post(
        'https://ithub.bulgakov.app/api/v2/auth/sign-in', 
        data=data
    )
    if not result.ok:
        message = result.json()['message']
        raise RuntimeError(f"Not getting the authorization key: {message}")
    try:
        return result.json()['token'], result.json()['data']['id']
    except:
        raise RuntimeError(f"Not getting the authorization key: {result.json()}")
    
    
def subject(subject_id: int, token: str) -> dict:
    result = requests.get(f'https://ithub.bulgakov.app/api/v2/subjects/{subject_id}', 
                          headers={"Authorization": f"Bearer {token}"})
    if not result.ok:
        message = result.json()['message']
        raise RuntimeError(f"Not getting the subject: {message}")
    return result.json()['data']
    

def step(step_id: int, token: str) -> dict:
    result = requests.get(f'https://ithub.bulgakov.app/api/v2/lessons/{step_id}', 
                          headers={"Authorization": f"Bearer {token}"})
    if not result.ok:
        message = result.json()['message']
        raise RuntimeError(f"Not getting the step: {message}")
    return result.json()['data']


def load_file(link: str) -> bytes:
    if "https" not in link:
        link = "https://ithub.bulgakov.app/" + link
    result = requests.get(link, allow_redirects=True)
    return result.content


def student_subjects_per_page(page: int, user_id: int, token: str) -> dict:
    result = requests.get(f'https://ithub.bulgakov.app/api/v2/users/{user_id}/subjects?role=student&page={page}',
                          headers={"Authorization": f"Bearer {token}"})
    if not result.ok:
        message = result.json()['message']
        raise RuntimeError(f"Not getting the subjects: {message}")
    return result.json()['data']