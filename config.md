# Core configuration schema

This documents all options available for the configuration schema use to power jsondash.

And of course, [you can always check out examples here](examples/config).

(Note: :heavy_exclamation_mark: = required, :no_entry_sign: = not user specified, :heavy_check_mark: = optional)

**date** - [*String/Date*] / auto-generated :no_entry_sign:

The date for the schema. This is automatically generated, so you don't need to edit it.

**name** - [*String*] / :heavy_exclamation_mark:

The date for the schema. This is automatically generated, so you don't need to edit it.

**modules** - [*Array of object*s] / :heavy_exclamation_mark:

This is a list of objects that corresponds to each chart.

```json
{
    "modules": [{}]
}
```

**modules**:**name** - [*String*] / :heavy_exclamation_mark:

The name of the chart - this is used in the title.

**modules**:**height** - [*String/Number*] / :heavy_exclamation_mark:

The height of the chart in pixels.

**modules**:**width** - [*String/Number*] / :heavy_exclamation_mark:

The width of the chart in pixels.

**modules**:**dataSource** - [*String*] / :heavy_exclamation_mark:

The API endpoint to get data from.

**modules**:**override** - [*Boolean*] / :heavy_check_mark:

Whether to allow overrides for the constructor (for passing in custom options). This is available on a per-library basis. See [schemas.md](schemas.md) for which charting libraries support it.

**modules**:**refresh** - [*Boolean*] / :heavy_check_mark:

Whether or not to allow refreshing this chart.

**modules**:**refreshInterval** - [*Number*] / :heavy_check_mark:

If `refresh` is true, The number of milliseconds before refreshing this chart. This will continuously refresh so use with caution for best performance/experience.

**modules**:**guid** - [*String*] / auto-generated :no_entry_sign:

The DOM id of this chart.

**modules**:**type** - [*String*] / :heavy_check_mark:

The type of chart. This is typically handled by the charting UI when adding charts, but it can be overriden manually.
