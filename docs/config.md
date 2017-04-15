# Core configuration schema

This documents all options available for the configuration schema use to power jsondash.

And of course, [you can always check out examples here](example_app/examples/config).

(Note: :heavy_exclamation_mark: = required, :no_entry_sign: = not user specified, :heavy_check_mark: = optional)

**layout** - [*Stringe*] / auto-generated :no_entry_sign:

The type of layout - either "freeform" or "grid". This is automatically generated, so you don't need to edit it.

**date** - [*String/Date*] / auto-generated :no_entry_sign:

The date for the schema. This is automatically generated, so you don't need to edit it.

**name** - [*String*] :heavy_exclamation_mark:

The name of the dashboard.

**modules** - [*Array of Object*s] :heavy_exclamation_mark:

This is a list of objects that corresponds to each chart.

```json
{
    "modules": [{}]
}
```

**modules**:**name** - [*String*] :heavy_exclamation_mark:

The name of the chart - this is used in the title.

**modules**:**height** - [*String/Number*] :heavy_exclamation_mark:

The height of the chart in pixels.

**modules**:**width** - [*String/Number*] :heavy_exclamation_mark:

The width of the chart in pixels.

**modules**:**row** - [*Number*] :heavy_check_mark:

The row which the chart resides in. This is only relevant if `"layout": "grid"` is specified for the dashboard.

**modules**:**order** - [*Number*] :heavy_check_mark:

The order of the chart in the layout. Best effort will be made to ensure layout ordering if these are specified, but in some cases, the layout packing algorithm may order things slightly different for optimal space filling.

For optimal results, make all your charts the same size or maintain a reasonably similar aspect ratio.

**modules**:**dataSource** - [*String*] :heavy_exclamation_mark:

The API endpoint to get data from.

**modules**:**override** - [*Boolean*] :heavy_check_mark:

Whether to allow overrides for the constructor (for passing in custom options). This is available on a per-library basis. See [schemas.md](schemas.md) for which charting libraries support it.

**modules**:**refresh** - [*Boolean*] :heavy_check_mark:

Whether or not to allow refreshing this chart.

**modules**:**refreshInterval** - [*Number*] :heavy_check_mark:

If `refresh` is true, The number of milliseconds before refreshing this chart. This will continuously refresh so use with caution for best performance/experience.

**modules**:**guid** - [*String*] / auto-generated :no_entry_sign:

The DOM id of this chart.

**modules**:**family** - [*String*] auto-generated :no_entry_sign:

The family this chart belongs to. This is generated when saving new modules and is used to optimize the number of static assets loaded on a page. *Note*: if you if edit this manually, it must be set on **all** modules, otherwise some will fail.

**modules**:**type** - [*String*] :heavy_check_mark:

The type of chart. This is typically handled by the charting UI when adding charts, but it can be overriden manually.

**modules**:**inputs** - [*Object*] :heavy_check_mark:

An object specifying a form and user inputs to use for optional filtering/interactivity with a given chart.

Example inputs configuration [can be found here](https://github.com/christabor/flask_jsondash/blob/master/example_app/examples/config/inputs.json).

**modules**:**inputs**:**btn_classes** [*Array of Strings*] :heavy_check_mark:

The button classes to apply to this chart's form.

**modules**:**inputs**:**submit_text** [*String*] :heavy_check_mark:

The button text to apply to this chart's form.

**modules**:**inputs**:**options** [*Array of Objects*] :heavy_check_mark:

The list of inputs for this chart's form. E.g:

```json
{
    "modules": [
        {
            "inputs": {
                "options": [{}]
            }
        }
    ]
}
```

**modules**:**inputs**:**options**:**type** [*String*] :heavy_check_mark:

The input type. Acceptable values are `number`, `select`, `radio`, `checkbox`, `text`, `password` and all html5 input types.

*Note on select* the `select` type (corresponding to a dropdown), you will need to specify `options`, which is an array of arrays., where the first index is the value, and the second index is the name displayed - e.g:

```json
{
    "type": "select",
    "options": [
        [10, "Show 10 items"],
        [20, "Show 20 items"]
    ]
}
```

*Note on radio*

Same format as the select type - an array of arrays.

```json
{
    "type": "radio",
    "options": [
        [10, "Show 10 items"],
        [20, "Show 20 items"]
    ]
}
```

*Note on checkbox*

Same format as above, but your default should be true or false.

```json
{
    "type": "checkbox",
    "default": true,
    "label": "Launch missiles?"
}
```

**modules**:**inputs**:**options**:**name** [*String*] :heavy_check_mark:

The `<input name="">` attribute for the form.

**modules**:**inputs**:**options**:**default** [*Mixed*] :heavy_check_mark:

The `<input value="">` attribute for the form.

**modules**:**inputs**:**options**:**placeholder** [*String*] :heavy_check_mark:

The `<input placeholder="">` attribute for the form.

**modules**:**inputs**:**options**:**validator_regex** [*Regex*] :heavy_check_mark:

The `<input pattern="">` attribute for the form for custom validation. This will only work with javascript friendly regular expressions.

**modules**:**inputs**:**options**:**input_classes** [*Array of Strings*] :heavy_check_mark:

The classes to apply to this input.

**modules**:**inputs**:**options**:**label** [*String*] :heavy_check_mark:

The `<label>` text for this input.

**modules**:**inputs**:**options**:**help_text** [*String*] :heavy_check_mark:

The small, subdued text used as a helper description for this input.
