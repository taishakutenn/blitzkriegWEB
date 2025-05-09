import base64
import re
import zlib
import asyncio
import aiohttp
import requests
from math import floor
from app.request_data import request_data_get, request_data_post

headers = {"User-Agent": ""}


def decode_level(level_data: str, is_official_level: bool) -> str:
    if is_official_level:
        level_data = 'H4sIAAAAAAAAA' + level_data
    base64_decoded = base64.urlsafe_b64decode(level_data.encode())
    # window_bits = 15 | 32 will autodetect gzip or not
    decompressed = zlib.decompress(base64_decoded, 15 | 32)
    return decompressed.decode()


def dict_from_string(line: str, sep: str) -> dict:
    line = line.split(sep)
    return dict(zip(line[::2], line[1::2]))


async def find_lvl(lvl_string):
    url = "http://www.boomlings.com/database/getGJLevels21.php"
    data = {
        "str": str(lvl_string),
        "type": 0,
        "secret": "Wmfd2893gb7",
    }
    async with aiohttp.ClientSession() as session:
        lined_text = await request_data_post(url, data, headers, session)
        lined_text = lined_text.split('#')
        levels = lined_text[0].split('|')
        if levels == ['-1']:
            return None
        creators = lined_text[1].split('|')
        creators_dicts = {}
        for creator in creators:
            info = creator.split(':')
            creators_dicts[info[0]] = info[1]
        info = levels[0].split(':')
        info = dict(zip(info[::2], info[1::2]))
        difficulties = 'https://gdbrowser.com/assets/difficulties/{}.png?'
        if info['17']:
            diff = {'3': ['Easy demon', difficulties.format('demon-easy')],
                    '4': ['Medium demon', difficulties.format('demon-medium')],
                    '0': ['Hard demon', difficulties.format('demon-hard')],
                    '5': ['Insane demon', difficulties.format('demon-insane')],
                    '6': ['Extreme demon', difficulties.format('demon-extreme')]}[info['43']]
        else:
            diff = {'0': ['Unrated', difficulties.format('unrated')],
                    '10': ['Easy', difficulties.format('easy')],
                    '20': ['Normal', difficulties.format('normal')],
                    '30': ['Hard', difficulties.format('hard')],
                    '40': ['Harder', difficulties.format('harder')],
                    '50': ['Insane', difficulties.format('insane')]}[info['9']]
        if int(info['13']) <= 7:
            version = float(f'1.{int(info['13']) - 1}')
        elif int(info['13']) == 10:
            version = 1.7
        else:
            version = int(info['13']) / 10
        if int(info['35']):
            song = info['35']
        else:
            song = [
                       'Stereo Madness', 'Back On Track', 'Polargeist', 'Dry Out', 'Base After Base', "Can't Let Go",
                       'Jumper', 'Time Machine', 'Cycles', 'xStep', 'Clutterfunk', 'Theory of Everything',
                       'Electroman Adventures', 'Clubstep', 'Electrodynamix', 'Hexagon Force', 'Blast Processing',
                       'Theory of Everything 2', 'Geometrical Dominator', 'Deadlocked', 'Fingerdash', 'Dash'
                   ][int(info['12'])] + ' (нет на newgrounds)'
        return {'id': info['1'],
                'title': info['2'],
                'creator': creators_dicts[info['6']],
                'difficulty': diff,
                'song': song,
                'version': version,
                'length': ['tiny', 'short', 'medium', 'long', 'xl', 'plat'][int(info['15'])],
                'description': base64.b64decode(info['3']).decode('ASCII'),
                'copyID': info['30'] if '30' in info.keys() else None}


async def get_blitzkrieg(lvl_id):
    data = {"levelID": str(lvl_id), "secret": "Wmfd2893gb7"}
    url = "http://www.boomlings.com/database/downloadGJLevel22.php"
    async with aiohttp.ClientSession() as session:
        level = await request_data_post(url, data, headers, session)
        level = dict_from_string(level, ':')

        level_id = level['1']
        level_name = level['2']
        level_hash = level['4']

        start_poses = []
        all_obj = []

        if level_hash.startswith('H4sI'):
            for obj in re.split(';', decode_level(level_hash, False)):
                if '_' not in obj:
                    objProp = obj.split(',')
                    if len(objProp) > 1:
                        all_obj.append(dict_from_string(obj, ','))
                        if objProp[1] == '31':
                            start_poses.append(dict_from_string(obj, ','))

        max_x = float(max(all_obj, key=lambda x: float(x['2']))['2']) + 340
        start_poses = sorted([floor(float(start_pos['2']) / max_x * 100) for start_pos in start_poses])

        start_poses.insert(0, 0)
        start_poses.append(100)

        table = []
        for stage in range(1, len(start_poses)):
            table.append([False] + [[f'{p1} - {p2}', False]
                                    for p1, p2 in list(zip(start_poses[:-stage:], start_poses[stage::]))[::-1]])
        return table


if __name__ == '__main__':
    pass
