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

describe('isD3Subtype', function(){
    it('should recognize the correct d3 subtypes', function(){
        expect(jsondash.util.isD3Subtype({type: 'dendrogram'})).toBe(true);
        expect(jsondash.util.isD3Subtype({type: 'voronoi'})).toBe(true);
        expect(jsondash.util.isD3Subtype({type: 'circlepack'})).toBe(true);
        expect(jsondash.util.isD3Subtype({type: 'treemap'})).toBe(true);
        expect(jsondash.util.isD3Subtype({type: 'radial-dendrogram'})).toBe(true);
        expect(jsondash.util.isD3Subtype({type: 'foo'})).toBe(false);
        expect(jsondash.util.isD3Subtype({type: null})).toBe(false);
    });
});

describe('isSparkline', function(){
    it('should recognize the correct sparkline type', function(){
        expect(jsondash.util.isSparkline('sparklines-foo')).toBe(true);
        expect(jsondash.util.isSparkline('smarkline-foo')).toBe(false);
    });
});

describe('getDigitSize', function(){
    it('should resize the text based on digits', function(){
        // TODO!
    });
});
