import pytest
import jwt
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4

pytestmark = pytest.mark.asyncio


async def test_film_views_not_auth(make_json_request):
    url = '/api/v1/events/film/views'
    params = {
        'film_id': str(uuid4()),
        'timestamp': 1
    }
    response = await make_json_request(url=url, params=params)

    assert response.status == HTTPStatus.FORBIDDEN


async def test_film_views_auth_not_valid(make_json_request):
    url = '/api/v1/events/film/views'
    params = {
        'film_id': str(uuid4()),
        'timestamp': 1
    }
    auth_token = 'not valid token'

    response = await make_json_request(url=url, params=params, auth_token=auth_token)

    assert response.status == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize(
    'sub, exp, status',
    [
        (str(uuid4()), int(datetime.now().timestamp() + 1000), HTTPStatus.OK),
        (str(uuid4()), int(datetime.now().timestamp() - 1000), HTTPStatus.FORBIDDEN),
        (None, int(datetime.now().timestamp() + 1000), HTTPStatus.FORBIDDEN),
        (str(uuid4()), None, HTTPStatus.FORBIDDEN),
    ]
)
async def test_film_views_auth_payload(make_json_request, sub, exp, status):
    url = '/api/v1/events/film/views'
    params = {
        'film_id': str(uuid4()),
        'timestamp': 1
    }
    payload = {
        'sub': sub,
        'exp': exp
    }
    auth_token = jwt.encode(payload, "secret", algorithm="HS256")

    response = await make_json_request(url=url, params=params, auth_token=auth_token)

    assert response.status == status


@pytest.mark.parametrize(
    'film_id, timestamp, status',
    [
        (str(uuid4()), 11, HTTPStatus.OK),
        (str(uuid4()), 'ss', HTTPStatus.UNPROCESSABLE_ENTITY),
        (str(uuid4()), None, HTTPStatus.UNPROCESSABLE_ENTITY),
        (11, 11, HTTPStatus.UNPROCESSABLE_ENTITY),
        ('dd', 11, HTTPStatus.UNPROCESSABLE_ENTITY),
        (None, 11, HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
async def test_film_views_auth_params(make_json_request, film_id, timestamp, status):
    url = '/api/v1/events/film/views'
    params = {}
    if film_id is not None:
        params['film_id'] = film_id
    if timestamp is not None:
        params['timestamp'] = timestamp
    payload = {
        'sub': str(uuid4()),
        'exp': int(datetime.now().timestamp() + 1000)
    }
    auth_token = jwt.encode(payload, "secret", algorithm="HS256")

    response = await make_json_request(url=url, params=params, auth_token=auth_token)

    assert response.status == status
