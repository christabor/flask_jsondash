"""This is an example app, demonstrating usage."""

import os

from flask import Flask

from flask_jsondash.charts_builder import charts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.config.update(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=True,
    JSONDASH_GLOBAL_USER='global',
)
app.debug = True
app.register_blueprint(charts)


def _can_edit_global():
    return True


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
    static=dict(
        js_path='js/vendor/',
        css_path='css/vendor/',
    ),
    auth=dict(
        edit_global=_can_edit_global,
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
