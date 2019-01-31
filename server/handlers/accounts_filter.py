from data.now import now
from ._abc import HandlerBase


class AccountsFilterHandler(HandlerBase):
    _RESULT_KEY = 'accounts'

    @classmethod
    def _parse_params(cls, query_params, _):
        predicates = []
        values = []
        fields = {'id', 'email'}

        try:
            limit = query_params['limit']
        except KeyError:
            return None

        for key, value in query_params.items():
            if key in {'limit', 'query_id'}:
                continue

            try:
                field, predicate = key.split('_')
            except ValueError:
                return None

            if field not in {'interests', 'likes'}:
                if field == 'premium':
                    fields.update(('premium_start', 'premium_finish'))
                else:
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

            if field == 'birth':
                value = int(value)
            elif predicate in {'contains', 'any'}:
                value = value.split(',')

            if predicate == 'now':
                values.extend((now, now))
            else:
                values.append(value)

        return predicates, values, fields, limit

    @classmethod
    def _prepare_query(cls, predicates, values, fields, limit):
        query = f'SELECT {",".join(fields)} FROM accounts ' \
                f'WHERE {" AND ".join(predicates)} LIMIT {limit}'
        return query, values


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
        'starts': "sname LIKE '%%s'"
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
        'now': 'premium_start <= %s AND %s <= premium_finish',
    },
}
