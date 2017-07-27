/**
 * Utility functions.
 */

jsondash = jsondash || {util: {}};

jsondash.util.getCSSClasses = function(conf, defaults) {
    var classes = {};
    if(conf.classes === undefined && defaults !== undefined) {
        $.each(defaults, function(i, klass){
            classes[klass] = true;
        });
        return classes;
    }
    if(conf.classes !== undefined) {
        $.each(conf.classes, function(i, klass){
            classes[klass] = true;
        });
    }
    return classes;
};

jsondash.util.getValidParamString = function(arr) {
    // Jquery $.serialize and $.serializeArray will
    // return empty query parameters, which is undesirable and can
    // be error prone for RESTFUL endpoints.
    // e.g. `foo=bar&bar=` becomes `foo=bar`
    var param_str = '';
    arr = arr.filter(function(param, i){return param.value !== '';});
    $.each(arr, function(i, param){
        param_str += (param.name + '=' + param.value);
        if(i < arr.length - 1 && arr.length > 1) param_str += '&';
    });
    return param_str;
};

/**
 * [reformatQueryParams Reformat params into a query string.]
 * @param  {[type]} old [List of query params]
 * @param  {[type]} new [List of query params]
 * @return {[type]}     [The new string (e.g. 'foo=bar&baz=1')]
        For example:
        old: foo=1&baz=1
        new: foo=2&quux=1
        expected: foo=2&quux=1&baz=1
 */
jsondash.util.reformatQueryParams = function(oldp, newp) {
    var _combined = {};
    var combined  = '';
    var oldparams = {};
    var newparams = {};
    $.each(oldp ? oldp.split('&'): [], function(i, param){
        param = param.split('=');
        oldparams[param[0]] = param[1];
    });
    $.each(newp ? newp.split('&'): [], function(i, param){
        param = param.split('=');
        newparams[param[0]] = param[1];
    });
    _combined = $.extend(oldparams, newparams);
    $.each(_combined, function(k, v){
        if(v !== undefined) {
            combined += k + '=' + v + '&';
        }
    });
    // Replace last ampersan if it exists.
    if(combined.charAt(combined.length - 1) === '&') {
        return combined.substring(0, combined.length - 1);
    }
    return combined;
};

/**
 * [isInDemoMode Check if app is in demo mode.]
 */
jsondash.util.isInDemoMode = function() {
    var parts = window.location.href.split('?');
    var matches = parts.filter(function(part, _){
        return part === 'jsondash_demo_mode=1' || part === 'jsondash_demo_mode=true';
    });
    return matches.length > 0;
};

/**
 * [intervalStrToMS Convert a string formatted to indicate an interval to milliseconds]
 * @param  {[String]} ival_fmt [The interval format string e.g. "1-d", "2-h"]
 * @return {[Number]} [The number of milliseconds]
 */
jsondash.util.intervalStrToMS = function(ival_fmt) {
    if(ival_fmt === undefined || ival_fmt === '') {
        return null;
    }
    // Just return number if it's a regular integer.
    if(!isNaN(ival_fmt)) {
        return ival_fmt;
    }
    var pieces = ival_fmt.split('-');
    var amt = parseInt(pieces[0], 10);
    if(pieces.length !== 2 || isNaN(amt) || amt === 0) {
        // Force NO value if the format is invalid.
        // This would be used to ensure the interval
        // is not set in the first place.
        return null;
    }
    var ival = pieces[1].toLowerCase();
    var ms2s = 1000;
    var ms2min = 60 * ms2s;
    var ms2hr = 60 * ms2min;
    var ms2day = 24 * ms2hr;

    // Seconds
    if(ival === 's') {
        return amt * ms2s;
    }
    // Minutes
    if(ival === 'm') {
        return amt * ms2min;
    }
    // Hours
    if(ival === 'h') {
        return amt * ms2hr;
    }
    // Days
    if(ival === 'd') {
        return amt * ms2day;
    }
    // Anything else is invalid.
    return null;
};

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

jsondash.util.scaleStr = function(x, y) {
    return 'scale(' + x + ',' + y + ')';
};

jsondash.util.translateStr = function(x, y) {
    return 'translate(' + x + ',' + y + ')';
};

/**
 * [getDigitSize return a d3 scale for adjusting font size based
 *     on digits and width of container.]
 */
jsondash.util.getDigitSize = function() {
    // scale value is reversed, since we want
    // the font-size to get smaller as the number gets longer.
    var scale = d3.scale.linear()
        .clamp(true)
        .domain([2, 14]) // min/max digits length: $0 - $999,999,999.00
        .range([90, 30]); // max/min font-size
    return scale;
};

if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = jsondash;
}
