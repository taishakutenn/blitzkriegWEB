"""Вынос конструкции 'async with session' в разные функции для сокращения кода"""


async def request_data_get(url, params, session):
    async with session.get(url, params=params) as resp:
        return await resp.json()


async def request_data_post(url, data, headers, session):
    async with session.post(url, data=data, headers=headers) as resp:
        return await resp.text()
