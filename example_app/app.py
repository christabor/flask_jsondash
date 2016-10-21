"""This is your typical app, demonstrating usage."""

import os

from flask_jsondash.charts_builder import charts

from flask import (
    Flask,
    session,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.config.update(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=False,
    JSONDASH_GLOBAL_USER='global',
)
app.debug = True
app.register_blueprint(charts)


def _can_delete():
    return True


def _can_clone():
    return True


def _get_username():
    return 'anonymous'


# Config examples.
app.config['JSONDASH'] = dict(
    metadata=dict(
        created_by=_get_username,
        username=_get_username,
    ),
    # static=dict(
    #     js_path='js/vendor/',
    #     css_path='css/vendor/',
    # ),
    auth=dict(
        clone=_can_clone,
        delete=_can_delete,
    )
)


@app.route('/', methods=['GET'])
def index():
    """Sample index."""
    return '<a href="/charts">Visit the charts blueprint.</a>'


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 5002))
    app.run(debug=True, port=PORT)
