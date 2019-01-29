import asyncpg
import re

from aiohttp import web

from .utils import alist, QueryTemplatesReplacer


async def accounts_group(request):
    parsed_params = _parse_params(request.query)
    if parsed_params is None:
        raise web.HTTPBadRequest
    try:
        entries = await alist(_get_entries(request.app['db'], *parsed_params))
    except asyncpg.DataError:
        raise web.HTTPBadRequest
    return web.json_response({'groups': entries})


def _parse_params(params):
    grouping_keys = order = None
    limit = params.get('limit')
    predicates = []
    values = []

    for key, value in params.items():
        if key == 'keys':
            grouping_keys = value
            if not set(grouping_keys.split(',')) <= _ACCEPTED_GROUP_KEYS:
                return None
        elif key == 'order':
            if value == '-1':
                order = 'DESC'
            elif value == '1':
                order = 'ASC'
            else:
                return None
        elif key not in {'query_id', 'limit'}:
            if key in {'likes', 'birth', 'joined'}:
                value = int(value)

            if key == 'likes':
                predicates.append('%s = ANY(likees_ids)')
            elif key == 'interests':
                predicates.append('%s = ANY(interests)')
            else:
                if key in {'joined', 'birth'}:
                    key = f'{key}_year'
                predicates.append(f'{key} = %s')

            values.append(value)

    if not grouping_keys or not order or not limit:
        return None

    return grouping_keys, order, limit, predicates, values


async def _get_entries(db_pool, grouping_keys, order, limit, predicates, values):
    query = f'SELECT {grouping_keys}, COUNT(*) AS count FROM accounts ' \
        f'WHERE {" AND ".join(predicates)} GROUP BY {grouping_keys} ' \
        f'ORDER BY count, {grouping_keys} {order} LIMIT {limit}'
    query = re.sub('%s', QueryTemplatesReplacer(), query)
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            async for row in conn.cursor(query, *values):
                yield dict(row)


_ACCEPTED_GROUP_KEYS = \
    frozenset(('sex', 'status', 'interests', 'country', 'city'))
