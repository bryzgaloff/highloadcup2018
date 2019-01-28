import asyncpg
from aiohttp import web

from .handlers import *

PG_CREDS = dict(user='postgres', database='hlcup18')


async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/accounts/filter/', accounts_filter),
    ])
    app['db'] = await asyncpg.create_pool(**PG_CREDS).__aenter__()
    app.on_cleanup.append(_close_db_pool)
    return app


async def _close_db_pool(app):
    await app['db'].__aexit__()

if __name__ == '__main__':
    web.run_app(init_app(), port=80)
