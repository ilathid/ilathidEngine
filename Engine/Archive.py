"""
The archive contains all the info on how to access a file
So the archive info is specific info on how to get and open a file.

You may notice the method to open the file is also in Archive. This may be a bit confusing and may need explenation:
- filepaths contain archive objects.
- a filepath is opened by calling: filepath.open()
- internally, the filepath object uses the archive open method, since openning different kinds of files requires different strategies, specific to the archive type.
"""

import os

# A FilePath is simply a path to a file. It just bundles a filename (with path) and an archive.
# I am no longer sure I like this idea.
class FilePath:
    """ A FilePath is the information needed to access and load any file. """

    def __init__(self, filename, archive):
        """
        filename -- path to file from within the archive
        archive  -- an archive object, which is the info needed to find and open the archive
        """
        self.filename = filename
        self._archive  = archive
        self.file = None
            
    def open(self):
        self.file = self._archive.open(self)
        return self.file

    def close(self):
        if self.file == None:
            raise Exception("file is not open")
        self.file.close
        self.file = None

    def getFilePath(self):
        return self._archive.getFullFilepath(self)

    def getArchive(self):
        """
        Returns the Archive of the filepath
        """
        return self._archive

class Archive:
    def __init__(self, name, folder):
        """ Just a flat folder"""
        self.folder = folder
        self.name = name
    
    def getFullFilepath(self, filepath):
        print "%s, %s, %s" % (self.folder, self.name, filepath.filename)
        return os.path.join(self.folder, self.name, filepath.filename)
        
    def open(self, filepath):
        return file(self.getFullFilepath(filepath), 'rb')

class EncArchive:
    # TODO: everything
    # the __init__ needs to take in everything needed to work with compressed or zipped files.
    pass
