# Flask JSONDash

Instant configurable, chart dashboards from any arbitrary API endpoint. JSON config only. Ready to go.

This project is a [flask blueprint](http://flask.pocoo.org/docs/0.10/blueprints/) that allows you to create sleek dashboards without writing any front end code. It saves JSON configurations for declaring arbitrary charts, leveraging popular libraries like C3.js and D3.js. It also supports templates and iframes, as well as other data visualization libraries. The beauty is that it simply requires a very basic configuration and uses any arbitrary json endpoint to get data, so long as the payload format is correct.

The dashboard layout and blueprint styles are pre-packaged, and provide only the essentials, while getting out of the way.

## Example configuration

Each chart is very straightforward. Most of the power is leveraged by the various charting libraries.

The [example json configuration](example.json) a very complicated example that can demonstrate all kinds of types that are supported.

## Usage

### Requirements

### Core

* Flask
* Jinja2

### Javascript/CSS

These are not included, as you are likely going to have them yourself. If you don't, you'll need to add them:

* Jquery (JS)
* Bootstrap (CSS/JS)

These are necessary and included, based simply on the likelihood they may not alread be used:

* JRespond (JS)
* SugarJS (JS)
* Freewall (JS)

### Charts

Chart requirements depend on what you want to expose to your users. You can configure these in the CHARTS_CONFIG dictionary in the `settings.py` file. You can override these settings by adding your own file, called `settings_override.py`

### Setting environment variables.

Make sure the following env vars are set:

* *CHARTS_DB_HOST* - The DB server hostname (defaults to 'localhost')
* *CHARTS_DB_PORT* - The DB server port (defaults to 27017)
* *CHARTS_DB_NAME* - The DB database name (defaults to 'charts')
* *CHARTS_DB_TABLE* The DB collection name (or sql table name) (defaults to 'views')
* *CHARTS_ACTIVE_DB* The DB backend to use - options: 'mongo', 'postgres' (defaults to 'mongo')

### Starting DB

Make sure to start so json configuration can be saved.

#### Mongodb

Start however you'd like, but usually `mongod` will work.

#### Postgresql

Start however you'd like, but usually `postgres -D /path/to/data/` will work.

### Starting flask app

Either import and use the blueprint in your own flask app, or run `app.py` directly to start the app as-is.

### Starting the test server

Run `endpoints.py` if you'd like to test out existing endpoints to link your chart json to.

### Using remote AJAX endpoints

See `endpoints.py` for examples on how to achieve this. If you do not allow CORS on the server-side, all ajax requests will fail.

## FAQs

**Q**: "Why'd you choose to expose library X, Y, or Z?"

*A*: I tried to go for libraries that are pretty widely known and popular. If you are dissastisfied with what's exposed, you can always add your own by embeddding any js/css and html in a template, and loading it through the `iframe` option.
