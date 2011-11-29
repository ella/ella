// Object inheritance
/*
Inspired by articles by Daniel Steigerwald on http://zdrojak.root.cz/clanky/oop-v-javascriptu-iii/

Classes can be defined in matter of following example:

var __Person = function() {
    function init(name) {
        this.name = name;
    }
    this.init =  init;

    function getName() {
        return this.name;
    }
    this.getName = getName;
    return this;
};
var Person = create_class_from_throttle_function(__Person);

var __Employee = function() {
    this.super_class = Person; // inheritance
    
    function init(name, salary) {
        Person.call(this, name);
        this.salary = salary;
    }
    this.init =  init;

    function getName() {
        var name = Employee._super.getName.call(this);
        return name + ' (zaměstnanec)';
    }
    this.getName = getName;

    this.getSalary = function() {
        return this.salary;
    };
    return this;
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
    var class_def = new Object();
    var config_obj = func.call(class_def);
    var init = EMPTY_CONSTRUCTOR;
    if (config_obj.hasOwnProperty('init')) {
        init = config_obj.init;
    }
    if (config_obj.hasOwnProperty('super_class')) {
        var parent_class = config_obj.super_class;
        var F = function() { };
        F.prototype = parent_class.prototype;
        init._super = parent_class.prototype;
        init.prototype = new F;
    }
    for (var member_name in config_obj) {
        if (member_name == 'super_class') {
            continue;
        }
        init.prototype[member_name] = config_obj[member_name];
    }
    class_def = null;
    config_obj = null;
    return init;
}
var to_class = create_class_from_throttle_function; //shortcut
