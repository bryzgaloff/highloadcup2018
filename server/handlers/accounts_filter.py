import re

from aiohttp import web

from server.handlers.utils import QueryTemplatesReplacer, alist


async def accounts_filter(request):
    parsed_query_args = _parse_filter_conditions(request.query)
    if parsed_query_args is None:
        raise web.HTTPBadRequest
    entries = await alist(_get_entries(
        request.app['db'], *parsed_query_args, request.query['limit']
    ))
    return web.json_response(entries)


def _parse_filter_conditions(params):
    predicates = []
    values = []
    fields = set()

    for key, value in params.items():
        if key in {'limit', 'query_id'}:
            continue

        try:
            field, predicate = key.split('_')
        except ValueError:
            return None

        if field not in {'interests', 'likes'}:
            fields.add(field)

        if predicate == 'null':
            if field not in _NULL_CHECK_FIELDS or value not in {'0', '1'}:
                return None
            if field == 'premium':
                field = 'premium_start'
            not_ = 'NOT' if value == '0' else ''
            predicates.append(f'{field} IS {not_} NULL')
            continue

        try:
            expression = _PREDICATES_TO_SQL[field][predicate]
        except KeyError:
            return None
        predicates.append(expression)

        if predicate == 'now':
            continue

        if field == 'birth':
            value = int(value)
        elif predicate in {'contains', 'any'}:
            value = value.split(',')
        values.append(value)

    return predicates, values, fields


async def _get_entries(db_pool, predicates, values, fields, limit):
    query = f'SELECT {",".join(fields)} FROM accounts ' \
        f'WHERE {" AND ".join(predicates)} LIMIT {limit}'
    query = re.sub('%s', QueryTemplatesReplacer(), query)
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            async for row in conn.cursor(query, *values):
                yield dict(row)


_NULL_CHECK_FIELDS = \
    frozenset(('fname', 'sname', 'phone', 'country', 'city', 'premium'))
_PREDICATES_TO_SQL = {
    'sex': {
        'eq': 'sex = %s',
    },
    'email': {
        'domain': 'email_domain = %s',
        'lt': 'email < %s',
        'gt': 'email > %s',
    },
    'status': {
        'eq': 'status = %s',
        'neq': 'status <> %s',
    },
    'fname': {
        'eq': 'fname = %s',
        'any': 'fname IN (%s)',
    },
    'sname': {
        'eq': 'sname = %s',
        'starts': 'sname LIKE %%s'
    },
    'phone': {
        'code': 'phone_code = %s',
    },
    'country': {
        'eq': 'country = %s',
    },
    'city': {
        'eq': 'city = %s',
        'any': 'city IN (%s)',
    },
    'birth': {
        'lt': 'birth < %s',
        'gt': 'birth > %s',
        'year': 'birth_year = %s',
    },
    'interests': {
        'contains': 'interests @> %s',
        'any': 'interests && %s',
    },
    'likes': {
        'contains': 'likees_ids @> %s',
    },
    'premium': {
        'now': 'now() BETWEEN premium_start AND premium_finish',
    },
}
