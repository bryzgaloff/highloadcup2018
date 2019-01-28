import zipfile
import os
import tempfile
import asyncio
import json
from itertools import chain, tee

import asyncpg

from data.utils import account_json_to_db_row, likes_to_row

PG_CREDS = dict(user='postgres', database='hlcup18')
_DATA_FILE_PATH = os.path.join('/', 'tmp', 'data', 'data.zip')


async def write_data():
    accounts, copy = tee(_load_accounts_data())
    async with asyncpg.create_pool(**PG_CREDS) as pool:
        await asyncio.gather(
            _write_data(pool, 'accounts', accounts, _accounts_mapper),
            _write_data(pool, 'likes', copy, _likes_mapper),
        )


def _load_accounts_data():
    def read_data():
        data_dir = _unzip(_DATA_FILE_PATH)
        for data_file_name in os.listdir(data_dir):
            full_path = os.path.join(data_dir, data_file_name)
            with open(full_path) as data_file:
                data = json.load(data_file)
            yield data['accounts']

    return chain(*read_data())


async def _write_data(pool, table, data, mapper):
    async with pool.acquire() as conn:
        rows = list(mapper(data))
        await conn.copy_records_to_table(table, records=rows)


def _accounts_mapper(accounts_data):
    return map(account_json_to_db_row, accounts_data)


def _likes_mapper(accounts_data):
    return chain(*map(likes_to_row, accounts_data))


def _unzip(data_file_path):
    tempdir = tempfile.mkdtemp()
    with zipfile.ZipFile(data_file_path) as zip_:
        zip_.extractall(tempdir)
    return tempdir


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(write_data())
