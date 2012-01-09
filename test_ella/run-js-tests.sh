#!/bin/bash
nosetests --with-javascript-only --with-dom --rhino-jar ~/rhino1_7R2/js.jar \
--no-javascript-lint --javascript-dir js_tests/
