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
    if(config.override && config.override === true) {
        // Just use the raw payload for this widgets' options.
        $.getJSON(config.dataSource, function(res){
            // Keep existing options if not specified.
            var config = $.extend(init_config, res);
            c3.generate(init_config);
        });
        return;
    }
    if(config.type === 'timeseries') {
        init_config['axis'] = {
            x: {type: 'timeseries'},
        };
        // Map the corresponding data key and list of dates
        // to the `x` property.
        init_config['data']['x'] = 'dates';
    }
    c3.generate(init_config);
}

function _handleD3(container, config) {
    // Clean up all D3 charts in one step.
    container.selectAll('svg').remove();
    // Handle specific types.
    if(config.type === 'radial-dendrogram') return _handleRadialDendrogram(container, config);
    if(config.type === 'dendrogram') return _handleDendrogram(container, config);
    if(config.type === 'voronoi') return _handleVoronoi(container, config);
    if(config.type === 'treemap') return _handleTreemap(container, config);
    if(config.type === 'circlepack') return _handleCirclePack(container, config);
    throw new Error('Unknown type: ' + config.type);
}

function _handleCirclePack(container, config) {
    // Adapted from https://bl.ocks.org/mbostock/4063530
    var margin = WIDGET_MARGIN_Y;
    var diameter = d3.max([config.width, config.height]) - margin;
    var format = d3.format(',d');

    var pack = d3.layout.pack()
        .size([diameter, diameter])
        .value(function(d) { return d.size; });

    var svg = container
        .append('svg')
        .attr('width', diameter)
        .attr('height', diameter)
        .append('g');

    d3.json(config.dataSource, function(error, data) {
        if(error) throw new Error("Could not load url: " + config.dataSource);

        var node = svg.datum(data).selectAll('.node')
        .data(pack.nodes)
        .enter().append('g')
        .attr('class', function(d) { return d.children ? 'node' : 'leaf node'; })
        .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });

        node.append('title')
        .text(function(d) { return d.name + (d.children ? '' : ': ' + format(d.size)); });

        node.append('circle')
        .attr('r', function(d) { return d.r; });

        node.filter(function(d) { return !d.children; }).append('text')
        .attr('dy', '.3em')
        .style('text-anchor', 'middle')
        .text(function(d) { return d.name.substring(0, d.r / 3); });
        unload(container);
    });

    d3.select(self.frameElement).style("height", diameter + "px");
}

function _handleTreemap(container, config) {
    // Adapted from http://bl.ocks.org/mbostock/4063582
    var margin = {
        top: WIDGET_MARGIN_Y / 2,
        bottom: WIDGET_MARGIN_Y / 2,
        left: WIDGET_MARGIN_X / 2,
        right: WIDGET_MARGIN_X / 2
    };
    var width = config.width - WIDGET_MARGIN_X;
    var height = config.height - WIDGET_MARGIN_Y;
    var color = d3.scale.category20c();
    var treemap = d3.layout.treemap()
        .size([width, height])
        .sticky(true)
        .value(function(d) { return d.size; });
    // Cleanup
    container.selectAll('.treemap').remove();
    var div = container
        .append('div')
        .classed({'treemap': true, 'chart-centered': true})
        .style('position', 'relative')
        .style('width', width + 'px')
        .style('height', height + 'px');

    d3.json(config.dataSource, function(error, root) {
        if(error) throw new Error('Could not load url: ' + config.dataSource);
        var node = div.datum(root).selectAll('.node')
            .data(treemap.nodes)
            .enter().append('div')
            .attr('class', 'node')
            .call(position)
            .style('border', '1px solid white')
            .style('font', '10px sans-serif')
            .style('line-height', '12px')
            .style('overflow', 'hidden')
            .style('position', 'absolute')
            .style('text-indent', '2px')
            .style('background', function(d) {
                return d.children ? color(d.name) : null;
            })
            .text(function(d) {
                return d.children ? null : d.name;
            });
        d3.selectAll('input').on('change', function change() {
            var value = this.value === 'count'
            ? function() { return 1; }
            : function(d) { return d.size;};
            node
            .data(treemap.value(value).nodes)
            .transition()
            .duration(1500)
            .call(position);
        });
    });

    function position() {
        this.style('left', function(d) { return d.x + 'px'; })
            .style('top', function(d) { return d.y + 'px'; })
            .style('width', function(d) { return Math.max(0, d.dx - 1) + 'px'; })
            .style('height', function(d) { return Math.max(0, d.dy - 1) + 'px'; });
    }
}

function _handleRadialDendrogram(container, config) {
    container.selectAll('svg').remove();
    // Code taken (and refactored for use here) from:
    // https://bl.ocks.org/mbostock/4339607
    var radius = (config.width > config.height ? config.width : config.height) / 2;
    var cluster = d3.layout.cluster()
        .size([360, radius * 0.65]); // reduce size relative to `radius`
    var diagonal = d3.svg.diagonal.radial()
        .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
    var svg = container.append('svg')
        .attr('width', radius * 2)
        .attr('height', radius * 2)
        .append('g')
        .attr('transform', 'translate(' + radius + ',' + radius + ')');
    d3.json(config.dataSource, function(error, root) {
        if (error) throw error;
        var nodes = cluster.nodes(root);
        var link = svg.selectAll('path.link')
            .data(cluster.links(nodes))
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', diagonal);
        var node = svg.selectAll('g.node')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', function(d) { return 'rotate(' + (d.x - 90) + ')translate(' + d.y + ')'; })
        node.append('circle')
            .attr('r', 4.5);
        node.append('text')
            .attr('dy', '.31em')
            .attr('text-anchor', function(d) { return d.x < 180 ? 'start' : 'end'; })
            .attr('transform', function(d) { return d.x < 180 ? 'translate(8)' : 'rotate(180)translate(-8)'; })
            .text(function(d) { return d.name; });
        unload(container);
    });
    d3.select(self.frameElement).style('height', radius * 2 + 'px');
}

function _handleDendrogram(container, config) {
    container.selectAll('svg').remove();
    var PADDING = 100;
    var width = config.width - WIDGET_MARGIN_X;
    var height = config.height - WIDGET_MARGIN_Y;
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
        if(error) throw new Error('Could not load url: ' + config.dataSource);

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
    d3.json(config.dataSource, function(error, data){
        if(error) throw new Error('Could not load url: ' + config.dataSource);
        var width = config.width - WIDGET_MARGIN_X;
        var height = config.height - WIDGET_MARGIN_Y;
        var vertices = data;
        var voronoi = d3.geom.voronoi().clipExtent([[0, 0], [width, height]]);
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
    });
}

function _handleSparkline(container, config) {
    // Clean up old canvas elements
    container.selectAll('.sparkline-container').remove();
    var sparkline_type = config.type.split('-')[1];
    var spark = container
        .append('div')
        .classed({
            'sparkline-container': true,
            'text-center': true
        });
    spark = $(spark[0]);
    $.getJSON(config.dataSource, function(data){
        var opts = {
            type: sparkline_type,
            width: config.width - WIDGET_MARGIN_X,
            height: config.height - WIDGET_MARGIN_Y,
        };
        spark.sparkline(data, opts);
        unload(container);
    });
}

function _handleDataTable(container, config) {
    // Clean up old tables if they exist, during reloading.
    container.selectAll('div').remove();
    d3.json(config.dataSource, function(error, res) {
        if(error) throw new Error('Could not load url: ' + config.dataSource);
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
        }).css({width: 'auto'});
        unload(container);
    });
}

function _handleSingleNum(container, config) {
    container.selectAll('.singlenum').remove();
    $.getJSON(config.dataSource, function(data){
        var div = container.append('div')
            .attr('id', 'widget-' + config.guid);
        var num = div.append('p')
            .classed({'singlenum': true})
            .text(data);
        // Add red or green, depending on if the number appears to be pos/neg.
        num.classed({
            'text-danger': data.startsWith('-'),
            'text-success': !data.startsWith('-')
        });
        // Get title height to offset box.
        var title_h = container
            .select('.widget-title')
            .node()
            .getBoundingClientRect()
            .height;
        var inner_box_height = config.height - title_h; // factor in rough height of title.
        div.style({
            'line-height': inner_box_height + 'px',
            'height': inner_box_height + 'px'
        });
        var digits = String(data).length;
        var size = getDigitSize()(digits);
        num.style('font-size', size + 'px');
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

function _handleVenn(container, config) {
    container.selectAll('.venn').remove();
    d3.json(config.dataSource, function(error, data){
        if(error) throw new Error('Could not load url: ' + config.dataSource);
        var chart = venn.VennDiagram();
        var cont = container
            .append('div')
            .classed({'venn': true})
        cont.datum(data).call(chart);
        cont.select('svg')
            .attr('width', config.width - WIDGET_MARGIN_X)
            .attr('height', config.height - WIDGET_MARGIN_Y)
        unload(container);
    });
}
