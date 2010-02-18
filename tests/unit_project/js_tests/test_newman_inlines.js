//nosejs.requireResource("jquery-1.3.1.js");
/*nosejs.requireFile("../../../ella/newman/media/jquery/jquery-1.3.2.js");
nosejs.requireFile("../../../ella/newman/media/jquery/jquery-ui.js");
nosejs.requireResource("jquery/qunit-testrunner.js");

nosejs.requireFile("../../../ella/newman/media/js/inlines.js");*/
if (typeof nosejs !== "undefined") {
    nosejs.requireResource("jquery-1.3.1.js");
    nosejs.requireResource("jquery/qunit-testrunner.js");
    nosejs.requireFile("case.js"); //TestCase namespace definition

    nosejs.requireFile("../../../ella/newman/media/js/kobayashi.js");
    nosejs.requireFile("../../../ella/newman/media/js/newman.js");
    nosejs.requireFile("../../../ella/newman/media/js/inlines.js");
}
////////////////////////

DummyFormHandler = new Object();
TestCase.init('Gallery Form Handler');

TestCase.set_up = function () {
    NewmanInline.clean_handler_registry();

    // DummyFormHandler
    (function () {
        function is_suitable() {
            return false;
        }
        DummyFormHandler.is_suitable = is_suitable;

        function init() {
        }
        DummyFormHandler.init = init;

        function preset_load_initiated(evt, preset) {
        }
        DummyFormHandler.preset_load_initiated = preset_load_initiated;

        function preset_load_completed(evt) {
        }
        DummyFormHandler.preset_load_completed = preset_load_completed;

        function validate_form($form) {
            return true;
        }
        DummyFormHandler.validate_form = validate_form;

        function add_inline_item(evt) {
        }
        DummyFormHandler.add_inline_item = add_inline_item;
    })();
};

TestCase.test_newman_inline = function() {
    NewmanInline.register_form_handler(DummyFormHandler);
    var reg = NewmanInline.get_handler_registry();
    equals(1, reg.length);
    equals(DummyFormHandler, reg[0]);
};
// Run all tests..
TestCase.run();
