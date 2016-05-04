/**
 * Handlers for various widget types. The method signatures are always the same,
 * but each handler can handle them differently.
 */

var WIDGET_MARGIN_X = 20;
var WIDGET_MARGIN_Y = 60;

function _handleC3(container, config) {
    var init_config = {
        bindto: '#' + normalizeName(config.name),
        legend: {
            show: true
        },
        size: {
            height: config.height - WIDGET_MARGIN_Y,
            width: config.width - WIDGET_MARGIN_X
        },
        data: {
            type: config.type,
            url: config.dataSource,
            mimeType: 'json'
        },
        onrendered: function(){
            unload(container);
        }
    };
    c3.generate(init_config);
}

function _handleD3(container, config) {
    // Clean up all D3 charts in one step.
    container.selectAll('svg').remove();
    // Handle specific types.
    if(config.type === 'dendrogram') return _handleDendrogram(container, config);
    if(config.type === 'voronoi') return _handleVoronoi(container, config);
    throw new Error('Unknown type: ' + config.type);
}

function _handleRadialDendrogram(container, config) {
    // TODO
}

function _handleDendrogram(container, config) {
    var PADDING = 100;
    var width = config.width - WIDGET_MARGIN_X,
    height = config.height - WIDGET_MARGIN_Y;
    var cluster = d3.layout.cluster()
    .size([height, width - PADDING]);
    var diagonal = d3.svg.diagonal()
    .projection(function(d) { return [d.y, d.x]; });
    var svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', 'translate(40,0)');

    d3.json(config.dataSource, function(error, root) {
        if (error) throw error;

        var nodes = cluster.nodes(root),
        links = cluster.links(nodes);

        var link = svg.selectAll('.link')
        .data(links)
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', diagonal);

        var node = svg.selectAll('.node')
        .data(nodes)
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', function(d) { return 'translate(' + d.y + ',' + d.x + ')'; })

        node.append('circle').attr('r', 4.5);
        node.append('text')
        .attr('dx', function(d) { return d.children ? -8 : 8; })
        .attr('dy', 3)
        .style('text-anchor', function(d) { return d.children ? 'end' : 'start'; })
        .text(function(d) { return d.name; });

        unload(container);
    });
}

function _handleVoronoi(container, config) {
    // TODO: DO NOT USE RANDOM DATA!
    var width = config.width - WIDGET_MARGIN_X;
    var height = config.height - WIDGET_MARGIN_Y;
    var name = '#' + normalizeName(config.name);
    var vertices = d3.range(100).map(function(d) {
        return [Math.random() * width, Math.random() * height];
    });
    var voronoi = d3.geom.voronoi()
    .clipExtent([[0, 0], [width, height]]);
    // Cleanup
    var svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height);

    var path = svg.append('g').selectAll('path');

    svg.selectAll('circle')
    .data(vertices.slice(1))
    .enter().append('circle')
    .attr('transform', function(d) { return 'translate(' + d + ')'; })
    .attr('r', 1.5);

    redraw();

    function redraw() {
        path = path.data(voronoi(vertices), polygon);
        path.exit().remove();
        path.enter().append('path')
        .attr('class', function(d, i) { return 'q' + (i % 9) + '-9'; })
        .attr('d', polygon);
        path.order();
    }
    unload(container);
}

function _handleSparkline(container, config) {
    var sparkline_type = config.type.split('-')[1];
    var spark = container
        .select('div')
        .classed({'sparkline-container': true})
        .append('span');
    spark.sparkline($.getJSON(config.dataSource, function(data){
        unload(container);
    }), {type: sparkline_type});
}

function _handleDataTable(container, config) {
    // Clean up old tables if they exist, during reloading.
    container.selectAll('div').remove();
    d3.json(config.dataSource, function(error, res) {
        if (error) throw error;
        var keys = d3.keys(res[0]).map(function(d){
            return {'data': d};
        });
        container
            .append('table')
            .classed({
                'table': true,
                'table-striped': true,
                'table-bordered': true
            })
            .attr('id', config.name);
        $('#' + config.name).dataTable({
            data: res,
            columns: keys
        }).css({
            width: '100%'
        });
        unload(container);
    });
}

function _handleTimeline(container, config) {
    $.getJSON(config.dataSource, function(data){
        container.append('div').attr('id', 'widget-' + config.guid);
        var timeline = new TL.Timeline('widget-' + config.guid, data);
        unload(container);
    });
}

function _handleIframe(container, config) {
    container.selectAll('iframe').remove();
    var iframe = container.append('iframe');
    iframe.attr({
        border: 0,
        src: config.dataSource,
        height: '100%',
        width: '100%'
    });
    unload(container);
}

function _handleCustom(container, config) {
    container.selectAll('.custom-container').remove();
    $.get(config.dataSource, function(html){
        container.append('div').classed({'custom-container': true}).html(html);
        unload(container);
    });
}
