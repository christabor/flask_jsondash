/**
 * Templating functions for DOM manipulation/template creation.
 */

function addWidget(container, model) {
    // Return if it exists.
    if(document.querySelector('[data-guid="' + model.guid + '"]')) return d3.select('[data-guid="' + model.guid + '"]');
    // Create new widget html
    var widget = d3.select(container).append('div');
    widget.attr('class', 'item widget');
    // Need a guid for referencing later
    widget.attr('data-guid', model.guid);
    widget.style('width',  model.width + 'px');
    widget.style('height',  model.height + 'px');

    var html = `
    <span class="widget-loader fa fa-circle-o-notch fa-spin"></span>
    <p class="widget-title">
    {name}
    <span rel="tooltip" title="Refresh the panels url endpoint" class="pull-right icon widget-refresh fa fa-refresh"></span>
    </p>
    <a href="#chart-options" data-toggle="modal" class="widget-edit"><span class="fa fa-edit"></span> Edit</a>
    <div id="{id}"></div>
    `.assign({
        name: model.name,
        width: model.width,
        height: model.height,
        id: normalizeName(model.name)
    });
    widget.html(html);
    return widget;
}
