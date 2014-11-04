#!/bin/bash

# Downloads the GAE SDK

wget -nc https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.14.zip

hash=$(sha1sum google_appengine_1.9.14.zip)
if [ "${hash}" != "5d58fc7414c17920281a661e66be5877bc30c379  google_appengine_1.9.14.zip" ]; then
    echo "Download is either corrupt, or the hash has changed!";
    exit;
fi

unzip -q google_appengine_1.9.14.zip
rm google_appengine_1.9.14.zip

