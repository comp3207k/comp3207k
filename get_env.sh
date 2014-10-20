#!/bin/bash

# Downloads the GAE SDK

wget -nc https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.13.zip

hash=$(sha1sum google_appengine_1.9.13.zip)
if [ "${hash}" != "05166691108caddc4d4cfdf683cfc4748df197a2  google_appengine_1.9.13.zip" ]; then
    echo "Download is either corrupt, or the hash has changed!";
    exit;
fi

unzip -q google_appengine_1.9.13.zip
rm google_appengine_1.9.13.zip

