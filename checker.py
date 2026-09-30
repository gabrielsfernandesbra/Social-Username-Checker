import asyncio
import re
import httpx
from fastapi import HTTPException

SOCIAL_NETWORKS = {
    "Instagram": "https://www.instagram.com/{}/",
    "Facebook": "https://www.facebook.com/{}",
    "X": "https://x.com/{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "Threads": "https://www.threads.com/@{}",
}

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")
HEADERS = {"User-Agent": "Mozilla/5.0"}

async def check_url(client, url):
    try:
        response = await client.get(url)

        if response.status_code == 404:
            status = "not_found"
        elif response.status_code in (401, 403, 429):
            status = "blocked"
        elif 200 <= response.status_code < 400:
            status = "exists"
        else:
            status = "error"

        return {"status": status, "http_code": response.status_code}

    except httpx.TimeoutException:
        return {"status": "timeout", "http_code": None}
    except httpx.RequestError:
        return {"status": "error", "http_code": None}

async def check_username(username):
    username = username.strip().lower()

    if not USERNAME_REGEX.fullmatch(username):
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Username inválido"})

    async with httpx.AsyncClient(headers=HEADERS, timeout=5, follow_redirects=True) as client:
        tasks = [check_url(client, url.format(username)) for url in SOCIAL_NETWORKS.values()]
        results = await asyncio.gather(*tasks)

    socials = {}

    for (name, template), result in zip(SOCIAL_NETWORKS.items(), results):
        socials[name] = {"url": template.format(username), **result}

    return {"status": "success", "username": username, "socials": socials}
