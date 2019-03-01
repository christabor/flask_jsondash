## Contributing

If you'd like to work on the project, a good place to start is using the example app to develop against. To do this easily, you'll want to setup a virtual environment and setup the package locally, using the `develop` mode of `setuptools`. The below should get you started:

```shell
git clone github.com/christabor/flask_jsondash.git
cd flask_jsondash
virtualenv env
source env/bin/activate
git checkout -b YOUR_NEW_BRANCH
python setup.py develop
cd example_app
python app.py
```

And voila! You can now edit the folder directly, and still use it as a normal pip package without having to reinstall every time you change something.

## Tests

To run all tests for python 2.7 and 3.x, with coverage, just run `tox` (assuming tox is installed.)

### Python

You can run these tests using pytest (`pip install -U pytest`) and then in the existing virtualenv, run `pytest tests`.

If you are having issues with this approach, an alternative would be to install pytest within the projects' virtualenv (assuming you've created one), and then running it like so: `python -m pytest tests`.

#### Test coverage

To find coverage information (assuming `pytest-cov` is installed), you can run: `pytest tests -s --cov=flask_jsondash`.

### Javascript

JS tests are run using the node library Jasmine. To install and run it, you'll need nodejs installed, then the package: `npm install -g jasmine`. You can then `cd` into the `tests_js` folder and run the provided python script `python runner.py`
