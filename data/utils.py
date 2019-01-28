from operator import itemgetter
from datetime import datetime, date


def account_json_to_db_row(account):
    return (
        account['id'],
        *_extract_email_info(account['email']),
        account.get('fname'),
        account.get('sname'),
        *_extract_phone_info(account.get('phone')),
        account['sex'],
        *_unfold_date(account, 'birth'),
        account.get('country'),
        account.get('city'),
        *_unfold_date(account, 'joined'),
        account['status'],
        account.get('interests', []),
        *_unfold_premium_dates(account.get('premium')),
        list(map(itemgetter('id'), account.get('likes', ()))),
    )


def _extract_email_info(email):
    try:
        domain = email.split('@')[1]
    except IndexError:
        domain = None
    return email, domain


def _extract_phone_info(phone):
    if phone is None:
        return None, None
    try:
        code = phone.split('(')[1].split(')')[0]
    except IndexError:
        code = None
    return phone, code


def _unfold_premium_dates(premium):
    if premium is None:
        return None, None
    values = premium['start'], premium['finish']
    return map(datetime.fromtimestamp, values)


def _unfold_date(account, field):
    timestamp = account[field]
    return timestamp, datetime.fromtimestamp(timestamp).date().year


def likes_to_row(account):
    if 'likes' not in account:
        return
    for like in account['likes']:
        yield (
            account['id'],
            like['id'],
            datetime.fromtimestamp(like['ts']),
        )
