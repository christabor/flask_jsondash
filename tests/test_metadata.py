import pytest

from flask_jsondash import charts_builder


@pytest.mark.auth
@pytest.mark.metadata
def test_auth_true_fakeauth(ctx, client):
    app, test = client
    assert charts_builder.auth(authtype=None)
    assert charts_builder.auth(authtype='foo')
    assert charts_builder.metadata(key='foo') is None


@pytest.mark.metadata
def test_metadata(ctx, client):
    app, test = client
    assert charts_builder.metadata() == dict(
        username='Username',
        created_by='Username',
    )
    assert charts_builder.metadata(key='username') == 'Username'
    assert charts_builder.metadata(key='created_by') == 'Username'


@pytest.mark.metadata
def test_metadata_exclude(ctx, client):
    app, test = client
    assert charts_builder.metadata() == dict(
        username='Username',
        created_by='Username',
    )
    assert charts_builder.metadata(exclude='created_by') == dict(
        username='Username'
    )
    assert charts_builder.metadata(exclude='username') == dict(
        created_by='Username'
    )
