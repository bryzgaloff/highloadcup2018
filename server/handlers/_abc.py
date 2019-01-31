import re
from abc import ABCMeta, abstractmethod

from aiohttp import web

from .utils import QueryTemplatesReplacer


class HandlerBase(metaclass=ABCMeta):
    _RESULT_KEY = None

    @classmethod
    async def handle(cls, request):
        parsed_query_args = cls._parse_params(request.query, request.match_info)
        if parsed_query_args is None:
            raise web.HTTPBadRequest

        query, values = cls._prepare_query(*parsed_query_args)
        async with request.app['db'].acquire() as conn:
            async with conn.transaction():
                await cls._run_pre_query_checks(conn, *parsed_query_args)
                entries = cls._get_entries(conn, query, values)
                entries = cls._prepare_entries(entries)
                entries = [entry async for entry in entries]

        if cls._RESULT_KEY is None:
            raise NotImplementedError('_RESULT_KEY should not be None')
        return web.json_response({cls._RESULT_KEY: entries})

    @classmethod
    @abstractmethod
    def _parse_params(cls, query_params, path_params):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _prepare_query(cls, *args):
        raise NotImplementedError

    @classmethod
    async def _get_entries(cls, conn, query, values):
        query = re.sub('%s', QueryTemplatesReplacer(), query)
        async for row in conn.cursor(query, *values):
            yield dict(row)

    @classmethod
    async def _prepare_entries(cls, entries):
        async for entry in entries:
            if 'premium_start' in entry:
                entry['premium'] = {
                    'start': entry.pop('premium_start'),
                    'finish': entry.pop('premium_finish'),
                }
            yield entry

    @classmethod
    async def _run_pre_query_checks(cls, conn, *args):
        return
