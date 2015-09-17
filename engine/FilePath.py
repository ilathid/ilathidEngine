
class FilePath:
    
    # filename   : the name of the file (can be inside an archive)
    # archive    : the name of the archive file if any, None otherwise
    # isAbsolute : if false, the files will be located using the filemanager.
    def __init__(self, filename, archive, encryption, isAbsolute = False):
        self._filename = filename
        self._archive  = archive
        self._encryption = encryption
        self._isAbsolute = isAbsolute
        
    def getFileName(self):
        return self._filename

    def getArchiveName(self):
        return self._archive

    def getEncryption(self):
        return int(self._encryption)

    def arePathsAbsolute(self):
        return self._isAbsolute
    