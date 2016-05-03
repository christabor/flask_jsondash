/**
 * Bootstrapping functions, event handling, etc... for application.
 */

 var dashboard_data = null;
 var chart_wall = null;
 var $API_ROUTE_URL = '[name="dataSource"]';
 var $API_PREVIEW = '#api-output';
 var $API_PREVIEW_BTN = '#api-output-preview';
 var $MODULE_FORM = '#module-form';
 var $VIEW_BUILDER = '#view-builder';
 var $ADD_MODULE = '#add-module';
 var $MAIN_CONTAINER = '#container';
 var $EDIT_MODAL = '#chart-options';
 var $DELETE_BTN = '#delete-widget';

 function previewAPIRoute(e) {
    e.preventDefault();
    // Shows the response of the API field as a json payload, inline.
    $.ajax({
        type: 'get',
        url: $($API_ROUTE_URL).val().trim(),
        success: function(d) {
           $($API_PREVIEW).html(d);
        },
        error: function(d, status, error) {
            $($API_PREVIEW).html(error);
        }
    });
}

function saveModule(e){
    var data     = serializeToJSON($($MODULE_FORM).serializeArray());
    var last     = $('.modules').find('input').last();
    var newfield = $('<input class="form-control" type="text">');
    var id = guid();
    // Add a unique guid for referencing later.
    data['guid'] = id;
    newfield.attr('name', 'module_' + id);
    newfield.val(JSON.stringify(data));
    $('.modules').append(newfield);
    // Add new visual block to view grid
    addWidget($VIEW_BUILDER, data);
    // Refit the grid
    chart_wall.fitWidth();
}

function updateEditForm(e) {
    var module_form = $($MODULE_FORM);
    // If the modal caller was the add modal button, skip populating the field.
    if(e.relatedTarget.id === $ADD_MODULE.replace('#', '')) {
        module_form.find('input').each(function(k, input){
            $(input).val('');
        });
        return;
    }
    // Updates the fields in the edit form to the active widgets values.
    var data = $(e.relatedTarget).closest('.item.widget').data();
    var guid = data.guid;
    var module = getModuleByGUID(guid);
    // Update the modal window fields with this one's value.
    $.each(module, function(field, val){
        module_form.find('[name="' + field + '"]').val(val);
    });
    // Update with current guid for referencing the module.
    module_form.attr('data-guid', guid);
}

function updateModule(e){
    var module_form = $($MODULE_FORM);
    // Updates the module input fields with new data by rewriting them all.
    var guid = module_form.attr('data-guid');
    var active = getModuleByGUID(guid);
    module_form.find('input').each(function(k, input){
        var name = $(input).attr('name');
        if(name) active[name] = $(input).val();
    });
    $('.modules').empty();
    $.each(dashboard_data.modules, function(k, module){
        var val = JSON.stringify(module);
        var input = $('<input type="text" name="module_' + k + '" class="form-control">');
        input.val(val);
        $('.modules').append(input);
    });
    // Trigger update form into view since data is dirty
    $('#edit-view-container').collapse('in');
}

function refreshWidget(e) {
    e.preventDefault();
    var container = $(this).closest('.widget');
    var guid = container.attr('data-guid');
    var config = getModuleByGUID(guid);
    var widget = addWidget($MAIN_CONTAINER, config);
    loadWidgetData(widget, config);
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
    initGrid($MAIN_CONTAINER);
}

function getModuleByGUID(guid) {
    return dashboard_data.modules.find(function(n){return n['guid'] === guid});
}

function deleteModule(e) {
    e.preventDefault();
    var guid = $($MODULE_FORM).attr('data-guid');
    var module = getModuleByGUID(guid);
    // Remove form input and visual widget
    $('.modules').find('#' + guid).remove();
    $('.item.widget[data-guid="' + guid + '"]').remove();
    $($EDIT_MODAL).modal('hide');
    // Redraw wall to replace visual 'hole'
    chart_wall.fitWidth();
}

function addDomEvents() {
    initGrid($VIEW_BUILDER);
    // TODO: debounce/throttle
    $($API_ROUTE_URL).on('change.charts', previewAPIRoute);
    $($API_PREVIEW_BTN).on('click.charts', previewAPIRoute);
    // Save module popup form
    $('#save-module').on('click.charts.module', saveModule);
    // Edit existing modules
    $($EDIT_MODAL).on('show.bs.modal', updateEditForm);
    $('#update-module').on('click.charts.module', updateModule);
    // Allow swapping of edit/update events
    // for the add module button and form modal
    $($ADD_MODULE).on('click.charts', function(){
        $('#update-module')
        .attr('id', 'save-module')
        .text('Save module')
        .off('click.charts.module')
        .on('click.charts', saveModule);
    });
    // Allow swapping of edit/update events
    // for the edit button and form modal
    $('.widget-edit').on('click.charts', function(){
        $('#save-module')
        .attr('id', 'update-module')
        .text('Update module')
        .off('click.charts.module')
        .on('click.charts', updateModule);
    });
    // Add delete button for existing widgets.
    $($DELETE_BTN).on('click', deleteModule);
}

function heartBeat(data) {
    addChartContainers($MAIN_CONTAINER, data);
}

function togglePanel(e) {
    e.preventDefault();
    var el = $(this).attr('href');
    $(el).toggleClass('open');
}

function initGrid(container) {
    // http://vnjs.net/www/project/freewall/#options
    chart_wall = new freewall(container);
    chart_wall.reset({
        selector: '.item',
        delay: 1,
        fixSize: 1, // Important! Fixes the widgets to their configured size.
        gutterX: 4,
        gutterY: 4,
        draggable: false,
        onResize: function() {
            chart_wall.fitWidth();
        }
    });
    chart_wall.fitWidth();
}

function unload(container) {
    container.select('.widget-loader').attr('class', 'hidden');
}

function isD3Subtype(config) {
    // Handle specific D3 types that aren't necessarily referenced under
    // the D3 namespace in a select field.
    if(config.type === 'dendrogram') return true;
    if(config.type === 'voronoi') return true;
    return false;
}

function isSparkline(type) {
    return type.substr(0, 10) === 'sparklines';
}

function loadWidgetData(widget, config) {
    try {
        if(config.type === 'datatable') {
            _handleDataTable(widget, config);
        }
        else if(isSparkline(config.type)) {
            _handleSparkline(widget, config);
        }
        else if(config.type === 'iframe') {
            _handleIframe(widget, config);
        }
        else if(config.type === 'timeline') {
            _handleTimeline(widget, config);
        }
        else if(config.type === 'custom') {
            _handleCustom(widget, config);
        }
        else if(isD3Subtype(config)) {
            _handleD3(widget, config);
        } else {
            _handleC3(widget, config);
        }
    } catch(e) {}
}

function loadDashboard(data) {
    addChartContainers($MAIN_CONTAINER, data);
    dashboard_data = data;
    if(window.charts_heartbeat.ENABLED) {
        // Set refresh interval
        setInterval(function(){heartBeat(data);}, HEARTBEAT_INTERVAL);
    }
    // Add event handlers for widget UI
    $('.widget-refresh').on('click.charts', refreshWidget);
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
