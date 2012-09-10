from ella.utils.installedapps import app_modules_loaded
run_log = []

def handle_stuff(*args, **kwargs):
    run_log.append((args, kwargs))
app_modules_loaded.connect(handle_stuff)
