# To build the OSX app bundle, run this script *from the root* as in :
# ./OSX/package_osx.sh

python setup_osx.py py2app
ditto -arch i386 dist/Ilathid.app/Contents/MacOS/python dist/Ilathid.app/Contents/MacOS/pythoni
rm dist/Ilathid.app/Contents/MacOS/Ilathid
rm dist/Ilathid.app/Contents/MacOS/python
mv dist/Ilathid.app/Contents/MacOS/pythoni dist/Ilathid.app/Contents/MacOS/python
cp OSX/llathid_launcher dist/Ilathid.app/Contents/MacOS/Ilathid
chmod +x dist/Ilathid.app/Contents/MacOS/Ilathid

rm dist/Ilathid.app/Contents/Resources/pygame/pygame_icon.icns 
cp OSX/Ilathid.icns dist/Ilathid.app/Contents/Resources/pygame/pygame_icon.icns
rm dist/Ilathid.app/Contents/Resources/pygame/pygame_icon.tiff
cp OSX/pygame_icon.tiff dist/Ilathid.app/Contents/Resources/pygame/pygame_icon.tiff

# pre-compile all source files
./dist/Ilathid.app/Contents/MacOS/python -mcompileall dist/Ilathid.app/Contents/Resources

# delete the original .py files and keep .pyc files only
rm `find dist/Ilathid.app/Contents/Resources -name "*.py" -print`
