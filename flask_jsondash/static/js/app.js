/** global: d3 */
/**
 * Bootstrapping functions, event handling, etc... for application.
 */

var jsondash = function() {
    var my = {
        chart_wall: null
    };
    var dashboard_data = null;
    var $API_ROUTE_URL = '[name="dataSource"]';
    var $API_PREVIEW = '#api-output';
    var $API_PREVIEW_BTN = '#api-output-preview';
    var $MODULE_FORM = '#module-form';
    var $VIEW_BUILDER = '#view-builder';
    var $ADD_MODULE = '#add-module';
    var $MAIN_CONTAINER = '#container';
    var $EDIT_MODAL = '#chart-options';
    var $DELETE_BTN = '#delete-widget';
    var $DELETE_DASHBOARD = '.delete-dashboard';
    var $SAVE_MODULE = '#save-module';
    var $EDIT_CONTAINER = '#edit-view-container';

    function addWidget(container, model) {
        if(document.querySelector('[data-guid="' + model.guid + '"]')) return d3.select('[data-guid="' + model.guid + '"]');
        return d3.select(container).select('div')
            .append('div')
            .classed({item: true, widget: true})
            .attr('data-guid', model.guid)
            .attr('data-refresh', model.refresh)
            .attr('data-refresh-interval', model.refreshInterval)
            .style('width', model.width + 'px')
            .style('height', model.height + 'px')
            .html(d3.select('#chart-template').html())
            .select('.widget-title .widget-title-text').text(model.name);
    }

    function previewAPIRoute(e) {
        e.preventDefault();
        // Shows the response of the API field as a json payload, inline.
        $.ajax({
            type: 'get',
            url: $($API_ROUTE_URL).val().trim(),
            success: function(d) {
               $($API_PREVIEW).html(prettyCode(d));
            },
            error: function(d, status, error) {
                $($API_PREVIEW).html(error);
            }
        });
    }

    function refreshableType(type) {
        if(type === 'youtube') {return false;}
        return true;
    }

    function saveModule(e){
        var data     = jsondash.util.serializeToJSON($($MODULE_FORM).serializeArray());
        var newfield = $('<input class="form-control" type="text">');
        var id       = jsondash.util.guid();
        // Add a unique guid for referencing later.
        data['guid'] = id;
        // Add family for lookups
        data['family'] = $($MODULE_FORM).find('[name="type"]').find('option:selected').data().family;
        if(!data.refresh || !refreshableType(data.type)) {data['refresh'] = false;}
        if(!data.override) {data['override'] = false;}
        newfield.attr('name', 'module_' + id);
        newfield.val(JSON.stringify(data));
        $('.modules').append(newfield);
        // Add new visual block to view grid
        addWidget($VIEW_BUILDER, data);
        // Refit the grid
        fitGrid();
    }

    function isModalButton(e) {
        return e.relatedTarget.id === $ADD_MODULE.replace('#', '');
    }

    function updateEditForm(e) {
        var module_form = $($MODULE_FORM);
        // If the modal caller was the add modal button, skip populating the field.
        if(isModalButton(e)) {
            module_form.find('input').each(function(_, input){
                $(input).val('');
            });
            $($API_PREVIEW).empty();
            $($DELETE_BTN).hide();
            return;
        }
        $($DELETE_BTN).show();
        // Updates the fields in the edit form to the active widgets values.
        var item = $(e.relatedTarget).closest('.item.widget');
        var guid = item.data().guid;
        var module = getModule(item);
        // Update the modal window fields with this one's value.
        $.each(module, function(field, val){
            if(field === 'override' || field === 'refresh') {
                module_form.find('[name="' + field + '"]').prop('checked', val);
            } else {
                module_form.find('[name="' + field + '"]').val(val);
            }
        });
        // Update with current guid for referencing the module.
        module_form.attr('data-guid', guid);
        populateOrderField(module);
    }

    function populateOrderField(module) {
        var module_form = $($MODULE_FORM);
        var widgets = $('.item.widget');
        // Add the number of items to order field.
        var order_field = module_form.find('[name="order"]');
        var max_options = widgets.length > 0 ? widgets.length + 1 : 2;
        order_field.find('option').remove();
        // Add empty option.
        order_field.append('<option value=""></option>');
        d3.map(d3.range(1, max_options), function(i){
            var option = $('<option></option>');
            option.val(i).text(i);
            order_field.append(option);
        });
        order_field.val(module && module.order ? module.order : '');
    }

    function updateModule(e){
        var module_form = $($MODULE_FORM);
        // Updates the module input fields with new data by rewriting them all.
        var guid = module_form.attr('data-guid');
        var active = getModuleByGUID(guid);
        // Update the modules values to the current input values.
        module_form.find('input').each(function(_, input){
            var name = $(input).attr('name');
            if(name) {
                if(name === 'override' || name === 'refresh') {
                    // Convert checkbox to json friendly format.
                    active[name] = $(input).is(':checked');
                } else {
                    active[name] = $(input).val();
                }
            }
        });
        // Update bar chart type
        active['type'] = module_form.find('[name="type"]').val();
        // Update order
        active['order'] = parseInt(module_form.find('[name="order"]').val(), 10);
        // Clear out module input values
        $('.modules').empty();
        $.each(dashboard_data.modules, function(i, module){
            var val = JSON.stringify(module, module);
            var input = $('<input type="text" name="module_' + i + '" class="form-control">');
            input.val(val);
            $('.modules').append(input);
        });
        updateWidget(active);
        $($EDIT_CONTAINER).collapse();
        // Refit the grid
        fitGrid();
    }

    function updateWidget(config) {
        // Trigger update form into view since data is dirty
        // Update visual size to existing widget.
        var widget = getModuleWidgetByGUID(config.guid);
        loader(widget);
        widget.style({
            height: config.height + 'px',
            width: config.width + 'px'
        });
        widget.select('.widget-title .widget-title-text').text(config.name);
        loadWidgetData(widget, config);
    }

    function refreshWidget(e) {
        e.preventDefault();
        var config = getModule($(this).closest('.widget'));
        var widget = addWidget($MAIN_CONTAINER, config);
        loadWidgetData(widget, config);
        fitGrid();
    }

    function addChartContainers(container, data) {
        for(var name in data.modules){
            // Closure to maintain each chart data value in loop
            (function(config){
                var config = data.modules[name];
                // Add div wrappers for js grid layout library,
                // and add title, icons, and buttons
                var widget = addWidget(container, config);
                // Determine how to load this widget
                loadWidgetData(widget, config);
            })(data.modules[name]);
        }
        fitGrid();
    }

    function getModuleWidgetByGUID(guid) {
        return d3.select('.item.widget[data-guid="' + guid + '"]');
    }

    function getModuleByGUID(guid) {
        return dashboard_data.modules.find(function(n){return n['guid'] === guid});
    }

    function deleteModule(e) {
        e.preventDefault();
        if(!confirm('Are you sure?')) {return;}
        var guid = $($MODULE_FORM).attr('data-guid');
        // Remove form input and visual widget
        $('.modules').find('#' + guid).remove();
        $('.item.widget[data-guid="' + guid + '"]').remove();
        $($EDIT_MODAL).modal('hide');
        // Redraw wall to replace visual 'hole'
        fitGrid();
        // Trigger update form into view since data is dirty
        $($EDIT_CONTAINER).collapse('show');
    }

    function addDomEvents() {
        // TODO: debounce/throttle
        $($API_ROUTE_URL).on('change.charts', previewAPIRoute);
        $($API_PREVIEW_BTN).on('click.charts', previewAPIRoute);
        // Save module popup form
        $($SAVE_MODULE).on('click.charts.module', saveModule);
        // Edit existing modules
        $($EDIT_MODAL).on('show.bs.modal', updateEditForm);
        $('#update-module').on('click.charts.module', updateModule);
        // Allow swapping of edit/update events
        // for the add module button and form modal
        $($ADD_MODULE).on('click.charts', function(){
            $('#update-module')
            .attr('id', $SAVE_MODULE.replace('#', ''))
            .text('Save module')
            .off('click.charts.module')
            .on('click.charts', saveModule);
        });
        // Allow swapping of edit/update events
        // for the edit button and form modal
        $('.widget-edit').on('click.charts', function(){
            $($SAVE_MODULE)
            .attr('id', 'update-module')
            .text('Update module')
            .off('click.charts.module')
            .on('click.charts', updateModule);
        });
        // Add delete button for existing widgets.
        $($DELETE_BTN).on('click.charts', deleteModule);
        // Add delete confirm for dashboards.
        $($DELETE_DASHBOARD).on('submit.charts', function(e){
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
        var valid_options = $.isPlainObject(opts);
        var options = $.extend({}, opts, {});
        if(init) {
            my.chart_wall = $('#container').packery(options);
            items = my.chart_wall.find('.item').draggable({
                scroll: true,
                handle: '.dragger',
                stop: function(){
                    $($EDIT_CONTAINER).collapse('show');
                    updateModuleOrder();
                    my.chart_wall.packery(options);
                }
            });
            my.chart_wall.packery('bindUIDraggableEvents', items);
        } else {
            my.chart_wall.packery(options);
        }
    }

    function updateModuleOrder() {
        var items = my.chart_wall.packery('getItemElements');
        // Update module order
        $.each(items, function(i, el){
            var module = getModule($(this));
            var config = $.extend(module, {order: i});
            updateModuleInput(config);
        });
    }

    function getModule(el) {
        // Return module by element
        var data = el.data();
        var guid = data.guid;
        var module = getModuleByGUID(guid);
        return module;
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
            var params = getValidParamString($(this).serializeArray());
            var _config = $.extend({}, config, {
                dataSource: url.replace(/\?.+/, '') + '?' + existing_params + '&' + params
            });
            // Otherwise reload like normal.
            loadWidgetData(widget, _config);
            // Hide the form again
            $(inputs_selector).removeClass('in');
        });
    }

    function getValidParamString(arr) {
        // Jquery $.serialize and $.serializeArray will
        // return empty query parameters, which is undesirable and can
        // be error prone for RESTFUL endpoints.
        // e.g. `foo=bar&bar=` becomes `foo=bar`
        var param_str = '';
        arr = arr.filter(function(param, i){return param.value !== '';});
        $.each(arr, function(i, param){
            param_str += (param.name + '=' + param.value);
            if(i < arr.length - 1 && arr.length > 1) param_str += '&';
        });
        return param_str;
    }

    function loadWidgetData(widget, config) {
        loader(widget);
        try {
            // Handle any custom inputs the user specified for this module.
            // They map to standard form inputs and correspond to query
            // arguments for this dataSource.
            if(config.inputs) {handleInputs(widget, config);}

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
            unload(widget);
        }
        addResizeEvent(widget, config);
    }

    function addResizeEvent(widget, config) {
        // Add resize event
        $(widget[0]).resizable({
            helper: 'resizable-helper',
            minWidth: 200,
            minHeight: 200,
            stop: function(event, ui) {
                // Update the configs dimensions.
                config = $.extend(config, {width: ui.size.width, height: ui.size.height});
                updateModuleInput(config);
                loadWidgetData(widget, config);
                fitGrid();
                // Open save panel
                $($EDIT_CONTAINER).collapse('show');
            }
        });
    }

    function updateModuleInput(config) {
        $('input[id="' + config.guid + '"]').val(JSON.stringify(config));
    }

    function prettyCode(code) {
        if(typeof code === "object") return JSON.stringify(code, null, 4);
        return JSON.stringify(JSON.parse(code), null, 4);
    }

    function addRefreshers(modules) {
        $.each(modules, function(_, module){
            if(module.refresh && module.refreshInterval) {
                var container = d3.select('[data-guid="' + module.guid + '"]');
                setInterval(function(){
                    loadWidgetData(container, module);
                }, parseInt(module.refreshInterval, 10));
            }
        });
    }

    function loadDashboard(data) {
        // Load the grid before rendering the ajax, since the DOM
        // is rendered server side.
        initGrid($MAIN_CONTAINER);
        // Add actual ajax data.
        addChartContainers($MAIN_CONTAINER, data);
        dashboard_data = data;

        // Add event handlers for widget UI
        $('.widget-refresh').on('click.charts', refreshWidget);

        // Setup refresh intervals for all widgets that specify it.
        addRefreshers(data.modules);

        // Format json config display
        $('#json-output').on('show.bs.modal', function(e){
            var code = $(this).find('code').text();
            $(this).find('code').text(prettyCode(code));
        });

        // Reformat the code inside of the raw json field, to pretty print
        // for the user.
        $('#raw-config').text(prettyCode($('#raw-config').text()));

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
        populateOrderField();
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
    return my;
}();
