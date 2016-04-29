"""Flask WTForm models."""

import json

from flask_wtf import Form
from wtforms import (
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    TextField,
    BooleanField,
)
from wtforms.validators import DataRequired


class DashbordForm(Form):
    """A form for creating new dashboards."""

    name = TextField(u'View name', validators=[DataRequired()])
