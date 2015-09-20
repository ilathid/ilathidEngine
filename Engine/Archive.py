"""
The archive contains all the info on how to access a file
So the archive info is specific info on how to get and open a file.

You may notice the method to open the file is also in Archive. This may be a bit confusing and may need explenation:
- filepaths contain archive objects.
- a filepath is opened by calling: filepath.getFile()
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
        self._filename = filename
        self._archive  = archive
            
    def getFile(self):
        """
        Returns a file handle for the file referenced by this file path
        """
        return self._archive.open(self)
        
    def getFileName(self):
        """
        Returns a filename
        """
        return self._filename

    def getFilePath(self):
        """
        Returns a filename
        """
        return self._archive.getFullFilepath(self)

    def getArchive(self):
        """
        Returns the Archive of the filepath
        """
        return self._archive

# Is this an okay method?
def Archive(name, params):
    if params['type'] == "file":
        file_loc = params['file_loc']
        return Archive_file(name, file_loc)
    else:
        raise Exception('AgeManager: Other archive types not supported')

class Archive_file:
    def __init__(self, name, file_loc):
        """ Just a flat folder"""
        self.file_loc = file_loc
        self.name = name
    
    def open(self, filepath):
        # Think: where are game files stored?
        return file(self.getFullFilepath(filepath), 'rb')
    
    def getFullFilepath(self, filepath):
        return os.path.join(self.file_loc, self.name, filepath._filename)
    
    def getName(self):
        return self.name

class Archive_enc:
    # TODO: everything
    # the __init__ needs to take in everything needed to work with compressed or zipped files.
    pass
