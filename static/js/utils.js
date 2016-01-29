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
    return name.replace(/#/gi, '').replace(/\./gi, '').replace(/ /gi, '_');
}
