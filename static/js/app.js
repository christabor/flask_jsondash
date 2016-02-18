/**
 * Bootstrapping functions, event handling, etc... for application.
 */

 var dashboard_data = null;
 var wall = null;
 var HEARTBEAT_INTERVAL = 10000;
 var $API_PREVIEW = '#api-output';
 var $NEW_MODULE = '#new-module';
 var $VIEW_BUILDER = '#view-builder';
 var $ADD_MODULE = '#add-module';
 var $MAIN_CONTAINER = '#container';

 function previewAPIRoute(e) {
    // Shows the response of the API field as a json payload, inline.
    $.get($(this).val().trim(), function(d){
       $($API_PREVIEW).html(d);
   });
}

function saveModule(e){
    var data     = serializeToJSON($($NEW_MODULE).serializeArray());
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
    wall.fitWidth();
}

function updateEditForm(e) {
    // Updates the fields in the edit form to the active widgets values.
    var name = $(this).siblings('div:first').attr('id');
    var module_form = $('#new-module');
    var module = dashboard_data.modules.find(function(n){return n['name'] === name});
    // Update the modal window fields with this one's value.
    $.each(module, function(field, val){
        module_form.find('[name="' + field + '"]').val(val);
    });
    // Update with current guid for referencing the module.
    module_form.attr('data-guid', module.guid);
}

function updateModule(e){
    var module_form = $('#new-module');
    // Updates the module input fields with new data by rewriting them all.
    var active = dashboard_data.modules.find(function(n){return n['guid'] === module_form.attr('data-guid')});
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
    var config = dashboard_data.modules.find(function(n){return n['guid'] === guid;});
    var widget = addWidget($MAIN_CONTAINER, config);
    loadWidgetData(widget, config, config);
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
            loadWidgetData(widget, config, config);
        })(data.modules[name]);
    }
    initGrid($MAIN_CONTAINER);
}

function addDomEvents() {
    initGrid($VIEW_BUILDER);
    // TODO: debounce/throttle
    $('[name="dataSource"]').on('change', previewAPIRoute);
    // Save module popup form
    $('#save-module').on('click.module', saveModule);

    // Sidepanels
    $('.panel-button').on('click', togglePanel);

    // Edit existing modules
    $('.widget-edit').on('click', updateEditForm);
    $('#update-module').on('click.module', updateModule);
    // Allow swapping of edit/update events
    // for the add module button and form modal
    $($ADD_MODULE).on('click', function(){
        $('#update-module')
        .attr('id', 'save-module').text('Save module')
        .off('click.module')
        .on('click', saveModule);
    });
    // Allow swapping of edit/update events
    // for the edit button and form modal
    $('.widget-edit').on('click', function(){
        $('#save-module')
        .attr('id', 'update-module').text('Update module')
        .off('click.module')
        .on('click', updateModule);
    });
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
    wall = new freewall(container);
    wall.reset({
        selector: '.item',
        delay: 1,
        fixSize: 1, // Important! Fixes the widgets to their configured size.
        gutterX: 4,
        gutterY: 4
        // draggable: true,
        // onResize: function() {
        //     wall.fitWidth();
        // }
    });
    wall.fitWidth();
}

function unload(container) {
    container.select('.widget-loader').attr('class', 'hidden');
}

function loadWidgetData(widget, config, config) {
    if(config.type === 'datatable') {
        _handleDataTable(widget, config, config);
    }
    else if(config.type.substr(0, 10) === 'sparklines') {
        _handleSparkline(widget, config, config);
    }
    else if(config.type === 'iframe') {
        _handleIframe(widget, config, config);
    }
    else if(config.type === 'timeline') {
        _handleTimeline(widget, config, config);
    }
    else if(config.type === 'custom') {
        _handleCustom(widget, config, config);
    }
    // TODO: FIX THIS ASAP
    else if(config.type === 'dendrogram' || config.type === 'voronoi') {
        _handleD3(widget, config, config);
    } else {
        _handleC3(widget, config, config);
    }
}

function loadDashboard(data) {
    addChartContainers($MAIN_CONTAINER, data);
    dashboard_data = data;
    // Set interval
    setInterval(function(){heartBeat(data);}, HEARTBEAT_INTERVAL);
    // Add event handlers for widget UI
    $('.widget-refresh').on('click', refreshWidget);
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

function init() {
    addDomEvents();
}

$(document).ready(init);
