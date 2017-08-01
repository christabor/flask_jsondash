/** global: jsondash */
/** global: c3 */
/** global: d3 */
/** global: venn */
/** global: Plotly */

jsondash.handleRes = function(error, data, container) {
    var err_msg = '';
    if(error) {
        err_msg = 'Error: ' + error.status + ' ' + error.statusText;
    }
    else if(!data) {
        err_msg = 'No data was found (invalid response).';
    }
    if(error || !data) {
        container.classed({error: true});
        container.select('.error-overlay')
            .classed({hidden: false})
            .select('.alert')
            .text(err_msg);
        jsondash.unload(container);
    }
};
jsondash.getJSON = function(container, config, callback) {
    var url     = config.dataSource;
    var cached  = config.cachedData;
    var err_msg = null;
    if(!url) throw new Error('Invalid URL: ' + url);
    if(cached && cached !== null && cached !== undefined) {
        // Ensure this is not re-used for this cycle. It's somewhat of a pseudo-cache in that sense.
        config.cachedData = null;
        return callback(null, cached);
    }
    d3.json(url, function(error, data){
        jsondash.handleRes(error, data, container);
        if(error || !data) {
            return;
        }
        callback(error, config.key && data.multicharts[config.key] ? data.multicharts[config.key] : data);
    });
};


/**
 * [getTitleBarHeight Return the height for a chart containers titlebar,
 *     plus any other computed box model properties.
 */
jsondash.getTitleBarHeight = function(container) {
    var titlebar = container.select('.widget-title');
    var titlebar_height = titlebar.node().getBoundingClientRect().height;
    var titlebar_padding = parseInt(titlebar.style('padding-bottom').replace('px', ''), 10);
    return titlebar_height + titlebar_padding;
};

/**
 * [getDynamicWidth Return the width for a container that has no specified width
 * (e.g. grid mode)]
 */
jsondash.getDynamicWidth = function(container, config) {
    if(isNaN(config.width)) {
        return d3.round(container.node().getBoundingClientRect().width);
    }
    return parseInt(config.width, 10);
};


/**
 * [getDiameter Calculate a valid diameter for a circular widget,
 * based on width/height to ensure the size never goes out of the container bounds.]
 */
jsondash.getDiameter = function(container, config) {
    var width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    return d3.min([d3.round(width), config.height]);
};

/**
 * Handler for all sigma.js specifications
 */
jsondash.handlers.handleSigma = function(container, config) {
    'use strict';
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    // Titlebar + padding + a bit extra to account for the bottom.
    var titlebar_offset = jsondash.getTitleBarHeight(container) * 1.2;
    // Sigmajs just assumes an ID for the querySelector, so we need to add one
    // to the child container.
    var new_id = 'sigma-' + jsondash.util.guid();
    var width = (_width - 10) + 'px';
    var height = (config.height - titlebar_offset) + 'px';
    container
        .select('.chart-container')
        .attr('id', new_id)
        .classed(jsondash.util.getCSSClasses(config))
        .style({
        width: width,
        height: height
    });
    jsondash.getJSON(container, config, function(error, data){
        var sig = new sigma({
          graph: data,
          width: width,
          height: height,
          container: new_id
        });
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

/**
 * [handleFlameGraph handler for flameGraph plugin]
 */
jsondash.handlers.handleFlameGraph = function(container, config) {
    jsondash.getJSON(container, config, function(_, data){
        var padding = 60;
        var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
        var flamegraph = d3.flameGraph()
            .width(_width - padding)
            .height(config.height - padding);
        container.datum(data).call(flamegraph);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

/**
 * Handler for all cytoscape specifications
 */
jsondash.handlers.handleCytoscape = function(container, config) {
    'use strict';
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    // Titlebar + padding + a bit extra to account for the bottom.
    var titlebar_offset = jsondash.getTitleBarHeight(container) * 1.2;
    container
        .select('.chart-container')
        .classed(jsondash.util.getCSSClasses(config))
        .style({
        width: (_width - 10) + 'px',
        height: (config.height - titlebar_offset) + 'px'
    });
    jsondash.getJSON(container, config, function(error, cyspec){
        // the `document.getElementByID` declaration in the cytoscape
        // spec is not serializable so we will ignore anything user
        // sent and just drop our selector in place of it.
        var override = {
            container: document.querySelector('[data-guid="' + config.guid + '"] .chart-container'),
            // We intentionally override w/h with null values,
            // so the graph is forced to be
            // constrained to the parent dimensions.
            layout: {
                width: null,
                height: null
            },
        };
        var spec = $.extend(cyspec, override);
        var cy = cytoscape(spec);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

/**
 * Handler for all vega-lite specifications
 */
jsondash.handlers.handleVegaLite = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config, function(error, vlspec){
        var SCALE_FACTOR = 0.7; // very important to get sizing jusst right.
        var selector = '[data-guid="' + config.guid + '"] .chart-container';
        var width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
        var size = d3.max([config.height, width]);
        var overrides = {
            width: ~~(size * SCALE_FACTOR),
            height: ~~(config.height * SCALE_FACTOR)
        };
        var embedSpec = {
            mode: 'vega-lite',
            spec: $.extend({}, vlspec, overrides)
        };
        d3.select(selector).classed(jsondash.util.getCSSClasses(config))
        vg.embed(selector, embedSpec, function(error, result) {
            // Callback receiving the View instance and parsed Vega spec
            // result.view is the View, which resides under the '#vis' element
            if(error) {
                throw new Error('Error loading chart: ' + error);
            }
            // Change look of default buttons
            container.select('.vega-actions')
                .classed({'btn-group': true})
                .selectAll('a')
                .classed({'btn btn-xs btn-default': true});
            // Look for callbacks potentially registered for third party code.
            jsondash.api.runCallbacks(container, config);
            jsondash.unload(container);
        });
    });
};

/**
 * Handlers for various widget types. The method signatures are always the same,
 * but each handler can handle them differently.
 */
jsondash.handlers.handleYoutube = function(container, config) {
    // Clean up all previous.
    'use strict';
    function getAttr(prop, props) {
        // Return the propery from a list of properties for the iframe.
        // e.g. getAttr('width', ["width="900""]) --> "900"
        return props.filter(function(k, v){
            return k.startsWith(prop);
        })[0];
    }


    var url = config.dataSource;
    var parts = config.dataSource.split(' ');
    var yt_width = parseInt(getAttr('width', parts).split('=')[1].replace(/"/gi, ''), 10);
    var height = parseInt(getAttr('height', parts).split('=')[1].replace(/"/gi, ''), 10);
    var width = isNaN(config.width) ? '100%' : yt_width;
    var url = getAttr('src', parts).replace('src=', '').replace(/"/gi, '');

    // In the case of YouTube, we have to override the config dimensions
    // as this will be wonky when the aspect ratio is calculated. We will
    // defer to YouTube calculations instead.
    container
        .select('.chart-container')
        .append('iframe')
        .classed(jsondash.util.getCSSClasses(config))
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
    jsondash.getJSON(container, config, function(error, data){
        var h = config.height - jsondash.config.WIDGET_MARGIN_Y;
        var w = config.width - jsondash.config.WIDGET_MARGIN_X;
        var svg = container
            .select('.chart-container')
            .append('svg')
            .classed(jsondash.util.getCSSClasses(config))
            .classed({'chart-graph': true});
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
    jsondash.getJSON(container, config, function(error, data){
        var h     = config.height - jsondash.config.WIDGET_MARGIN_Y;
        var w     = config.width - jsondash.config.WIDGET_MARGIN_X;
        var svg   = container
            .select('.chart-container')
            .append('svg')
            .classed(jsondash.util.getCSSClasses(config))
            .classed({'wordcloud': true});
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
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    'use strict';
    var init_config = {
        bindto: '[data-guid="' + config.guid + '"] .chart-container',
        legend: {
            show: true
        },
        size: {
            height: config.height - jsondash.config.WIDGET_MARGIN_Y,
            width: _width - jsondash.config.WIDGET_MARGIN_X
        },
        data: {},
        onrendered: function(){
            // Look for callbacks potentially registered for third party code.
            jsondash.api.runCallbacks(container, config);
            jsondash.unload(container);
        }
    };

    container
        .select('.chart-container')
        .classed(jsondash.util.getCSSClasses(config))

    /**
     * [normalizeData Transform data from a standardized jsondash
     *     format into one suitable for c3.]
     */
    function normalizeData(data, type) {
        // For most cases, we build out N columns into ['label', 0, 1, 2, 3] format
        // from data in format: {'foo': [1, 2]} or format {'foo': 1}
        var cols = [];
        if(type === 'donut' || type === 'gauge' || type === 'pie') {
            $.each(data, function(label, val){
                cols.push([label, val]);
            });
            return cols;
        }
        if(type === 'timeseries') {
            var dates = ['x'];
            data.dates.map(function(date, _){
                dates.push(date);
            });
            cols.push(dates);
        }
        $.each(data, function(label, vals){
            if(label !== 'dates') {
                var newarr = [label];
                vals.map(function(val, _){
                    newarr.push(val);
                });
                cols.push(newarr);
            }
        });
        return cols;
    }

    jsondash.getJSON(container, config, function(error, data){
        if(jsondash.util.isOverride(config)) {
            // Just use the raw payload for this widgets' options.
            // Keep existing options if not specified.
            init_config = $.extend(init_config, data);
        } else {
            if(config.type === 'timeseries') {
                // Map the corresponding data key and list of dates
                // to the `x` property.
                init_config.axis = {
                    x: {type: 'timeseries'}
                };
                init_config.data.x = 'x';
            } else {
                init_config.data.type = config.type;
            }
            init_config.data.columns = normalizeData(data, config.type);
        }
        c3.generate(init_config);
    });
};

jsondash.handlers.handleBasic = function(container, config) {
    'use strict';
    if(config.type === 'numbergroup') { return jsondash.handlers.handleNumbersGroup(container, config); }
    if(config.type === 'number') { return jsondash.handlers.handleSingleNum(container, config); }
    if(config.type === 'iframe') { return jsondash.handlers.handleIframe(container, config); }
    if(config.type === 'image') { return jsondash.handlers.handleImage(container, config); }
    if(config.type === 'youtube') { return jsondash.handlers.handleYoutube(container, config); }
    if(config.type === 'custom') { return jsondash.handlers.handleCustom(container, config); }
};

jsondash.handlers.handleD3 = function(container, config) {
    'use strict';
    // Handle specific types.
    if(config.type === 'radial-dendrogram') { return jsondash.handlers.handleRadialDendrogram(container, config); }
    if(config.type === 'dendrogram') { return jsondash.handlers.handleDendrogram(container, config); }
    if(config.type === 'voronoi') { return jsondash.handlers.handleVoronoi(container, config); }
    if(config.type === 'treemap') { return jsondash.handlers.handleTreemap(container, config); }
    if(config.type === 'circlepack') { return jsondash.handlers.handleCirclePack(container, config); }
};

jsondash.handlers.handleCirclePack = function(container, config) {
    'use strict';
    // Adapted from https://bl.ocks.org/mbostock/4063530
    var margin = jsondash.config.WIDGET_MARGIN_Y;
    var diameter = jsondash.getDiameter(container, config) - margin;
    var format = d3.format(',d');
    var pack = d3.layout.pack()
        .size([diameter, diameter])
        .value(function(d) { return d.size; });
    var svg = container
        .select('.chart-container')
        .append('svg')
        .classed(jsondash.util.getCSSClasses(config))
        .attr('width', diameter)
        .attr('height', diameter)
        .append('g');

    jsondash.getJSON(container, config, function(error, data) {
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
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    var width = _width - jsondash.config.WIDGET_MARGIN_X;
    var height = config.height - jsondash.config.WIDGET_MARGIN_Y;
    var color = d3.scale.category20c();
    var treemap = d3.layout.treemap()
        .size([width, height])
        .sticky(true)
        .value(function(d) { return d.size; });
    var div = container
        .select('.chart-container')
        .append('div')
        .classed(jsondash.util.getCSSClasses(config))
        .classed({treemap: true, 'chart-centered': true})
        .style('position', 'relative')
        .style('width', width + 'px')
        .style('height', height + 'px');

    jsondash.getJSON(container, config, function(error, root) {
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
    // Code taken (and refactored for use here) from:
    // https://bl.ocks.org/mbostock/4339607
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    var radius = jsondash.getDiameter(container, config);
    var cluster = d3.layout.cluster()
        .size([360, radius / 2 - 150]); // reduce size relative to `radius`
    var diagonal = d3.svg.diagonal.radial()
        .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
    var svg = container
        .select('.chart-container')
        .append('svg')
        .classed(jsondash.util.getCSSClasses(config))
        .attr('width', radius)
        .attr('height', radius);
    var g = svg.append('g');
    g.attr('transform', 'translate(' + radius / 2 + ',' + radius / 2 + ')');

    jsondash.getJSON(container, config, function(error, root) {
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
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    // A general padding for the svg inside of the widget.
    // The cluster dendrogram will also need to have padding itself, so
    // the bounds are not clipped in the svg.
    var svg_pad = 20;
    var width = _width - svg_pad;
    var height = config.height - svg_pad;
    var PADDING = width / 4;
    var cluster = d3.layout.cluster()
        .size([height * 0.85, width - PADDING]);
    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });
    var svg = container
        .select('.chart-container')
        .append('svg')
        .classed(jsondash.util.getCSSClasses(config))
        .attr('width', width)
        .attr('height', height);
    var g = svg.append('g')
        .attr('transform', 'translate(40, 0)');

    jsondash.getJSON(container, config, function(error, root) {
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
    jsondash.getJSON(container, config, function(error, data){
        var _width   = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
        var width    = _width - jsondash.config.WIDGET_MARGIN_X;
        var height   = config.height - jsondash.config.WIDGET_MARGIN_Y;
        var vertices = data;
        var voronoi  = d3.geom.voronoi().clipExtent([[0, 0], [width, height]]);
        var svg = container
            .select('.chart-container')
            .append('svg')
            .classed(jsondash.util.getCSSClasses(config))
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
    var sparkline_type = config.type.split('-')[1];
    var spark = container
        .select('.chart-container')
        .append('div')
        .classed(jsondash.util.getCSSClasses(config))
        .classed({
            'sparkline-container': true,
            'text-center': true
        });
    spark = $(spark[0]);
    jsondash.getJSON(container, config, function(data){
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
    jsondash.getJSON(container, config, function(error, res) {
        var keys = d3.keys(res[0]).map(function(d){
            return {data: d, title: d};
        });
        var titlebar_offset = jsondash.getTitleBarHeight(container) * 2.5;
        var table_class_defaults = ['table', 'table-bordered', 'table-striped'];
        var classes = jsondash.util.getCSSClasses(config, table_class_defaults);
        container
            .select('.chart-container')
            .append('table')
            .classed(classes);
        var opts = config.override ? res : {data: res, columns: keys};
        $(container.select('table')[0])
            .dataTable(opts).css({
                width: 'auto',
        });
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleNumbersGroup = function(container, config) {
    'use strict';
    var scale = d3.scale.linear()
        .clamp(true)
        .domain([1, 20]) // min/max digits length
        .range([80, 30]); // max/min font-size

    function getStylesForColumn(d) {
        var digits = String(d.data).length + String(d.units ? d.units : '').length;
        var size = ~~scale(digits);
        var styles = 'font-size: ' + size + 'px;';
        if(d.color && d.noformat !== false) {
            styles += 'color: ' + d.color + ';';
        }
        return styles;
    }

    jsondash.getJSON(container, config, function(error, data){
        container
        .select('.chart-container')
        .append('table')
        .classed({numgroup: true, 'table': true})
        .classed(jsondash.util.getCSSClasses(config))
        .append('tr')
        .selectAll('td')
        .data(data)
        .enter()
        .append('td')
        .attr('width', function(d, i){
            return d.width !== null && d.width !== undefined ? d.width : null;
        })
        .attr('class', function(d, i){
            if(!d.noformat) {
                var classes = '';
                classes += typeof d === 'string' && d.startsWith('-') ? 'text-danger' : '';
                classes += typeof d === 'string' && !d.startsWith('-') ? 'text-success' : '';
                return classes;
            }
        })
        .html(function(d, i){
            var styles = getStylesForColumn(d);
            var title = '<p class="numgroup-title">' + d.title + '</p>';
            var units = d.units ? '<span class="numgroup-val-units"> ' + d.units + '</span>' : '';
            var num = '<h4 class="numgroup-val" style="' + styles + '">' + d.data + units + '</h4>';
            var desc = '<small class="numgroup-desc">' + (d.description ? d.description : '') + '</small>';
            return title + desc + num;
        });
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleSingleNum = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config, function(error, res){
        var data = res.data.data ? res.data.data : res.data;
        var num = container
            .select('.chart-container')
            .append('div')
            .classed({singlenum: true})
            .classed(jsondash.util.getCSSClasses(config))
            .text(data);
        data = String(data);
        // Add red or green, depending on if the number appears to be pos/neg.
        if(!res.noformat) {
            num.classed({
                'text-danger': data.startsWith('-'),
                'text-success': !data.startsWith('-')
            });
        }
        // Allow custom colors.
        if(res.color && res.noformat) {
            num.style('color', res.color);
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
    jsondash.getJSON(container, config, function(data){
        container
            .append('div')
            .classed(jsondash.util.getCSSClasses(config))
            .attr('id', 'widget-' + config.guid);
        var timeline = new TL.Timeline('widget-' + config.guid, data);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

/**
 * [handleImage Embed an image src directly.]
 */
jsondash.handlers.handleImage = function(container, config) {
    'use strict';
    var img = container.select('.chart-container').append('img');
    var height = (config.height - jsondash.config.WIDGET_MARGIN_Y) + 'px';
    img.attr({
        src: config.dataSource,
        height: height
    });
    img.classed({img: true});
    img.classed(jsondash.util.getCSSClasses(config));
    // Look for callbacks potentially registered for third party code.
    jsondash.api.runCallbacks(container, config);
    jsondash.unload(container);
};

jsondash.handlers.handleIframe = function(container, config) {
    'use strict';
    var iframe = container
        .select('.chart-container')
        .append('iframe');
    iframe.attr({
        border: 0,
        src: config.dataSource,
        height: config.height - jsondash.config.WIDGET_MARGIN_Y,
        width: isNaN(config.width) ? '100%' : config.width - jsondash.config.WIDGET_MARGIN_X
    });
    iframe.classed(jsondash.util.getCSSClasses(config));
    // Look for callbacks potentially registered for third party code.
    jsondash.api.runCallbacks(container, config);
    jsondash.unload(container);
};

jsondash.handlers.handleCustom = function(container, config) {
    'use strict';
    $.get(config.dataSource, function(html){
        container
            .select('.chart-container')
            .append('div')
            .classed({'custom-container': true})
            .classed(jsondash.util.getCSSClasses(config))
            .html(html);
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};

jsondash.handlers.handleVenn = function(container, config) {
    'use strict';
    jsondash.getJSON(container, config, function(error, data){
        var chart = venn.VennDiagram();
        var cont = container
            .select('.chart-container')
            .append('div')
            .classed(jsondash.util.getCSSClasses(config))
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
    var _width = isNaN(config.width) ? jsondash.getDynamicWidth(container, config) : config.width;
    container
        .select('.chart-container')
        .append('div')
        .classed(jsondash.util.getCSSClasses(config))
        .classed({'plotly-container': true})
        .attr('id', id);
    jsondash.getJSON(container, config, function(error, data){
        var plotly_wrapper =  d3.select('#' + id);
        delete data.layout.height;
        delete data.layout.width;
        data.layout.margin = {l: 20, r: 20, b: 20, t: 50};
        if(config.override) {
            Plotly.plot(id, data.data, data.layout || {}, data.options || {});
        } else {
            Plotly.plot(id, data);
        }
       plotly_wrapper.select('.svg-container').style({
            'margin': '0 auto',
            'width': isNaN(config.width) ? '100%' : config.width,
            'height': config.height
        });
        plotly_wrapper.select('#scene').style({
            'width': _width,
            'height': config.height
        });
        // Look for callbacks potentially registered for third party code.
        jsondash.api.runCallbacks(container, config);
        jsondash.unload(container);
    });
};
