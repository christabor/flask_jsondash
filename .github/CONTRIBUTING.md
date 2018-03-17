## Filing issues

### Requirements

1. Please be as detailed as possible and provide plenty of context.
2. Please use as many relevant labels as necessary to ensure work is properly categorized.

## Contributing

### A couple requirements:

1. Where appropriate (all python code) unit tests are required. JS unit tests are encouraged but at the moment are not well instrumented.
2. Coverage must meet or exceed percentage set in the tox file (usually 98%)
3. Massive changes should be proposed as issues before any work is done (e.g. I don't like jquery - let's switch to X will be closed if a PR is submitted without discussion).
4. Create a README.md with as much useful info as possible in your services module (e.g. `/services/<SERVICE>/README.md`)

### If adding new chart types, examples, etc... you must:

1. Provide example configurations to load the dashboard.
2. Provide example endpoints to pull data from (that correspond to the configuration in 1.) or:
3. Provide example raw data (as json) if no endpoints are specified
4. Ensure all configurations are validated as a correct schema (the tool does this automatically when editing via "raw json" mode).

**Adding** new charts - tips for integration:

1. Add you chart config in the `settings.py` file.
2. Add your handler in `handlers.js`
3. Reference the handler in the `app.js` code.
4. Add example endpoint as needed.
5. Add local library to the example app, and add remote urls for CDN (cdnjs works great.) in the config.
6. Ensure it works and all assets are available.

Then add the requirements above to ensure everything is complete.
