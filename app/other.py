import asyncio
import aiohttp


async def request_data(url, params, session):
    async with session.get(url, params=params) as resp:
        return await resp.json()


async def get_demonlist():
    url = 'https://pointercrate.com/api/v2/demons/listed/'
    async with aiohttp.ClientSession() as session:
        tasks = [request_data(url, {'limit': 50, 'after': i}, session) for i in range(0, 101, 50)]
        top = []
        for task in asyncio.as_completed(tasks):
            top += await task
        top.sort(key=lambda x: x['position'])
        for demon in top:
            if demon['verifier']['name'][0] == '[':
                demon['verifier']['name'] = demon['verifier']['name'].split(' ', 1)[1]
        return top
