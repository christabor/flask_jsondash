/**
 * Utility functions.
 */

jsondash.util.serializeToJSON = function(arr) {
    // Convert form data to a proper json value
    var json = {};
    $.each(arr, function(_, pair){
        json[pair.name] = pair.value;
    });
    return json;
};

jsondash.util.isOverride = function(config) {
    return config.override && config.override === true;
};

// Credit: http://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
jsondash.util.s4 = function() {
    return Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);
};

jsondash.util.guid = function() {
    var s4 = jsondash.util.s4;
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
};

jsondash.util.polygon = function(d) {
    return "M" + d.join("L") + "Z";
};

jsondash.util.isD3Subtype = function(config) {
    // Handle specific D3 types that aren't necessarily referenced under
    // the D3 namespace in a select field.
    if(config.type === 'dendrogram') return true;
    if(config.type === 'voronoi') return true;
    if(config.type === 'circlepack') return true;
    if(config.type === 'treemap') return true;
    if(config.type === 'radial-dendrogram') return true;
    return false;
};

jsondash.util.isSparkline = function(type) {
    return type.substr(0, 10) === 'sparklines';
};

/**
 * [getDigitSize return a d3 scale for adjusting font size based
 *     on digits and width of container.]
 */
jsondash.util.getDigitSize = function() {
    var BOX_PADDING = 20;
    // scale value is reversed, since we want
    // the font-size to get smaller as the number gets longer.
    var scale = d3.scale.linear()
        .clamp(true)
        .domain([2, 14]) // min/max digits length: $0 - $999,999,999.00
        .range([90, 30]); // max/min font-size
    window.scale = scale;
    return scale;
};
