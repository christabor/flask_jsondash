/** global: d3 */
/**
 * Bootstrapping functions, event handling, etc... for application.
 */

var jsondash = function() {
    var my = {
        chart_wall: null,
        widgets: {},
    };
    var MIN_CHART_SIZE   = 200;
    var dashboard_data   = null;
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
    var SAVE_MODULE      = $('#save-module');
    var EDIT_CONTAINER   = $('#edit-view-container');
    var MAIN_FORM        = $('#save-view-form');
    var JSON_DATA        = $('#raw-config');
    var ADD_ROW_CONTS    = $('.add-new-row-container');
    var EDIT_TOGGLE_BTN  = $('[href=".edit-mode-component"]');
    var UPDATE_FORM_BTN  = $('#update-module');
    var CHART_TEMPLATE   = $('#chart-template');
    var ROW_TEMPLATE     = $('#row-template').find('.grid-row');

    function widget(container, config) {
        // model for a chart widget
        var self = this;
        self.config = config;
        self.guid = self.config.guid;
        self.container = container;
        self._makeWidget = function(container, config) {
            if(document.querySelector('[data-guid="' + config.guid + '"]')) return d3.select('[data-guid="' + config.guid + '"]');
            return d3.select(container).select('div')
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
        self.el = self._makeWidget(container, config);

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
            // Delete the input
            self.getInput().remove();
            // Delete the widget
            self.el.remove();
            // Remove reference to the model by guid
            delete my.widgets[self.guid];
            EDIT_MODAL.modal('hide');
            // Redraw wall to replace visual 'hole'
            fitGrid();
            // Trigger update form into view since data is dirty
            EDIT_CONTAINER.collapse('show');
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
            }
            widget.select('.widget-title .widget-title-text').text(self.config.name);
            // Update the form input for this widget.
            self._updateForm();

            if(!dont_refresh) {
                loadWidgetData(self, self.config);
                EDIT_CONTAINER.collapse();
                // Refit the grid
                fitGrid();
            } else {
                unload(widget);
            }
        };
        self._updateForm = function() {
            self.getInput().val(JSON.stringify(self.config));
        };
    }

    function getFormConfig() {
        return jsondash.util.serializeToJSON(WIDGET_FORM.serializeArray());
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
            type: 'get',
            url: API_ROUTE_URL.val().trim(),
            success: function(data) {
                API_PREVIEW.html(prettyCode(data));
            },
            error: function(data, status, error) {
                API_PREVIEW.html(error);
            }
        });
    }

    function refreshableType(type) {
        if(type === 'youtube') {return false;}
        return true;
    }

    function saveWidget(e){
        var config   = getFormConfig();
        var newfield = $('<input class="form-control" type="text">');
        var id       = jsondash.util.guid();
        // Add a unique guid for referencing later.
        config['guid'] = id;
        // Add family for lookups
        config['family'] = WIDGET_FORM.find('[name="type"]').find('option:selected').data().family;
        if(!config.refresh || !refreshableType(config.type)) {config['refresh'] = false;}
        if(!config.override) {config['override'] = false;}
        newfield.attr('name', 'module_' + id);
        newfield.val(JSON.stringify(config));
        $('.modules').append(newfield);
        // We also need to update the order of all other charts in case.
        updateChartsRowOrder();
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
        WIDGET_FORM.find('input').each(function(_, input){
            $(input).val('');
        });
    }

    function deleteRow(row) {
        var rownum = row.find('.grid-row-label').data().row;
        row.find('.item.widget').each(function(i, widget){
            var guid = $(this).data().guid;
            var widget = getWidgetByGUID(guid).delete(true);
        });
        // Remove AFTER removing the charts contained within
        row.remove();
        updateRowOrder();
    }

    function populateEditForm(e) {
        // If the modal caller was the add modal button, skip populating the field.
        API_PREVIEW.text('...');
        if(isModalButton(e) || isRowButton(e)) {
            clearForm();
            DELETE_BTN.hide();
            if(isRowButton(e)) {
                var row = $(e.relatedTarget).data().row;
                populateRowField(row);
            } else {
                populateRowField();
            }
            return;
        }
        DELETE_BTN.show();
        // Updates the fields in the edit form to the active widgets values.
        var item = $(e.relatedTarget).closest('.item.widget');
        var guid = item.data().guid;
        var conf = getWidgetByGUID(guid).config;
        populateRowField(conf.row);
        // Update the modal fields with this widgets' value.
        $.each(conf, function(field, val){
            if(field === 'override' || field === 'refresh') {
                WIDGET_FORM.find('[name="' + field + '"]').prop('checked', val);
            } else {
                WIDGET_FORM.find('[name="' + field + '"]').val(val);
            }
        });
        // Update with current guid for referencing the module.
        WIDGET_FORM.attr('data-guid', guid);
        populateOrderField(conf);
        // Update form for specific row if row button was caller
        // Trigger event for select dropdown to ensure any UI is consistent.
        // This is done AFTER the fields have been pre-populated.
        WIDGET_FORM.find('[name="type"]').change();
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
        var widgets = $('.item.widget');
        // Add the number of items to order field.
        var order_field = WIDGET_FORM.find('[name="order"]');
        var max_options = 0;
        if(my.layout === 'grid') {
            max_options = widgets.length > 0 ? widgets.length + 1 : 2;
        } else {
            max_options = widgets.length > 0 ? widgets.length + 1 : 2;
        }
        order_field.find('option').remove();
        // Add empty option.
        order_field.append('<option value=""></option>');
        d3.map(d3.range(1, max_options), function(i){
            var option = $('<option></option>');
            option.val(i).text(i);
            order_field.append(option);
        });
        order_field.val(widget && widget.config ? widget.config : '');
    }

    /**
     * [getParsedFormConfig Get a config usable for each json widget based on the forms active values.]
     * @return {[object]} [The serialized config]
     */
    function getParsedFormConfig() {
        var conf = {};
        WIDGET_FORM.find('.form-control').each(function(_, input){
            var name = $(input).attr('name');
            var val = $(input).val();
            if(name === 'override' ||
                name === 'refresh') {
                // Convert checkbox to json friendly format.
                conf[name] = $(input).is(':checked');
            } else if(name === 'refreshInterval' ||
                      name === 'row' ||
                      name === 'height' ||
                      name === 'order') {
                conf[name] = parseInt(val, 10);
                if(isNaN(conf[name])) {
                    conf[name] = null;
                }
            } else {
                conf[name] = val;
            }
            // This is not amenable to integer parsing
            if(name === 'width' && my.layout === 'grid') {
                conf['width'] = val;
            }
        });
        return conf;
    }

    function onUpdateWidget(e){
        var guid = WIDGET_FORM.attr('data-guid');
        var widget = getWidgetByGUID(guid);
        var conf = getParsedFormConfig();
        widget.update(conf);
    }

    function refreshWidget(e) {
        e.preventDefault();
        loadWidgetData(getWidgetByEl($(this).closest('.widget')));
        fitGrid();
    }

    function addChartContainers(container, data) {
        for(var name in data.modules){
            // Closure to maintain each chart data value in loop
            (function(config){
                var config = data.modules[name];
                // Add div wrappers for js grid layout library,
                // and add title, icons, and buttons
                // This is the widget "model"/object used throughout.
                my.widgets[config.guid] = new widget(container, config);
            })(data.modules[name]);
        }
        fitGrid();
        for(var guid in my.widgets){
            var widg = my.widgets[guid];
            loadWidgetData(widg);
        }
    }

    function getWidgetByGUID(guid) {
        return my.widgets[guid];
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
        return true;
    }

    /**
     * [chartsTypeChanged Event handler for onChange event for chart type field]
     */
    function chartsTypeChanged(e) {
        var active_conf = getFormConfig();
        var previewable = isPreviewableType(active_conf.type);
        togglePreviewOutput(previewable);
    }

    /**
     * [addDomEvents Add all dom event handlers here]
     */
    function addDomEvents() {
        // Chart type change
        WIDGET_FORM.find('[name="type"]').on('change.charts.type', chartsTypeChanged);
        // TODO: debounce/throttle
        API_ROUTE_URL.on('change.charts', previewAPIRoute);
        API_PREVIEW_BTN.on('click.charts', previewAPIRoute);
        // Save module popup form
        SAVE_MODULE.on('click.charts.module', saveWidget);
        // Edit existing modules
        EDIT_MODAL.on('show.bs.modal', populateEditForm);
        UPDATE_FORM_BTN.on('click.charts.module', onUpdateWidget);

        // Allow swapping of edit/update events
        // for the add module button and form modal
        ADD_MODULE.on('click.charts', function(){
            UPDATE_FORM_BTN
            .attr('id', SAVE_MODULE.selector.replace('#', ''))
            .text('Save module')
            .off('click.charts.module')
            .on('click.charts', saveWidget);
        });

        // Allow swapping of edit/update events
        // for the add module per row button and form modal
        VIEW_BUILDER.on('click.charts', '.grid-row-label', function(){
            UPDATE_FORM_BTN
            .attr('id', SAVE_MODULE.selector.replace('#', ''))
            .text('Save module')
            .off('click.charts.module')
            .on('click.charts', saveWidget);
        });

        // Allow swapping of edit/update events
        // for the edit button and form modal
        $('.widget-edit').on('click.charts', function(){
            SAVE_MODULE
            .attr('id', UPDATE_FORM_BTN.selector.replace('#', ''))
            .text('Update module')
            .off('click.charts.module')
            .on('click.charts', onUpdateWidget);
        });
        // Add delete button for existing widgets.
        DELETE_BTN.on('click.charts', function(e){
            e.preventDefault();
            var guid = WIDGET_FORM.attr('data-guid');
            var widget = getWidgetByGUID(guid).delete(false);
        });
        // Add delete confirm for dashboards.
        DELETE_DASHBOARD.on('submit.charts', function(e){
            if(!confirm('Are you sure?')) e.preventDefault();
        });
    }

    function initGrid(container) {
        fitGrid({
            columnWidth: 5,
            itemSelector: '.item',
            transitionDuration: 0,
            fitWidth: true
        }, true);
        $('.item.widget').removeClass('hidden');
    }

    function fitGrid(opts, init) {
        var drag_opts = {
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
                    my.chart_wall.packery(options);
                    updateChartsOrder();
                }
            }
        };
        if(my.layout === 'grid') {
            var grid_drag_opts = {
                // revert: true,
                connectToSortable: '.grid-row'
            };
            $('.grid-row').droppable({
                drop: function(event, ui) {
                    // update the widgets location
                    var idx = $(this).index();
                    var el = $(ui.draggable);
                    var widget = getWidgetByEl(el);
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
            $('.item.widget').draggable($.extend(grid_drag_opts, drag_opts));
            return;
        }
        var valid_options = $.isPlainObject(opts);
        var options = $.extend({}, valid_options ? opts : {}, {});
        if(init) {
            my.chart_wall = $('#container').packery(options);
            items = my.chart_wall.find('.item').draggable(drag_opts);
            my.chart_wall.packery('bindUIDraggableEvents', items);
        } else {
            my.chart_wall.packery(options);
        }
    }

    function updateChartsOrder() {
        // Update the order and order value of each chart
        var items = my.chart_wall.packery('getItemElements');
        // Update module order
        $.each(items, function(i, el){
            var widget = getWidgetByEl($(this));
            widget.update({order: i}, true);
        });
    }

    function getWidgetByEl(el) {
        return getWidgetByGUID(el.data().guid);
    }

    function loader(container) {
        container.select('.loader-overlay').classed({hidden: false});
        container.select('.widget-loader').classed({hidden: false});
    }

    function unload(container) {
        container.select('.loader-overlay').classed({hidden: true});
        container.select('.widget-loader').classed({hidden: true});
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
            var _config = $.extend({}, config, {
                dataSource: url.replace(/\?.+/, '') + '?' + existing_params + '&' + params
            });
            // Otherwise reload like normal.
            loadWidgetData(getWidgetByGUID(config.guid));
            // Hide the form again
            $(inputs_selector).removeClass('in');
        });
    }

    /**
     * [loadWidgetData Load a widgets data source/re-render]
     * @param  {[dom selection]} widget [The dom selection]
     * @param  {[object]} config [The chart config]
     */
    function loadWidgetData(widg) {
        var widget = widg.el;
        var config = widg.config;

        widget.classed({error: false});
        widget.select('.error-overlay')
            .classed({hidden: true})
            .select('.alert')
            .text('');

        loader(widget);
        try {
            // Handle any custom inputs the user specified for this module.
            // They map to standard form inputs and correspond to query
            // arguments for this dataSource.
            if(config.inputs) {handleInputs(widg, config);}

            if(config.type === 'datatable') {
                jsondash.handlers.handleDataTable(widget, config);
            }
            else if(jsondash.util.isSparkline(config.type)) {
                jsondash.handlers.handleSparkline(widget, config);
            }
            else if(config.type === 'iframe') {
                jsondash.handlers.handleIframe(widget, config);
            }
            else if(config.type === 'timeline') {
                jsondash.handlers.handleTimeline(widget, config);
            }
            else if(config.type === 'venn') {
                jsondash.handlers.handleVenn(widget, config);
            }
            else if(config.type === 'number') {
                jsondash.handlers.handleSingleNum(widget, config);
            }
            else if(config.type === 'youtube') {
                jsondash.handlers.handleYoutube(widget, config);
            }
            else if(config.type === 'graph'){
                jsondash.handlers.handleGraph(widget, config);
            }
            else if(config.type === 'custom') {
                jsondash.handlers.handleCustom(widget, config);
            }
            else if(config.type === 'wordcloud') {
                jsondash.handlers.handleWordCloud(widget, config);
            }
            else if(config.type === 'plotly-any') {
                jsondash.handlers.handlePlotly(widget, config);
            }
            else if(jsondash.util.isD3Subtype(config)) {
                jsondash.handlers.handleD3(widget, config);
            } else {
                jsondash.handlers.handleC3(widget, config);
            }
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
    }

    function addResizeEvent(widg) {
        // Add resize event
        $(widg.el[0]).resizable({
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
                loadWidgetData(widg);
                fitGrid();
                // Open save panel
                EDIT_CONTAINER.collapse('show');
            }
        });
    }

    function prettyCode(code) {
        if(typeof code === "object") return JSON.stringify(code, null, 4);
        return JSON.stringify(JSON.parse(code), null, 4);
    }

    function addRefreshers(modules) {
        $.each(modules, function(_, module){
            if(module.refresh && module.refreshInterval) {
                setInterval(function(){
                    loadWidgetData(getWidgetByGUID(module.guid));
                }, parseInt(module.refreshInterval, 10));
            }
        });
    }

    function prettifyJSONPreview() {
        // Reformat the code inside of the raw json field,
        // to pretty print for the user.
        JSON_DATA.text(prettyCode(JSON_DATA.text()));
    }

    function setupResponsiveEvents() {
        // This is handled by bs3, so we don't need it.
        if(my.layout === 'grid') {return;}
        // Setup responsive handlers
        var jres = jRespond([
        {
            label: 'handheld',
            enter: 0,
            exit: 767
        }
        ]);
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
    }

    function updateChartsRowOrder() {
        // Update the row order for each chart.
        // This is necessary for cases like adding a new row,
        // where the order is updated (before or after) the current row.
        // NOTE: This function assumes the row order has been recalculated in advance!
        $('.grid-row').each(function(i, row){
            $(row).find('.item.widget').each(function(j, item){
                var widget = getWidgetByEl($(item));
                widget.update({row: i + 1}, true);
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
        initGrid(MAIN_CONTAINER);
        // Add actual ajax data.
        addChartContainers(MAIN_CONTAINER, data);
        my.dashboard_data = data;

        // Add event handlers for widget UI
        $('.widget-refresh').on('click.charts', refreshWidget);

        // Setup refresh intervals for all widgets that specify it.
        addRefreshers(data.modules);

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

        prettifyJSONPreview();
        setupResponsiveEvents();
        populateOrderField();
        populateRowField();
        fitGrid();
        if(isEmptyDashboard()) {EDIT_TOGGLE_BTN.click();}
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
    my.dashboard_data = dashboard_data;
    return my;
}();
