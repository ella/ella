// TestCase namespace used to automate calling of setup and tear_down functions
// before each test_* function is called.
TestCase = new Object();
(function() {
    
    // Should be called before set_up, tear_down and test_* functions 
    // being registered.
    function init(test_module_name) {
        module(test_module_name);

        var func_name;
        for (tst in TestCase) {
            func_name = tst.toString();
            if (func_name.indexOf('test_') > -1) {
                delete TestCase.tst;
            }
        }
    }
    TestCase.init = init;

    function set_up() {
        throw new Exception('set_up Not implemented!');
    }
    TestCase.set_up = set_up;

    function tear_down() {
    }
    TestCase.tear_down = tear_down;

    function unit_test(test_description, callback) {
        TestCase.set_up();
        test(test_description, callback); // test function provided by nosejs
        TestCase.tear_down();
    }

    // runs all TestCase.test_* functions. These functions must be manualy 
    // assigned to TestCase object.
    function run() {
        var func_name;

        for (tst in TestCase) {
            func_name = tst.toString();
            if (func_name.indexOf('test_') > -1) {
                unit_test(func_name, TestCase[func_name]);
            }
        }
    }
    TestCase.run = run;

})();


