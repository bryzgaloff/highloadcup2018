class QueryTemplatesReplacer:
    def __init__(self):
        self._occurrence_no = 0

    def __call__(self, match):
        self._occurrence_no += 1
        return f'${self._occurrence_no}'


async def alist(async_gen):
    """ :type async_gen: typing.AsyncGenerator """
    return [item async for item in async_gen]
