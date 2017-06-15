# Contributing

## A couple requirements:

1. Where appropriate (all python code) unit tests are required. JS unit tests are encouraged but at the moment are not well instrumented.
2. Coverage must meet or exceed percentage set in the tox file (usually 98%)
3. Massive changes should be proposed as issues before any work is done (e.g. I don't like jquery - let's switch to X will be closed if a PR is submitted without discussion).

## If adding new chart types, examples, etc... you must:

1. Provide example configurations to load the dashboard.
2. Provide example endpoints to pull data from (that correspond to the configuration in 1.) or:
3. Provide example raw data (as json) if no endpoints are specified
4. Ensure all configurations are validated as a correct schema (the tool does this automatically when editing via "raw json" mode).
