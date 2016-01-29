from flask import Flask
from charts_builder import charts

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.debug = True

app.register_blueprint(charts)


if __name__ == '__main__':
    app.run(debug=True)
