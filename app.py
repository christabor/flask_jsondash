"""This is your typical app, demonstrating usage."""

from charts_builder.charts_builder import charts

from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

app.register_blueprint(charts)


@app.route('/', methods=['GET'])
def index():
    """Sample index."""
    return '<a href="/charts">Visit the charts blueprint.</a>'


if __name__ == '__main__':
    app.run(debug=True, port=5002)
