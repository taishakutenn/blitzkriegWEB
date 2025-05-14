import asyncio
import aiohttp
from app.request_data import request_data_get


async def get_demonlist() -> list[dict]:
    """
    Возвращает список уровней, отсортированных по их позиции в топе.
    Список состоит из словарей формата get_lvl (следующая функция)
    """
    url = 'https://pointercrate.com/api/v2/demons/listed/'

    async with aiohttp.ClientSession() as session:
        tasks = [request_data_get(url, {'limit': 50, 'after': i}, session) for i in range(0, 101, 50)]
        top = []
        for task in asyncio.as_completed(tasks):
            top += await task

    top.sort(key=lambda x: x['position'])
    for demon in top:
        if demon['verifier']['name'][0] == '[':
            demon['verifier']['name'] = demon['verifier']['name'].split(' ', 1)[1]

    return top


async def get_lvl(lvl_id: int or str) -> dict or None:
    """
    Возвращает уровень в формате:
    {
      'id': int (id на серверах pointercrate),
      'position': int,
      'name': str,
      'requirement': int (лист %),
      'video': str (ссылка на прохождение),
      'thumbnail': str (ссылка на превью),
      'publisher': {'id': int (pointercrate id), 'name': str, 'banned': bool},
      'verifier': {'id': int (pointercrate id), 'name': str, 'banned': bool},
      'level_id': int (id с серверов GD)
     }
    """
    url = 'https://pointercrate.com/api/v2/demons/listed/'

    async with aiohttp.ClientSession() as session:
        demon = await request_data_get(url, {'level_id': lvl_id}, session)

    if demon:
        demon = demon[0]
        if demon['verifier']['name'][0] == '[':
            demon['verifier']['name'] = demon['verifier']['name'].split(' ', 1)[1]
        return demon
    return None


if __name__ == '__main__':
    pass
