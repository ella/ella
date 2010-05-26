// Object inheritance
/*
Inspired by articles by Daniel Steigerwald on http://zdrojak.root.cz/clanky/oop-v-javascriptu-iii/

Classes can be defined in matter of following example:

var __Person = function() {
    var me = {};
    function init(name) {
        this.name = name;
    }
    me.init =  init;

    function getName() {
        return this.name;
    }
    me.getName = getName;
    return me;
};
var Person = create_class_from_throttle_function(__Person);

var __Employee = function() {
    var me  = {};
    me.super_class = Person; // inheritance
    
    function init(name, salary) {
        Person.call(this, name);
        this.salary = salary;
    }
    me.init =  init;

    function getName() {
        var name = Employee._super.getName.call(this);
        return name + ' (zaměstnanec)';
    }
    me.getName = getName;

    me.getSalary = function() {
        return this.salary;
    };
    return me;
};
var Employee = create_class_from_throttle_function(__Employee);

var joe = new Employee('Joe', 1000);
alert([
    
    joe.getName() == 'Joe (zaměstnanec)',
    joe.getSalary() == 1000,

    joe instanceof Person,
    joe instanceof Employee,
    
    typeof Employee == 'function',
    typeof joe == 'object',

    joe.init == Employee.prototype.init,
    Employee._super == Person.prototype

]);

*/

var EMPTY_CONSTRUCTOR = function() { };

function create_class_from_throttle_function(func) {
    var config_obj = func();
    var init = EMPTY_CONSTRUCTOR;
    if (config_obj.hasOwnProperty('init')) {
        init = config_obj.init;
    }
    if (config_obj.hasOwnProperty('super_class')) {
        var par = config_obj.super_class;
        var F = function() { };
        init._super = F.prototype = par.prototype;
        init.prototype = new F;
    }
    for (var i in config_obj) {
        if (i == 'super_class') {
            continue;
        }
        init.prototype[i] = config_obj[i];
    }
    return init;
}
var to_class = create_class_from_throttle_function; //shortcut
