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

function guid() {
    // Credit: http://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript
    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
        .toString(16)
        .substring(1);
    }
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

function normalizeName(name) {
    return 'id_' + name.replace(/#/gi, '').replace(/\./gi, '').replace(/ /gi, '_');
}

function polygon(d) {
    return "M" + d.join("L") + "Z";
}

function isD3Subtype(config) {
    // Handle specific D3 types that aren't necessarily referenced under
    // the D3 namespace in a select field.
    if(config.type === 'dendrogram') return true;
    if(config.type === 'voronoi') return true;
    if(config.type === 'treemap') return true;
    return false;
}

function isSparkline(type) {
    return type.substr(0, 10) === 'sparklines';
}
