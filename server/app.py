import argparse

import asyncpg
from aiohttp import web

from .handlers import *

PG_CREDS = dict(user='postgres', database='hlcup18')


async def init_app():
    accounts_app = web.Application()
    accounts_app.add_routes([
        web.get('/filter/', AccountsFilterHandler.handle),
        web.get('/group/', AccountsGroupHandler.handle),
        web.get('/{account_id}/recommend/', AccountsRecommendHandler.handle),
    ])
    accounts_app.cleanup_ctx.append(_db_pool)

    app = web.Application()
    app.add_subapp('/accounts/', accounts_app)

    return app


async def _db_pool(app):
    pool = asyncpg.create_pool(**PG_CREDS)
    await pool.__aenter__()
    app['db'] = pool
    yield
    await pool.__aexit__()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path')
    args = parser.parse_args()

    web.run_app(init_app(), path=args.path)
