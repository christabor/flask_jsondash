var jsondash = require('../flask_jsondash/static/js/utils');

describe('serializeToJSON', function(){
    it('should serialize properly', function(){
        // TODO!
    });
});

describe('isOverride', function(){
    it('should override values', function(){
        expect(jsondash.util.isOverride({override: true})).toBe(true);
        expect(jsondash.util.isOverride({override: false})).toBe(false);
    });
});

describe('guid', function(){
    it('should generated a guid', function(){
        expect(jsondash.util.guid().length).toBe(36);
    });
});

describe('polygon', function(){
    it('should create a polygon svg string', function(){
        expect(jsondash.util.polygon(['30', '60'])).toBe('M30L60Z');
        expect(jsondash.util.polygon([])).toBe('MZ');
    });
});

describe('getDigitSize', function(){
    it('should resize the text based on digits', function(){
        // TODO!
    });
});

describe('translateStr', function(){
    it('should create the string for a svg translation value', function(){
        expect(jsondash.util.translateStr(10, 20)).toBe('translate(10,20)');
        expect(jsondash.util.translateStr('50%', '50%')).toBe('translate(50%,50%)');
    });
});

describe('scaleStr', function(){
    it('should create the string for a svg scale value', function(){
        expect(jsondash.util.scaleStr(10, 20)).toBe('scale(10,20)');
        expect(jsondash.util.scaleStr('50%', '50%')).toBe('scale(50%,50%)');
    });
});
