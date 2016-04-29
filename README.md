# Flask JSONDash

Instant configurable, chart dashboards from any arbitrary API endpoint. JSON config only. Ready to go.

This project is a flask app, backed by mongodb, that saves JSON configurations for declaring arbitrary charts, templates and iframes, and uses any arbitrary json endpoint, so long as the data format is correct.

Styles and chart layout is pre-packaged, and provides only the bare essentials, while getting out of the way.

## Example configuration

Below is a very complicated configuration that can demonstrate all the types that are supported:

```json
{
    "date" : "2015-12-28T00:39:04.209Z",
    "name": "basic-view-001",
    "gutters": 5,
    "modules": [
        {
            "type": "timeseries",
            "name": "name3",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        },
        {
            "type" : "iframe"
            "name" : "sparklines1",
            "height" : 200,
            "width" : 400,
            "dataSource": "/examples/inline-sparklines.html",
        },
        {
            "type" : "timeline"
            "name" : "timeline",
            "height" : 500,
            "width" : 1000,
            "dataSource" : "http://localhost:5001/timeline/",
        },
        {
            "type": "pie",
            "name": "name4",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        },
        {
            "type": "iframe",
            "name": "hexbin1",
            "width": 600,
            "height": 400,
            "dataSource": "/examples/inline-chart-hexbin.html"
        },
        {
            "type": "iframe",
            "name": "inline1",
            "width": 600,
            "height": 400,
            "dataSource": "/examples/inline-chart.html"
        },
        {
            "type": "custom",
            "name": "tabsthing",
            "width": 510,
            "height": 400,
            "dataSource": "/examples/tabbed-widget.html"
        },
        {
            "type": "line",
            "name": "name5",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        },
        {
            "type": "step",
            "name": "name6",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        },
        {
            "type": "bar",
            "name": "name7",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        },
        {
            "type": "table",
            "name": "name8",
            "width": 510,
            "height": 400,
            "dataSource": "http://localhost:5001/test1"
        }
    ]
}
```

As you can see, each chart is very straightforward. Most of the power is leveraged by the various charting libraries.

## Usage

### Setting environment variables.

Make sure the following env vars are set:

* *CHARTS_DB_HOST* - The DB server hostname (defaults to 'localhost')
* *CHARTS_DB_PORT* - The DB server port (defaults to 27017)
* *CHARTS_DB_NAME* - The DB database name (defaults to 'charts')
* *CHARTS_DB_TABLE* The DB collection name (or sql table name) (defaults to 'views')
* *CHARTS_ACTIVE_DB* The DB backend to use - options: 'mongo', 'postgres' (defaults to 'mongo')

Make sure to start so json configuration can be saved.

### Starting DB

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
