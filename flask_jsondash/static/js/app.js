/** global: d3 */
/**
 * Bootstrapping functions, event handling, etc... for application.
 */

var jsondash = function() {
    var my = {
        chart_wall: null
    };
    var MIN_CHART_SIZE   = 200;
    var API_ROUTE_URL    = $('[name="dataSource"]');
    var API_PREVIEW      = $('#api-output');
    var API_PREVIEW_BTN  = $('#api-output-preview');
    var API_PREVIEW_CONT = $('.api-preview-container');
    var WIDGET_FORM      = $('#module-form');
    var VIEW_BUILDER     = $('#view-builder');
    var ADD_MODULE       = $('#add-module');
    var MAIN_CONTAINER   = $('#container');
    var EDIT_MODAL       = $('#chart-options');
    var DELETE_BTN       = $('#delete-widget');
    var DELETE_DASHBOARD = $('.delete-dashboard');
    var SAVE_WIDGET_BTN  = $('#save-module');
    var EDIT_CONTAINER   = $('#edit-view-container');
    var MAIN_FORM        = $('#save-view-form');
    var JSON_DATA        = $('#raw-config');
    var ADD_ROW_CONTS    = $('.add-new-row-container');
    var EDIT_TOGGLE_BTN  = $('[href=".edit-mode-component"]');
    var UPDATE_FORM_BTN  = $('#update-module');
    var CHART_TEMPLATE   = $('#chart-template');
    var ROW_TEMPLATE     = $('#row-template').find('.grid-row');
    var EVENTS           = {
        init:             'jsondash.init',
        edit_form_loaded: 'jsondash.editform.loaded',
        add_widget:       'jsondash.widget.added',
        update_widget:    'jsondash.widget.updated',
        delete_widget:    'jsondash.widget.deleted',
        refresh_widget:   'jsondash.widget.refresh',
        add_row:          'jsondash.row.add',
        delete_row:       'jsondash.row.delete',
        preview_api:      'jsondash.preview',
    }

    /**
     * [Widgets A singleton manager for all widgets.]
     */
    function Widgets() {
        var self = this;
        self.widgets = {};
        self.url_cache = {};
        self.container = MAIN_CONTAINER.selector;
        self.all = function() {
            return self.widgets;
        };
        self.add = function(config) {
            self.widgets[config.guid] = new Widget(self.container, config);
            self.widgets[config.guid].$el.trigger(EVENTS.add_widget);
            return self.widgets[config.guid];
        };
        self.addFromForm = function() {
            return self.add(self.newModel());
        };
        self._delete = function(guid) {
            delete self.widgets[guid];
        };
        self.get = function(guid) {
            return self.widgets[guid];
        };
        self.getByEl = function(el) {
            return self.get(el.data().guid);
        };
        /**
         * [getAllMatchingProp Get widget guids matching a givne propname and val]
         */
        self.getAllMatchingProp = function(propname, val) {
            var matches = [];
            $.each(self.all(), function(i, widg){
                if(widg.config[propname] === val) {
                    matches.push(widg.config.guid);
                }
            });
            return matches;
        };
        /**
         * [getAllOfProp Get all the widgets' config values of a specified property]
         */
        self.getAllOfProp = function(propname) {
            var props = [];
            $.each(self.all(), function(i, widg){
                props.push(widg.config[propname]);
            });
            return props;
        };
        self.getAllOfPropUnless = function(propname, propcheck, val) {
            var props = [];
            $.each(self.all(), function(i, widg){
                if(widg.config[propcheck] !== val) {
                    props.push(widg.config[propname]);
                }
            });
            return props;
        };
        /**
         * [loadAll Load all widgets at once in succession]
         */
        self.loadAll = function() {
            // Don't run this on certain types that are not cacheable (e.g. binary, html)
            var config_urls = self.getAllOfPropUnless('dataSource', 'family', 'Basic');
            var unique_urls = d3.set(config_urls).values();
            var cached = {};
            var proms = [];
            // Build out promises.
            $.each(unique_urls, function(_, url){
                var req = $.ajax({
                    url: url,
                    type: 'GET',
                    dataType: 'json',
                    error: function(error){
                        var matches = self.getAllMatchingProp('dataSource', url);
                        $.each(matches, function(_, guid){
                            var widg = self.get(guid);
                            jsondash.handleRes(error, null, widg.el);
                        });
                    }
                });
                proms.push(req);
            });
            // Retrieve and gather the promises
            $.when.apply($, proms).done(whenAllDone);

            function whenAllDone() {
                $.each(arguments, function(index, prom){
                    var ref_url = unique_urls[index];
                    var data = null;
                    if(ref_url) {
                        data = prom[0];
                        cached[ref_url] = data;
                    }
                });
                // Inject a cached value on the config for use down the road
                // (this is done so little is changed with the architecture of getting and loading).
                for(var guid in self.all()){
                    // Don't refresh, just update config with new key value for cached data.
                    var widg = self.get(guid);
                    var data = cached[widg.config.dataSource];
                    // Grab data from specific `key` key, if it exists (for shared data on a single endpoint).
                    var cachedData = widg.config.key && data.multicharts ? data.multicharts[widg.config.key] : data;
                    widg.update({cachedData: cachedData}, true);
                    // Actually load them all
                    widg.load();
                }
            }
        };
        self.newModel = function() {
            var config = getParsedFormConfig();
            var guid   = jsondash.util.guid();
            config['guid'] = guid;
            if(!config.refresh || !refreshableType(config.type)) {
                config['refresh'] = false;
            }
            return config;
        };
        self.populate = function(data) {
            for(var name in data.modules){
                // Closure to maintain each chart data value in loop
                (function(config){
                    var config = data.modules[name];
                    // Add div wrappers for js grid layout library,
                    // and add title, icons, and buttons
                    // This is the widget "model"/object used throughout.
                    self.add(config);
                })(data.modules[name]);
            }
        };
    }

    function Widget(container, config) {
        // model for a chart widget
        var self = this;
        self.config = config;
        self.guid = self.config.guid;
        self.container = container;
        self._refreshInterval = null;
        self._makeWidget = function(config) {
            if(document.querySelector('[data-guid="' + config.guid + '"]')){
                return d3.select('[data-guid="' + config.guid + '"]');
            }
            return d3.select(self.container).select('div')
                .append('div')
                .classed({item: true, widget: true})
                .attr('data-guid', config.guid)
                .attr('data-refresh', config.refresh)
                .attr('data-refresh-interval', config.refreshInterval)
                .style('width', config.width + 'px')
                .style('height', config.height + 'px')
                .html(d3.select(CHART_TEMPLATE.selector).html())
                .select('.widget-title .widget-title-text').text(config.name);
        };
        // d3 el
        self.el = self._makeWidget(config);
        // Jquery el
        self.$el = $(self.el[0]);
        self.init = function() {
            // Add event handlers for widget UI
            self.$el.find('.widget-refresh').on('click.charts', refreshWidget);
            self.$el.find('.widget-delete').on('click.charts.delete', function(e){
                self.delete();
            });
            // Allow swapping of edit/update events
            // for the edit button and form modal
            self.$el.find('.widget-edit').on('click.charts', function(){
                SAVE_WIDGET_BTN
                .attr('id', UPDATE_FORM_BTN.selector.replace('#', ''))
                .text('Update widget')
                .off('click.charts.save')
                .on('click.charts', onUpdateWidget);
            });
            if(self.config.refresh && self.config.refreshInterval) {
                self._refreshInterval = setInterval(function(){
                    self.load();
                }, parseInt(self.config.refreshInterval, 10));
            }
            if(my.layout === 'grid') {
                updateRowControls();
            }
        };
        self.getInput = function() {
            // Get the form input for this widget.
            return $('input[id="' + self.guid + '"]');
        };
        self.delete = function(bypass_confirm) {
            if(!bypass_confirm){
                if(!confirm('Are you sure?')) {
                    return;
                }
            }
            var row = self.$el.closest('.grid-row');
            clearInterval(self._refreshInterval);
            // Delete the input
            self.getInput().remove();
            self.$el.trigger(EVENTS.delete_widget, [self]);
            // Delete the widget
            self.el.remove();
            // Remove reference to the collection by guid
            my.widgets._delete(self.guid);
            EDIT_MODAL.modal('hide');
            // Redraw wall to replace visual 'hole'
            if(my.layout === 'grid') {
                // Fill empty holes in this charts' row
                fillEmptyCols(row);
                updateRowControls();
            }
            // Trigger update form into view since data is dirty
            EDIT_CONTAINER.collapse('show');
            // Refit grid - this should be last.
            fitGrid();
        };
        self.addGridClasses = function(sel, classes) {
            d3.map(classes, function(colcount){
                var classlist = {};
                classlist['col-md-' + colcount] = true;
                classlist['col-lg-' + colcount] = true;
                sel.classed(classlist);
            });
        };
        self.removeGridClasses = function(sel) {
            var bootstrap_classes = d3.range(1, 13);
            d3.map(bootstrap_classes, function(i){
                var classes = {};
                classes['col-md-' + i] = false;
                classes['col-lg-' + i] = false;
                sel.classed(classes);
            });
        };
        self.update = function(conf, dont_refresh) {
                /**
             * Single source to update all aspects of a widget - in DOM, in model, etc...
             */
            var widget = self.el;
            // Update model data
            self.config = $.extend(self.config, conf);
            // Trigger update form into view since data is dirty
            // Update visual size to existing widget.
            loader(widget);
            widget.style({
                height: self.config.height + 'px',
                width: my.layout === 'grid' ? '100%' : self.config.width + 'px'
            });
            if(my.layout === 'grid') {
                // Extract col number from config: format is "col-N"
                var colcount = self.config.width.split('-')[1];
                var parent = d3.select(widget.node().parentNode);
                // Reset all other grid classes and then add new one.
                self.removeGridClasses(parent);
                self.addGridClasses(parent, [colcount]);
                // Update row buttons based on current state
                updateRowControls();
            }
            widget.select('.widget-title .widget-title-text').text(self.config.name);
            // Update the form input for this widget.
            self._updateForm();

            if(!dont_refresh) {
                self.load();
                EDIT_CONTAINER.collapse();
                // Refit the grid
                fitGrid();
            } else {
                unload(widget);
            }
            $(widget[0]).trigger(EVENTS.update_widget);
        };
        self.load = function() {
            var widg      = my.widgets.get(self.guid);
            var widget    = self.el;
            var $widget   = self.$el;
            var config    = widg.config;
            var inputs    = $widget.find('.chart-inputs');
            var container = $('<div></div>').addClass('chart-container');
            var family    = config.family.toLowerCase();

            widget.classed({error: false});
            widget.select('.error-overlay')
                .classed({hidden: true})
                .select('.alert')
                .text('');

            loader(widget);

            try {
                // Cleanup for all widgets.
                widget.selectAll('.chart-container').remove();
                // Ensure the chart inputs comes AFTER any chart container.
                if(inputs.length > 0) {
                    inputs.before(container);
                } else {
                    $widget.append(container);
                }
                // Handle any custom inputs the user specified for this module.
                // They map to standard form inputs and correspond to query
                // arguments for this dataSource.
                if(config.inputs) {
                    handleInputs(widg, config);
                }

                // Retrieve and immediately call the appropriate handler.
                getHandler(family)(widget, config);

            } catch(e) {
                if(console && console.error) console.error(e);
                widget.classed({error: true});
                widget.select('.error-overlay')
                    .classed({hidden: false})
                    .select('.alert')
                    .text('Loading error: "' + e + '"');
                unload(widget);
            }
            addResizeEvent(widg);
        };
        self._updateForm = function() {
            self.getInput().val(JSON.stringify(self.config));
        };

        // Run init script on creation
        self.init();
    }

    /**
     * [fillEmptyCols Fill in gaps in a row when an item has been deleted (fixed grid only)]
     */
    function fillEmptyCols(row) {
        row.each(function(_, row){
            var items = $(row).find('.item.widget');
            var cols = $(row).find('> div');
            cols.filter(function(i, col){
                return $(col).find('.item.widget').length === 0;
            }).remove();
        });
    }

    function togglePreviewOutput(is_on) {
        if(is_on) {
            API_PREVIEW_CONT.show();
            return;
        }
        API_PREVIEW_CONT.hide();
    }

    function previewAPIRoute(e) {
        e.preventDefault();
        // Shows the response of the API field as a json payload, inline.
        $.ajax({
            type: 'GET',
            url: API_ROUTE_URL.val().trim(),
            success: function(data) {
                API_PREVIEW.html(prettyCode(data));
                API_PREVIEW.trigger(EVENTS.preview_api, [{status: data, error: false}]);
            },
            error: function(data, status, error) {
                API_PREVIEW.html(error);
                API_PREVIEW.trigger(EVENTS.preview_api, [{status: data, error: true}]);
            }
        });
    }

    function refreshableType(type) {
        if(type === 'youtube') {return false;}
        return true;
    }

    function validateWidgetForm() {
        var is_valid = true;
        var url_field = WIDGET_FORM.find('[name="dataSource"]');
        WIDGET_FORM.find('[required]').each(function(i, el){
            if($(el).val() === '') {
                $(el).parent().addClass('has-error').removeClass('has-success');
                is_valid = false;
                return false;
            } else {
                $(el).parent().addClass('has-success').removeClass('has-error');
            }
        });
        // Validate youtube videos
        if(WIDGET_FORM.find('[name="type"]').val() === 'youtube') {
            if(!url_field.val().startsWith('<iframe')) {
                url_field.parent().addClass('has-error');
                is_valid = false;
                return false;
            }
        }
        return is_valid;
    }

    function saveWidget(e){
        if(!(validateWidgetForm())) {
            return false;
        }
        var new_config = my.widgets.newModel();
        // Remove empty rows and then update the order so it's consecutive.
        $('.grid-row').not('.grid-row-template').each(function(i, row){
            // Delete empty rows - except any empty rows that have been created
            // for the purpose of this new chart.
            if($(row).find('.item.widget').length === 0 && new_config.row !== i + 1) {
                $(row).remove();
            }
        });
        // Update the row orders after deleting empty ones
        updateRowOrder();
        var newfield = $('<input class="form-control" type="text">');
        // Add a unique guid for referencing later.
        newfield.attr('name', 'module_' + new_config.id);
        newfield.val(JSON.stringify(new_config));
        $('.modules').append(newfield);
        // Save immediately.
        MAIN_FORM.submit();
    }

    function isModalButton(e) {
        return e.relatedTarget.id === ADD_MODULE.selector.replace('#', '');
    }

    function isRowButton(e) {
        return $(e.relatedTarget).hasClass('grid-row-label');
    }

    function clearForm() {
        WIDGET_FORM.find('label')
        .removeClass('has-error')
        .removeClass('has-success')
        .find('input, select')
        .each(function(_, input){
            $(input).val('');
        });
    }

    function deleteRow(row) {
        var rownum = row.find('.grid-row-label').data().row;
        row.find('.item.widget').each(function(i, widget){
            var guid = $(this).data().guid;
            var widget = my.widgets.get(guid).delete(true);
        });
        // Remove AFTER removing the charts contained within
        row.remove();
        updateRowOrder();
        el.trigger(EVENTS.delete_row);
    }

    function populateEditForm(e) {
        // If the modal caller was the add modal button, skip populating the field.
        API_PREVIEW.text('...');
        clearForm();
        if(isModalButton(e) || isRowButton(e)) {
            DELETE_BTN.hide();
            if(isRowButton(e)) {
                var row = $(e.relatedTarget).data().row;
                populateRowField(row);
                // Trigger the order field update based on the current row
                WIDGET_FORM.find('[name="row"]').change();
            } else {
                populateRowField();
            }
            return;
        }
        DELETE_BTN.show();
        // Updates the fields in the edit form to the active widgets values.
        var item = $(e.relatedTarget).closest('.item.widget');
        var guid = item.data().guid;
        var widget = my.widgets.get(guid);
        var conf = widget.config;
        populateRowField(conf.row);
        // Update the modal fields with this widgets' value.
        $.each(conf, function(field, val){
            if(field === 'override' || field === 'refresh') {
                WIDGET_FORM.find('[name="' + field + '"]').prop('checked', val);
            } else if(field === 'classes') {
                WIDGET_FORM.find('[name="' + field + '"]').val(val.join(','));
            } else {
                WIDGET_FORM.find('[name="' + field + '"]').val(val);
            }
        });
        // Update with current guid for referencing the module.
        WIDGET_FORM.attr('data-guid', guid);
        // Populate visual GUID
        $('[data-view-chart-guid]').find('.guid-text').text(guid);
        populateOrderField(widget);
        // Update form for specific row if row button was caller
        // Trigger event for select dropdown to ensure any UI is consistent.
        // This is done AFTER the fields have been pre-populated.
        WIDGET_FORM.find('[name="type"]').change();
        // A trigger for 3rd-party/external js to use to listen to.
        WIDGET_FORM.trigger(EVENTS.edit_form_loaded);
    }

    function populateRowField(row) {
        var rows_field = $('[name="row"]');
        var num_rows = $('.grid-row').not('.grid-row-template').length;
        // Don't try and populate if not in freeform mode.
        if(my.layout === 'freeform') {return;}
        if(num_rows === 0){
            addNewRow();
        }
        rows_field.find('option').remove();
        // Add new option fields - d3 range is exclusive so we add one
        d3.map(d3.range(1, num_rows + 1), function(i){
            var option = $('<option></option>');
            option.val(i).text('row ' + i);
            rows_field.append(option);
        });
        // Update current value
        if(row) {rows_field.val(row)};
    }

    /**
     * [populateOrderField Destroy and re-create order dropdown input based on number of items in a row, or in a dashboard.]
     * @param  {[object]} config [The widget config (optional)]
     */
    function populateOrderField(widget) {
        // Add the number of items to order field.
        var order_field = WIDGET_FORM.find('[name="order"]');
        var max_options = 0;
        if(my.layout === 'grid') {
            if(!widget) {
                var row = WIDGET_FORM.find('[name="row"]').val();
                // Get the max options based on the currently selected value in the row dropdown
                // We also add one since this is "adding" a new item so the order should include
                // one more than is currently there.
                max_options = $('.grid-row').eq(row - 1).find('.item.widget').length + 1;
            } else {
                // Get parent row and find number of widget children for this rows' order max
                max_options = $(widget.el[0]).closest('.grid-row').find('.item.widget').length;
            }
        } else {
            var widgets = $('.item.widget');
            max_options = widgets.length > 0 ? widgets.length: 2;
        }
        order_field.find('option').remove();
        // Add empty option.
        order_field.append('<option value=""></option>');
        d3.map(d3.range(1, max_options + 1), function(i){
            var option = $('<option></option>');
            option.val(i).text(i);
            order_field.append(option);
        });
        order_field.val(widget && widget.config ? widget.config.order : '');
    }

    /**
     * [getParsedFormConfig Get a config usable for each json widget based on the forms active values.]
     * @return {[object]} [The serialized config]
     */
    function getParsedFormConfig() {
        function parseNum(num) {
            // Like parseInt, but always returns a Number.
            if(isNaN(parseInt(num, 10))) {
                return 0;
            }
            return parseInt(num, 10);
        }
        var form = WIDGET_FORM;
        var conf = {
            name: form.find('[name="name"]').val(),
            type: form.find('[name="type"]').val(),
            family: form.find('[name="type"]').find('option:checked').data() ? form.find('[name="type"]').find('option:checked').data().family : null,
            width: form.find('[name="width"]').val(),
            height: parseNum(form.find('[name="height"]').val(), 10),
            dataSource: form.find('[name="dataSource"]').val(),
            override: form.find('[name="override"]').is(':checked'),
            order: parseNum(form.find('[name="order"]').val(), 10),
            refresh: form.find('[name="refresh"]').is(':checked'),
            refreshInterval: jsondash.util.intervalStrToMS(form.find('[name="refreshInterval"]').val()),
            classes: getClasses(form)
        };
        if(my.layout === 'grid') {
            conf['row'] = parseNum(form.find('[name="row"]').val());
        }
        return conf;
    }

    function getClasses(form) {
        var classes = form.find('[name="classes"]').val().replace(/\ /gi, '').split(',');
        return classes.filter(function(el, i){
            return el !== '';
        });
    }

    function onUpdateWidget(e){
        var guid = WIDGET_FORM.attr('data-guid');
        var widget = my.widgets.get(guid);
        var conf = getParsedFormConfig();
        widget.update(conf);
    }

    function refreshWidget(e) {
        e.preventDefault();
        var el = my.widgets.getByEl($(this).closest('.widget'));
        el.$el.trigger(EVENTS.refresh_widget);
        el.load();
        fitGrid();
    }

    /**
     * [isPreviewableType Determine if a chart type can be previewed in the 'preview api' section of the modal]
     * @param  {[type]}  string [The chart type]
     * @return {Boolean}      [Whether or not it's previewable]
     */
    function isPreviewableType(type) {
        if(type === 'iframe') {return false;}
        if(type === 'youtube') {return false;}
        if(type === 'custom') {return false;}
        if(type === 'image') {return false;}
        return true;
    }

    /**
     * [chartsTypeChanged Event handler for onChange event for chart type field]
     */
    function chartsTypeChanged(e) {
        var active_conf = getParsedFormConfig();
        var previewable = isPreviewableType(active_conf.type);
        togglePreviewOutput(previewable);
    }

    function populateGridWidthDropdown() {
        var cols = d3.range(1, 13).map(function(i, v){return 'col-' + i;});;
        var form = d3.select(WIDGET_FORM.selector);
        form.select('[name="width"]').remove();
        form
            .append('select')
            .attr('name', 'width')
            .selectAll('option')
            .data(cols)
            .enter()
            .append('option')
            .value(function(i, v){
                return i;
            })
            .text(function(i, v){
                return i;
            });
    }

    function chartsModeChanged(e) {
        var mode = MAIN_FORM.find('[name="mode"]').val();
        if(mode === 'grid') {
            populateGridWidthDropdown();
        }
    }

    function chartsRowChanged(e) {
        // Update the order field based on the current rows item length.
        populateOrderField();
    }

    function loader(container) {
        container.select('.loader-overlay').classed({hidden: false});
        container.select('.widget-loader').classed({hidden: false});
    }

    function unload(container) {
        container.select('.loader-overlay').classed({hidden: true});
        container.select('.widget-loader').classed({hidden: true});
    }

    /**
     * [addDomEvents Add all dom event handlers here]
     */
    function addDomEvents() {
        MAIN_FORM.find('[name="mode"]').on('change.charts.row', chartsModeChanged);
        WIDGET_FORM.find('[name="row"]').on('change.charts.row', chartsRowChanged);
        // Chart type change
        WIDGET_FORM.find('[name="type"]').on('change.charts.type', chartsTypeChanged);
        // TODO: debounce/throttle
        API_PREVIEW_BTN.on('click.charts', previewAPIRoute);
        // Save module popup form
        SAVE_WIDGET_BTN.on('click.charts.save', saveWidget);
        // Edit existing modules
        EDIT_MODAL.on('show.bs.modal', populateEditForm);
        UPDATE_FORM_BTN.on('click.charts.save', onUpdateWidget);

        // Allow swapping of edit/update events
        // for the add module button and form modal
        ADD_MODULE.on('click.charts', function(){
            UPDATE_FORM_BTN
            .attr('id', SAVE_WIDGET_BTN.selector.replace('#', ''))
            .text('Save widget')
            .off('click.charts.save')
            .on('click.charts.save', saveWidget);
        });

        // Allow swapping of edit/update events
        // for the add module per row button and form modal
        VIEW_BUILDER.on('click.charts', '.grid-row-label', function(){
            UPDATE_FORM_BTN
            .attr('id', SAVE_WIDGET_BTN.selector.replace('#', ''))
            .text('Save widget')
            .off('click.charts.save')
            .on('click.charts.save', saveWidget);
        });

        // Add delete button for existing widgets.
        DELETE_BTN.on('click.charts', function(e){
            e.preventDefault();
            var guid = WIDGET_FORM.attr('data-guid');
            var widget = my.widgets.get(guid).delete(false);
        });
        // Add delete confirm for dashboards.
        DELETE_DASHBOARD.on('submit.charts', function(e){
            if(!confirm('Are you sure?')) e.preventDefault();
        });

        // Format json config display
        $('#json-output').on('show.bs.modal', function(e){
            var code = $(this).find('code').text();
            $(this).find('code').text(prettyCode(code));
        });

        // Add event for downloading json config raw.
        // Will provide decent support but still not major: http://caniuse.com/#search=download
        $('[href="#download-json"]').on('click', function(e){
            var datestr = new Date().toString().replace(/ /gi, '-');
            var data = encodeURIComponent(JSON.stringify(JSON_DATA.val(), null, 4));
            data = "data:text/json;charset=utf-8," + data;
            $(this).attr('href', data);
            $(this).attr('download', 'charts-config-raw-' + datestr + '.json');
        });

        // For fixed grid, add events for making new rows.
        ADD_ROW_CONTS.find('.btn').on('click', addNewRow);

        EDIT_TOGGLE_BTN.on('click', function(e){
            $('body').toggleClass('jsondash-editing');
            updateRowControls();
        });

        $('.delete-row').on('click', function(e){
            e.preventDefault();
            var row = $(this).closest('.grid-row');
            if(row.find('.item.widget').length > 0) {
                if(!confirm('Are you sure?')) {
                    return;
                }
            }
            deleteRow(row);
        });
    }

    function initFixedDragDrop(options) {
        var grid_drag_opts = {
            connectToSortable: '.grid-row'
        };
        $('.grid-row').droppable({
            drop: function(event, ui) {
                // update the widgets location
                var idx    = $(this).index();
                var el     = $(ui.draggable);
                var widget = my.widgets.getByEl(el);
                widget.update({row: idx}, true);
                // Actually move the dom element, and reset
                // the dragging css so it snaps into the row container
                el.parent().appendTo($(this));
                el.css({
                    position: 'relative',
                    top: 0,
                    left: 0
                });
            }
        });
        $('.item.widget').draggable($.extend(grid_drag_opts, options));
    }

    function fitGrid(grid_packer_opts, init) {
        var packer_options = $.isPlainObject(grid_packer_opts) ? grid_packer_opts : {};
        var grid_packer_options = $.extend({}, packer_options, {});
        var drag_options = {
            scroll: true,
            handle: '.dragger',
            start: function() {
                $('.grid-row').addClass('drag-target');
            },
            stop: function(){
                $('.grid-row').removeClass('drag-target');
                EDIT_CONTAINER.collapse('show');
                if(my.layout === 'grid') {
                    // Update row order.
                    updateChartsRowOrder();
                } else {
                    my.chart_wall.packery(grid_packer_options);
                    updateChartsOrder();
                }
            }
        };
        if(my.layout === 'grid' && $('.grid-row').length > 1) {
            initFixedDragDrop(drag_options);
            return;
        }
        if(init) {
            my.chart_wall = $('#container').packery(grid_packer_options);
            items = my.chart_wall.find('.item').draggable(drag_options);
            my.chart_wall.packery('bindUIDraggableEvents', items);
        } else {
            my.chart_wall.packery(grid_packer_options);
        }
    }

    function updateChartsOrder() {
        // Update the order and order value of each chart
        var items = my.chart_wall.packery('getItemElements');
        // Update module order
        $.each(items, function(i, el){
            var widget = my.widgets.getByEl($(this));
            widget.update({order: i}, true);
        });
    }

    function handleInputs(widget, config) {
        var inputs_selector = '[data-guid="' + config.guid + '"] .chart-inputs';
        // Load event handlers for these newly created forms.
        $(inputs_selector).find('form').on('submit', function(e){
            e.stopImmediatePropagation();
            e.preventDefault();
            // Just create a new url for this, but use existing config.
            // The global object config will not be altered.
            // The first {} here is important, as it enforces a deep copy,
            // not a mutation of the original object.
            var url = config.dataSource;
            // Ensure we don't lose params already save on this endpoint url.
            var existing_params = url.split('?')[1];
            var params = jsondash.util.getValidParamString($(this).serializeArray());
            params = jsondash.util.reformatQueryParams(existing_params, params);
            var _config = $.extend({}, config, {
                dataSource: url.replace(/\?.+/, '') + '?' + params
            });
            my.widgets.get(config.guid).update(_config, true);
            // Otherwise reload like normal.
            my.widgets.get(config.guid).load();
            // Hide the form again
            $(inputs_selector).removeClass('in');
        });
    }

    function getHandler(family) {
        var handlers  = {
            basic          : jsondash.handlers.handleBasic,
            datatable      : jsondash.handlers.handleDataTable,
            sparkline      : jsondash.handlers.handleSparkline,
            timeline       : jsondash.handlers.handleTimeline,
            venn           : jsondash.handlers.handleVenn,
            graph          : jsondash.handlers.handleGraph,
            wordcloud      : jsondash.handlers.handleWordCloud,
            vega           : jsondash.handlers.handleVegaLite,
            plotlystandard : jsondash.handlers.handlePlotly,
            cytoscape      : jsondash.handlers.handleCytoscape,
            sigmajs        : jsondash.handlers.handleSigma,
            c3             : jsondash.handlers.handleC3,
            d3             : jsondash.handlers.handleD3,
            flamegraph     : jsondash.handlers.handleFlameGraph
        };
        return handlers[family];
    }

    function addResizeEvent(widg) {
        // Add resize event
        var resize_opts = {
            helper: 'resizable-helper',
            minWidth: MIN_CHART_SIZE,
            minHeight: MIN_CHART_SIZE,
            maxWidth: VIEW_BUILDER.width(),
            handles: my.layout === 'grid' ? 's' : 'e, s, se',
            stop: function(event, ui) {
                var newconf = {height: ui.size.height};
                if(my.layout !== 'grid') {
                    newconf['width'] = ui.size.width;
                }
                // Update the configs dimensions.
                widg.update(newconf);
                fitGrid();
                // Open save panel
                EDIT_CONTAINER.collapse('show');
            }
        };
        // Add snap to grid (vertical only) in fixed grid mode.
        // This makes aligning charts easier because the snap points
        // are more likely to be consistent.
        if(my.layout === 'grid') {resize_opts['grid'] = 20;}
        $(widg.el[0]).resizable(resize_opts);
    }

    function prettyCode(code) {
        if(typeof code === "object") return JSON.stringify(code, null, 4);
        return JSON.stringify(JSON.parse(code), null, 4);
    }

    function prettifyJSONPreview() {
        // The raw config is hidden in demo mode,
        // so this will throw an error otherwise
        if(jsondash.util.isInDemoMode()) {return;}
        // Reformat the code inside of the raw json field,
        // to pretty print for the user.
        JSON_DATA.text(prettyCode(JSON_DATA.text()));
    }

    function addNewRow(e) {
        // Add a new row with a toggleable label that indicates
        // which row it is for user editing.
        var placement = 'top';
        if(e) {
            e.preventDefault();
            placement = $(this).closest('.row').data().rowPlacement;
        }
        var el = ROW_TEMPLATE.clone(true);
        el.removeClass('grid-row-template');
        if(placement === 'top') {
            VIEW_BUILDER.find('.add-new-row-container:first').after(el);
        } else {
            VIEW_BUILDER.find('.add-new-row-container:last').before(el);
        }
        // Update the row ordering text
        updateRowOrder();
        // Add new events for dragging/dropping
        fitGrid();
        el.trigger(EVENTS.add_row);
    }

    function updateChartsRowOrder() {
        // Update the row order for each chart.
        // This is necessary for cases like adding a new row,
        // where the order is updated (before or after) the current row.
        // NOTE: This function assumes the row order has been recalculated in advance!
        $('.grid-row').each(function(i, row){
            $(row).find('.item.widget').each(function(j, item){
                var widget = my.widgets.getByEl($(item));
                widget.update({row: i + 1, order: j + 1}, true);
            });
        });
    }

    function updateRowOrder() {
        $('.grid-row').not('.grid-row-template').each(function(i, row){
            var idx = $(row).index();
            $(row).find('.grid-row-label').attr('data-row', idx);
            $(row).find('.rownum').text(idx);
        });
        updateChartsRowOrder();
    }

    function loadDashboard(data) {
        // Load the grid before rendering the ajax, since the DOM
        // is rendered server side.
        fitGrid({
            columnWidth: 5,
            itemSelector: '.item',
            transitionDuration: 0,
            fitWidth: true
        }, true);
        $('.item.widget').removeClass('hidden');

        // Populate widgets with the config data.
        my.widgets.populate(data);

        // Load all widgets, adding actual ajax data.
        my.widgets.loadAll();

        // Setup responsive handlers
        var jres = jRespond([{
            label: 'handheld',
            enter: 0,
            exit: 767
        }]);
        jres.addFunc({
            breakpoint: 'handheld',
            enter: function() {
                $('.widget').css({
                    'max-width': '100%',
                    'width': '100%',
                    'position': 'static'
                });
            }
        });
        prettifyJSONPreview();
        populateRowField();
        fitGrid();
        if(isEmptyDashboard()) {EDIT_TOGGLE_BTN.click();}
        MAIN_CONTAINER.trigger(EVENTS.init);
    }

    /**
     * [updateRowControls Check each row's buttons and disable the "add" button if that row
     * is at the maximum colcount (12)]
     */
    function updateRowControls() {
        $('.grid-row').not('.grid-row-template').each(function(i, row){
            var count = getRowColCount($(row));
            if(count >= 12) {
                $(row).find('.grid-row-label').addClass('disabled');
            } else {
                $(row).find('.grid-row-label').removeClass('disabled');
            }
        });
    }

    /**
     * [getRowColCount Return the column count of a row.]
     * @param  {[dom selection]} row [The row selection]
     */
    function getRowColCount(row) {
        var count = 0;
        row.find('.item.widget').each(function(j, item){
            var classes = $(item).parent().attr('class').split(/\s+/);
            for(var i in classes) {
                if(classes[i].startsWith('col-md-')) {
                    count += parseInt(classes[i].replace('col-md-', ''), 10);
                }
            }
        });
        return count;
    }

    function isEmptyDashboard() {
        return $('.item.widget').length === 0;
    }

    my.config = {
        WIDGET_MARGIN_X: 20,
        WIDGET_MARGIN_Y: 60
    };
    my.loadDashboard = loadDashboard;
    my.handlers = {};
    my.util = {};
    my.loader = loader;
    my.unload = unload;
    my.addDomEvents = addDomEvents;
    my.getActiveConfig = getParsedFormConfig;
    my.layout = VIEW_BUILDER.length > 0 ? VIEW_BUILDER.data().layout : null;
    my.widgets = new Widgets();
    return my;
}();
