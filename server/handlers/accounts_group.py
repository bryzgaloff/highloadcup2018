import asyncpg
from aiohttp import web

from ._abc import HandlerBase


class AccountsGroupHandler(HandlerBase):
    _RESULT_KEY = 'groups'

    @classmethod
    async def handle(cls, request, **_):
        try:
            return await super().handle(request)
        except asyncpg.DataError:
            raise web.HTTPBadRequest

    @classmethod
    def _parse_params(cls, query_params, _):
        grouping_keys = order = None
        limit = query_params.get('limit')
        predicates = []
        values = []

        for key, value in query_params.items():
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

    @classmethod
    def _prepare_query(cls, grouping_keys, order, limit, predicates, values):
        where_clause = f'WHERE {" AND ".join(predicates)}' if predicates else ''
        query = f'SELECT {grouping_keys}, COUNT(*) AS count FROM accounts ' \
            f'{where_clause} GROUP BY {grouping_keys} ' \
            f'ORDER BY count, {grouping_keys} {order} LIMIT {limit}'
        return query, values


_ACCEPTED_GROUP_KEYS = \
    frozenset(('sex', 'status', 'interests', 'country', 'city'))
