async def request_data(url, params, session):
    async with session.get(url, params=params) as resp:
        return await resp.json()