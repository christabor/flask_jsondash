var jsondash = require('../flask_jsondash/static/js/app');

describe('dashEvents', function(){
    it('Should recognize all events', function(){
        function testEvent(name) {
            $('body').on(name, function(e){
                console.log('Event ran: ' + name);
            });
        }
        $.each(EVENTS, function(k, name){
            testEvent(name);
        });
        // expect(jsondash.util.scaleStr('50%', '50%')).toBe('scale(50%,50%)');
    });
});
