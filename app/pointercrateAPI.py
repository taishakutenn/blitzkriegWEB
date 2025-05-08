import asyncio
import aiohttp
from request_data import request_data


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


async def get_lvl(lvl_id):
    url = 'https://pointercrate.com/api/v2/demons/listed/'
    async with aiohttp.ClientSession() as session:
        demon = await request_data(url, {'level_id': lvl_id}, session)
        print(demon)
        if demon:
            demon = demon[0]
            if demon['verifier']['name'][0] == '[':
                demon['verifier']['name'] = demon['verifier']['name'].split(' ', 1)[1]
            return demon
        return None


if __name__ == '__main__':
    print(asyncio.run(get_lvl(86407629)))
