#!/bin/bash

# Creates a ZIP file in the correct format for submission

echo "Add -noarchive to just create zip folder"

SOURCE_ARCHIVE=source.zip
ARCHIVE=comp3207.zip

if [ -d zip ]
  then
    echo "Removing old zip directory"
    rm -r zip
fi


mkdir zip

# Code from scratch
mkdir zip/SourceA
mkdir zip/SourceA/python
mkdir zip/SourceA/javascript
mkdir zip/SourceA/misc

# Modified code
mkdir zip/SourceB
mkdir zip/SourceB/python
mkdir zip/SourceB/javascript
mkdir zip/SourceB/misc

# Unmodified code
mkdir zip/SourceC
mkdir zip/SourceC/python
mkdir zip/SourceC/javascript
mkdir zip/SourceC/misc



echo "Copying files"

cp src/*.py zip/SourceA/python/
rm zip/SourceA/python/handlers.py
mkdir zip/SourceA/python/tests/
cp src/tests/*.py zip/SourceA/python/tests/
mkdir zip/SourceA/javascript/static/
cp src/static/*.js zip/SourceA/javascript/static/
cp src/*.yaml zip/SourceA/misc/
mkdir zip/SourceA/misc/views/
cp src/views/*.{html,json} zip/SourceA/misc/views/
mkdir zip/SourceA/misc/templates
mkdir zip/SourceA/misc/templates/images
cp src/templates/images/*.{jpg,png} zip/SourceA/misc/templates/images/

cp src/handlers.py zip/SourceB/python/
mkdir zip/SourceB/misc/templates
mkdir zip/SourceB/misc/templates/bootstrap
mkdir zip/SourceB/misc/templates/bootstrap/css
cp src/templates/bootstrap/css/starter-template.css zip/SourceB/misc/templates/bootstrap/css/

mkdir zip/SourceC/javascript/templates
mkdir zip/SourceC/javascript/templates/bootstrap
mkdir zip/SourceC/javascript/templates/bootstrap/js
cp src/templates/bootstrap/js/*.js zip/SourceC/javascript/templates/bootstrap/js/
mkdir zip/SourceC/misc/templates
mkdir zip/SourceC/misc/templates/bootstrap
mkdir zip/SourceC/misc/templates/bootstrap/css
mkdir zip/SourceC/misc/templates/bootstrap/fonts
cp src/templates/bootstrap/css/*.{css,map} zip/SourceC/misc/templates/bootstrap/css/
rm zip/SourceC/misc/templates/bootstrap/css/starter-template.css
cp src/templates/bootstrap/fonts/* zip/SourceC/misc/templates/bootstrap/fonts/

cp submission_readme zip/readme


if [ -a $ARCHIVE ]
  then
    echo "Removing old archive"
    rm $ARCHIVE
fi

if [ $# -eq 1 -a $1 == '-noarchive' ]
  then
    echo "Skipping archive creation"
    exit
fi

cd zip
find | zip ../$SOURCE_ARCHIVE -@
cd ..


zip $ARCHIVE $SOURCE_ARCHIVE team_k.pdf

rm $SOURCE_ARCHIVE
rm -r zip

echo "Archive $ARCHIVE created"

