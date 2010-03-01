// Object inheritance patterns

// adds beget method to Object
if (typeof Object.beget !== 'function') {
     Object.beget = function (o) {
         var F = function () {};
         F.prototype = o;
         return new F();
     };
}


// super
if (typeof Object.superior !== 'function') {
    Object.superior  = function (name) {
        var that = this,
            method = that[name];
        return function (  ) {
            return method.apply(that, arguments);
        };
    };
}
