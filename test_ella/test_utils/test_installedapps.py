import sys

from ella.utils.installedapps import call_modules, app_modules_loaded

from nose import tools


def test_module_loaded_and_signal_fired():
    call_modules(('loadme',))

    tools.assert_true('test_ella.test_app.loadme' in sys.modules)
    loadme = sys.modules['test_ella.test_app.loadme']
    tools.assert_equals(1, len(loadme.run_log))
    tools.assert_equals(((), {'signal': app_modules_loaded, 'sender': None}), loadme.run_log[0])
