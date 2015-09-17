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
