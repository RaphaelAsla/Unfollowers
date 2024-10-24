#!/usr/bin/python3
import re
import asyncio
import aiohttp
from datetime import datetime

async def obtain_app_id(session: aiohttp.ClientSession) -> str:
    async with session.get("https://www.instagram.com") as response:
        response_text = await response.text()
        appid_match = re.search(r'appId":(\d*),', response_text)
        if appid_match:
            return appid_match.group(1)
        else:
            return "-1"

async def obtain_session_id(username, password) -> str:
    time = int(datetime.now().timestamp())

    payload = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{time}:{password}",
        "queryParams": {},
        "optIntoOneTap": "false"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.instagram.com/accounts/login/") as response:
            response.raise_for_status()
            response_text = await response.text()
            csrf_match = re.search(r'csrf_token":"(.*?)"', response_text)
            if csrf_match:
                csrf = csrf_match.group(1)
            else:
                return "-1"
        
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken": csrf,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }

        async with session.post("https://www.instagram.com/accounts/login/ajax/", data=payload, headers=headers) as response:
            session_id = response.cookies.get("sessionid")
            if session_id:
                return session_id.value
            else:
                return "-1"

def find_unfollowers(followers, following) -> dict:
    following_keys = set(following.keys())
    followers_keys = set(followers.keys())

    unfollowers_keys = following_keys - followers_keys

    unfollowers = {user: following[user] for user in unfollowers_keys}

    return unfollowers

def get_bulk_user_info(data) -> dict:
    bulk_info = {}
    for d in data:
        bulk_info[d["username"]] = d
    return bulk_info

async def obtain_unfollowers(session_id: str) -> dict:
    user_id = session_id.split("%")[0]

    cookies = {
        "sessionid": session_id,
    }

    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }

    followers_url = f"https://www.instagram.com/api/v1/friendships/{user_id}/followers/"
    following_url = f"https://www.instagram.com/api/v1/friendships/{user_id}/following/"

    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        appid = await obtain_app_id(session)
        headers["X-Ig-App-Id"] = appid

        session.headers.update(headers)

        params = {
            "count": "12",
        }
       
        async def fetch_users(url):
            users_list = {}

            while True:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        users = get_bulk_user_info(response_json["users"])
                        users_list.update(users)

                        if "next_max_id" in response_json:
                            params.update({"max_id": response_json["next_max_id"]})
                        else:
                            break
                    else:
                        print("Request failed.")
                        print(f"Status code: {response.status}")
                        print(await response.text())
                        break

            return users_list

        async def fetch_followers():
            return await fetch_users(followers_url)

        async def fetch_following():
            return await fetch_users(following_url)

        followers_result, following_result = await asyncio.gather(
            fetch_followers(),
            fetch_following()
        )

    return find_unfollowers(followers_result, following_result)
