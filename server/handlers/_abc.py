import re
from abc import ABCMeta, abstractmethod

from aiohttp import web

from .utils import QueryTemplatesReplacer


class HandlerBase(metaclass=ABCMeta):
    _RESULT_KEY = None

    @classmethod
    async def handle(cls, request, **path_params):
        parsed_query_args = cls._parse_params(request.query, path_params)
        if parsed_query_args is None:
            raise web.HTTPBadRequest
        query, values = cls._prepare_query(*parsed_query_args)
        entries = cls._get_entries(request.app['db'], query, values)
        result = await cls._prepare_result(entries)
        return web.json_response(result)

    @classmethod
    @abstractmethod
    def _parse_params(cls, query_params, path_params):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _prepare_query(cls, *args):
        raise NotImplementedError

    @classmethod
    async def _get_entries(cls, db_pool, query, values):
        query = re.sub('%s', QueryTemplatesReplacer(), query)
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                async for row in conn.cursor(query, *values):
                    yield dict(row)

    @classmethod
    async def _prepare_result(cls, entries):
        """ Validate and prepare result. """
        if cls._RESULT_KEY is None:
            raise NotImplementedError
        return {cls._RESULT_KEY: [entry async for entry in entries]}
