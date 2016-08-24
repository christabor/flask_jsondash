/**
 * Utility functions.
 */

function serializeToJSON(arr) {
    // Convert form data to a proper json value
    var json = {};
    $.each(arr, function(_, pair){
        json[pair.name] = pair.value;
    });
    return json;
}

// Credit: http://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);
}

function guid() {
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

function normalizeName(name) {
    if(!name) return 'id_NONAME_' + s4();
    // Credit: http://stackoverflow.com/questions/4328500/
    // how-can-i-strip-all-punctuation-from-a-string-in-javascript-using-regex
    name = name.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"");
    // Reformat it for ID use.
    return 'id_' + name.replace(/#/gi, '').replace(/ /gi, '_');
}

function polygon(d) {
    return "M" + d.join("L") + "Z";
}

function isD3Subtype(config) {
    // Handle specific D3 types that aren't necessarily referenced under
    // the D3 namespace in a select field.
    if(config.type === 'dendrogram') return true;
    if(config.type === 'voronoi') return true;
    if(config.type === 'circlepack') return true;
    if(config.type === 'treemap') return true;
    if(config.type === 'radial-dendrogram') return true;
    return false;
}

function isSparkline(type) {
    return type.substr(0, 10) === 'sparklines';
}

/**
 * [getDigitSize return a d3 scale for adjusting font size based
 *     on digits and width of container.]
 */
function getDigitSize() {
    var BOX_PADDING = 20;
    // scale value is reversed, since we want
    // the font-size to get smaller as the number gets longer.
    var scale = d3.scale.linear()
        .clamp(true)
        .domain([2, 14]) // min/max digits length: $0 - $999,999,999.00
        .range([90, 30]); // max/min font-size
    window.scale = scale;
    return scale;
}
