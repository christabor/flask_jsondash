/** global: jsondash */
/** global: c3 */
/** global: d3 */
/** global: venn */
/** global: Plotly */

jsondash.getJSON = function(container, url, callback) {
    if(!url) throw new Error('Invalid URL: ' + url);
    d3.json(url, function(error, data){
        if(error) {
            jsondash.unload(container);
            throw new Error("Could not load url: " + url);
        }
        callback(error, data);
    });
};

/**
 * Handlers for various widget types. The method signatures are always the same,
 * but each handler can handle them differently.
 */

jsondash.handlers.handleYoutube = function(container, config) {
    // Clean up all previous.
    'use strict';
    container.selectAll('iframe').remove();

    function getAttr(prop, props) {
        // Return the propery from a list of properties for the iframe.
        // e.g. getAttr('width', ["width="900""]) --> "900"
        return props.filter(function(k, v){
            return k.startsWith(prop);
        })[0];
    }

    var url = config.dataSource;
    var parts = config.dataSource.split(' ');
    var height = parseInt(getAttr('height', parts).split('=')[1].replace(/"/gi, ''), 10);
    var width = parseInt(getAttr('width', parts).split('=')[1].replace(/"/gi, ''), 10);
    var url = getAttr('src', parts).replace('src=', '').replace(/"/gi, '');

    // In the case of YouTube, we have to override the config dimensions
    // as this will be wonky when the aspect ratio is calculated. We will
    // defer to YouTube calculations instead.
    container.append('iframe')
        .attr('width', width)
        .attr('height', height)
        .attr('src', url)
        .attr('allowfullscreen', true)
        .attr('frameborder', 0);
    // Look for callbacks potentially registered for third party code.
    jsondash.api.runCallbacks(container, config);
    jsondash.unload(container);
};

/**
 * [handleGraph creates graphs using the dot format
 * spec with d3 and dagre-d3]
 */
jsondash.handlers.handleGraph = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config.dataSource, function(error, data){
        container.selectAll('.chart-graph').remove();
        var h = config.height - jsondash.config.WIDGET_MARGIN_Y;
        var w = config.width - jsondash.config.WIDGET_MARGIN_X;
        var svg = container.append('svg').classed({'chart-graph': true});
        var svg_group = svg.append('g');
        var g = graphlibDot.read(data.graph);
        var bbox = null;
        // Create the renderer
        var render = new dagreD3.render();
        render(svg_group, g);
        bbox = svg.node().getBBox();
        svg.attr('width', bbox.width)
            .attr('height', bbox.height);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

/**
 * [handleWordCloud create word clouds using the d3-cloud extension.]
 */
jsondash.handlers.handleWordCloud = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config.dataSource, function(error, data){
        container.selectAll('.wordcloud').remove();
        var h     = config.height - jsondash.config.WIDGET_MARGIN_Y;
        var w     = config.width - jsondash.config.WIDGET_MARGIN_X;
        var svg   = container.append('svg').classed({'wordcloud': true});
        var fill  = d3.scale.category20();
        var cloud = d3.layout.cloud;
        var words = data.map(function(d) {
            return {text: d.text, size: d.size};
        });
        var layout = cloud()
            .size([w, h])
            .words(words)
            .padding(4)
            .rotate(function() {return ~~(Math.random() * 1) * 90;})
            .font('Arial')
            .fontSize(function(d) {return d.size;})
            .on('end', draw);

        layout.start();

        function draw(words) {
          svg
              .attr('width', layout.size()[0])
              .attr('height', layout.size()[1])
            .append('g')
              .attr('transform', 'translate(' + layout.size()[0] / 2 + ',' + layout.size()[1] / 2 + ')')
            .selectAll('text').data(words)
            .enter().append('text')
              .style('font-size', function(d) { return d.size + 'px'; })
              .style('font-family', 'arial')
              .style('fill', function(d, i) { return "#000"; })
              .attr('text-anchor', 'middle')
              .attr('transform', function(d) {
                return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')';
              })
              .text(function(d) { return d.text; });
        }

        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleC3 = function(container, config) {
    'use strict';
    var init_config = {
        bindto: '[data-guid="' + config.guid + '"] .chart-container',
        legend: {
            show: true
        },
        size: {
            height: config.height - jsondash.config.WIDGET_MARGIN_Y,
            width: config.width - jsondash.config.WIDGET_MARGIN_X
        },
        data: {
            type: config.type,
            url: config.dataSource,
            mimeType: 'json'
        },
        onrendered: function(){
            // Look for callbacks potentially registered for third party code.
            jsondash.api.runCallbacks(container, config);
            jsondash.unload(container);
        }
    };
    if(jsondash.util.isOverride(config)) {
        // Just use the raw payload for this widgets' options.
        jsondash.getJSON(container, config.dataSource, function(error, data){
            // Keep existing options if not specified.
            config = $.extend(init_config, data);
            c3.generate(init_config);
        });
        return;
    }
    if(config.type === 'timeseries') {
        init_config.axis = {
            x: {type: 'timeseries'}
        };
        // Map the corresponding data key and list of dates
        // to the `x` property.
        init_config.data.x = 'dates';
    }
    c3.generate(init_config);
};

jsondash.handlers.handleD3 = function(container, config) {
    'use strict';
    // Clean up all D3 charts in one step.
    container.selectAll('svg').remove();
    // Handle specific types.
    if(config.type === 'radial-dendrogram') { return jsondash.handlers.handleRadialDendrogram(container, config); }
    if(config.type === 'dendrogram') { return jsondash.handlers.handleDendrogram(container, config); }
    if(config.type === 'voronoi') { return jsondash.handlers.handleVoronoi(container, config); }
    if(config.type === 'treemap') { return jsondash.handlers.handleTreemap(container, config); }
    if(config.type === 'circlepack') { return jsondash.handlers.handleCirclePack(container, config); }
    throw new Error('Unknown type: ' + config.type);
};

jsondash.handlers.handleCirclePack = function(container, config) {
    'use strict';
    // Adapted from https://bl.ocks.org/mbostock/4063530
    var margin = jsondash.config.WIDGET_MARGIN_Y;
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

    jsondash.getJSON(container, config.dataSource, function(error, data) {
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
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });

    d3.select(self.frameElement).style("height", diameter + "px");
};

jsondash.handlers.handleTreemap = function(container, config) {
    'use strict';
    // Adapted from http://bl.ocks.org/mbostock/4063582
    var margin = {
        top: jsondash.config.WIDGET_MARGIN_Y / 2,
        bottom: jsondash.config.WIDGET_MARGIN_Y / 2,
        left: jsondash.config.WIDGET_MARGIN_X / 2,
        right: jsondash.config.WIDGET_MARGIN_X / 2
    };
    var width = config.width - jsondash.config.WIDGET_MARGIN_X;
    var height = config.height - jsondash.config.WIDGET_MARGIN_Y;
    var color = d3.scale.category20c();
    var treemap = d3.layout.treemap()
        .size([width, height])
        .sticky(true)
        .value(function(d) { return d.size; });
    // Cleanup
    container.selectAll('.treemap').remove();
    var div = container
        .append('div')
        .classed({treemap: true, 'chart-centered': true})
        .style('position', 'relative')
        .style('width', width + 'px')
        .style('height', height + 'px');

    jsondash.getJSON(container, config.dataSource, function(error, root) {
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
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });

    function position() {
        this.style('left', function(d) { return d.x + 'px'; })
            .style('top', function(d) { return d.y + 'px'; })
            .style('width', function(d) { return Math.max(0, d.dx - 1) + 'px'; })
            .style('height', function(d) { return Math.max(0, d.dy - 1) + 'px'; });
    }
};

jsondash.handlers.handleRadialDendrogram = function(container, config) {
    'use strict';
    container.selectAll('svg').remove();
    // Code taken (and refactored for use here) from:
    // https://bl.ocks.org/mbostock/4339607
    var padding = 50;
    var radius = (config.width > config.height ? config.width : config.height) - padding;
    var cluster = d3.layout.cluster()
        .size([360, radius / 2 - 150]); // reduce size relative to `radius`
    var diagonal = d3.svg.diagonal.radial()
        .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
    var svg = container.append('svg')
        .attr('width', radius)
        .attr('height', radius);
    var g = svg.append('g');
    g.attr('transform', 'translate(' + radius / 2 + ',' + radius / 2 + ')');

    jsondash.getJSON(container, config.dataSource, function(error, root) {
        if (error) { throw error; }
        var nodes = cluster.nodes(root);
        var link = g.selectAll('path.link')
            .data(cluster.links(nodes))
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', diagonal);
        var node = g.selectAll('g.node')
            .data(nodes)
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', function(d) { return 'rotate(' + (d.x - 90) + ')translate(' + d.y + ')'; });
        node.append('circle')
            .attr('r', 4.5);
        node.append('text')
            .attr('dy', '.31em')
            .attr('text-anchor', function(d) { return d.x < 180 ? 'start' : 'end'; })
            .attr('transform', function(d) { return d.x < 180 ? 'translate(8)' : 'rotate(180)translate(-8)'; })
            .text(function(d) { return d.name; });
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
    d3.select(self.frameElement).style('height', radius * 2 + 'px');
};

jsondash.handlers.handleDendrogram = function(container, config) {
    'use strict';
    container.selectAll('svg').remove();
    // A general padding for the svg inside of the widget.
    // The cluster dendrogram will also need to have padding itself, so
    // the bounds are not clipped in the svg.
    var svg_pad = 20;
    var width = config.width - svg_pad;
    var height = config.height - svg_pad;
    var PADDING = width / 4;
    var cluster = d3.layout.cluster()
        .size([height * 0.85, width - PADDING]);
    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });
    var svg = container
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    var g = svg.append('g')
        .attr('transform', 'translate(40, 0)');

    jsondash.getJSON(container, config.dataSource, function(error, root) {
        var nodes = cluster.nodes(root);
        var links = cluster.links(nodes);
        var link = g.selectAll('.link')
        .data(links)
        .enter().append('path')
        .attr('class', 'link')
        .attr('d', diagonal);

        var node = g.selectAll('.node')
        .data(nodes)
        .enter().append('g')
        .attr('class', 'node')
        .attr('transform', function(d) { return 'translate(' + d.y + ',' + d.x + ')'; });

        node.append('circle').attr('r', 4.5);
        node.append('text')
        .attr('dx', function(d) { return d.children ? -8 : 8; })
        .attr('dy', 3)
        .style('text-anchor', function(d) { return d.children ? 'end' : 'start'; })
        .text(function(d) { return d.name; });

        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleVoronoi = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config.dataSource, function(error, data){
        var width = config.width - jsondash.config.WIDGET_MARGIN_X;
        var height = config.height - jsondash.config.WIDGET_MARGIN_Y;
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
            path = path.data(voronoi(vertices), jsondash.util.polygon);
            path.exit().remove();
            path.enter().append('path')
            .attr('class', function(d, i) { return 'q' + (i % 9) + '-9'; })
            .attr('d', jsondash.util.polygon);
            path.order();
        }
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleSparkline = function(container, config) {
    'use strict';
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
    jsondash.getJSON(container, config.dataSource, function(data){
        var opts = {
            type: sparkline_type,
            width: config.width - jsondash.config.WIDGET_MARGIN_X,
            height: config.height - jsondash.config.WIDGET_MARGIN_Y
        };
        spark.sparkline(data, opts);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleDataTable = function(container, config) {
    'use strict';
    // Clean up old tables if they exist, during reloading.
    container.selectAll('.dataTables_wrapper').remove();
    jsondash.getJSON(container, config.dataSource, function(error, res) {
        var keys = d3.keys(res[0]).map(function(d){
            return {data: d, title: d};
        });
        container
            .append('table')
            .classed({
                table: true,
                'table-striped': true,
                'table-bordered': true,
                'table-condensed': true
            });
        var opts = config.override ? res : {data: res, columns: keys};
        $(container.select('table')[0]).dataTable(opts).css({width: 'auto'});
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleSingleNum = function(container, config) {
    'use strict';
    container.selectAll('.singlenum').remove();
    jsondash.getJSON(container, config.dataSource, function(resp){
        var data = resp.data.data ? resp.data.data : resp.data;
        var num = container.select('.chart-container').append('div')
            .classed({singlenum: true})
            .text(data);
        data = String(data);
        // Add red or green, depending on if the number appears to be pos/neg.
        if(!resp.noformat) {
            num.classed({
                'text-danger': data.startsWith('-'),
                'text-success': !data.startsWith('-')
            });
        }
        // Allow custom colors.
        if(resp.color && resp.noformat) {
            num.style('color', resp.color);
        }
        // Get title height to offset box.
        var title_h = container
            .select('.widget-title')
            .node()
            .getBoundingClientRect()
            .height;
        var h = config.height - jsondash.config.WIDGET_MARGIN_Y;
        num.style({
            'line-height': h + 'px',
            height: h + 'px',
            width: config.width - jsondash.config.WIDGET_MARGIN_X
        });
        var digits = String(data).length;
        var size = jsondash.util.getDigitSize()(digits);
        num.style('font-size', size + 'px');
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleTimeline = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config.dataSource, function(data){
        container.append('div').attr('id', 'widget-' + config.guid);
        var timeline = new TL.Timeline('widget-' + config.guid, data);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleIframe = function(container, config) {
    'use strict';
    container.selectAll('iframe').remove();
    var iframe = container.append('iframe');
    iframe.attr({
        border: 0,
        src: config.dataSource,
        height: config.height - jsondash.config.WIDGET_MARGIN_Y,
        width: config.width - jsondash.config.WIDGET_MARGIN_X
    });
    // Look for callbacks potentially registered for third party code.
    jsondash.api.runCallbacks(container, config);
    jsondash.unload(container);
};

jsondash.handlers.handleCustom = function(container, config) {
    'use strict';
    container.selectAll('.custom-container').remove();
    $.get(config.dataSource, function(html){
        container.append('div').classed({'custom-container': true}).html(html);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleVenn = function(container, config) {
    'use strict';
    container.selectAll('.venn').remove();
    jsondash.getJSON(container, config.dataSource, function(error, data){
        var chart = venn.VennDiagram();
        var cont = container
            .append('div')
            .classed({venn: true});
        cont.datum(data).call(chart);
        cont.select('svg')
            .attr('width', config.width - jsondash.config.WIDGET_MARGIN_X)
            .attr('height', config.height - jsondash.config.WIDGET_MARGIN_Y);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handlePlotly = function(container, config) {
    'use strict';
    var id = 'plotly-' + config.guid;
    container.selectAll('.plotly-container').remove();
    container.append('div')
        .classed({'plotly-container': true})
        .attr('id', id);
    jsondash.getJSON(container, config.dataSource, function(error, data){
        if(config.override) {
            if(data.layout && data.layout.margin) {
                // Remove margins, they mess up the
                // layout and are already accounted for.
                delete data.layout['margin'];
            }
            Plotly.plot(id, data.data, data.layout || {}, data.options || {});
        } else {
            Plotly.plot(id, data);
        }
        d3.select('#' + id).select('.svg-container').style({'margin': '0 auto'})
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};
