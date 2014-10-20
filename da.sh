#!/bin/bash

# dev_appserver.py shortcut - runs the application at http://localhost:9000/

if [ -d "google_appengine" ]; then
    ./google_appengine/dev_appserver.py --port=9000 --datastore_path=./data/datastore ./src $@
else
    echo "You need to download the dev tools, run ./get_env.sh"
fi

