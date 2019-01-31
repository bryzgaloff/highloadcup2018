from aiohttp import web

from data.now import now
from ._abc import HandlerBase


class AccountsRecommendHandler(HandlerBase):
    _RESULT_KEY = 'accounts'

    @classmethod
    def _parse_params(cls, query_params, path_params):
        try:
            account_id = path_params['account_id']
            limit = query_params['limit']
        except KeyError:
            return None

        country = city = None
        for key, value in query_params.items():
            if key == 'country':
                country = value
            elif key == 'city':
                city = value
            elif key not in {'limit', 'query_id'}:
                return None

        return account_id, country, city, limit

    @classmethod
    def _prepare_query(cls, account_id, country, city, limit):
        values = []
        where_clause = ''
        if country is not None:
            where_clause = f'WHERE country = %s'
            values.append(country)
        if city is not None:
            if not where_clause:
                where_clause = 'WHERE '
            else:
                where_clause += ' AND '
            where_clause += f'city = %s'
            values.append(city)

        query = f'''
            SELECT
                id, email, status, fname, sname, birth,
                premium_start, premium_finish
            FROM (
                SELECT
                    interests, birth_year,
                    CASE WHEN sex = 'm' THEN 'f'
                         ELSE 'm' END AS opposite_sex
                FROM accounts
                WHERE id = {account_id}) AS source
            JOIN accounts
                ON accounts.sex = source.opposite_sex
                    AND accounts.interests && source.interests
            {where_clause}
            ORDER BY
                premium_start <= %s AND %s <= premium_finish DESC,
                CASE WHEN status = 'свободны' THEN 0
                     WHEN status = 'заняты' THEN 2
                     ELSE 1 END ASC,
                array_length(array_intersect(
                    source.interests, accounts.interests
                ), 1) DESC,
                ABS(source.birth_year - accounts.birth_year) ASC
            LIMIT {limit}
        '''
        values.extend((now, now))

        return query, values

    @classmethod
    async def _run_pre_query_checks(cls, conn, account_id, *_):
        query = f'SELECT 1 FROM accounts WHERE id = {account_id}'
        if await conn.fetchval(query) is None:
            raise web.HTTPNotFound
