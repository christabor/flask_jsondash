jsondash.api = function(){
    var callbacks = {};
    var my = {};
    my.listCallbacks = function() {
        return callbacks;
    };
    my.registerCallback = function(guid, cb, args) {
        var cb_obj = {callback: cb, args: args};
        if(!callbacks[guid]) {
            callbacks[guid] = [cb_obj];
        } else {
            callbacks[guid].push(cb_obj);
        }
    }
    my.runCallbacks = function(container, config) {
        var cbs = callbacks[config.guid];
        if(cbs) {
            $.each(cbs, function(i, cb_config){
                cb_config.callback(container, config, cb_config.args);
            });
        }
    }
    return my;
}();
