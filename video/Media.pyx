#cython: cdivision=True

import time
import threading

#cdef extern from "Python.h":
#    object PyString_FromString(char *v)

cdef extern from "stdio.h":
    int printf(char *format, ...) nogil

######## alibrary ###################
cdef extern from "alibrary.h" nogil:
    void initialize_al()
    void shutdown_al()

cdef extern from "MediaPlayer.h" nogil:
    ctypedef struct MediaPlayer:
        pass
    ctypedef struct mpframe:
        char *data
        int len
        int width
        int height
    int init_mp(MediaPlayer *mp, char *filepath)
    void close_mp(MediaPlayer *mp)
    int hasAudio_mp(MediaPlayer *mp)
    int hasVideo_mp(MediaPlayer *mp)
    int getPlaybackTime_mp(MediaPlayer *mp)
    int getPauseTime_mp(MediaPlayer *mp)
    void reset_mp(MediaPlayer *mp)
    void play_mp(MediaPlayer *mp)
    int getDuration_mp(MediaPlayer *mp)
    void seek_mp(MediaPlayer *mp, int tim)
    void loop_mp(MediaPlayer *mp)
    void interrupt_mp(MediaPlayer *mp)
    int getState_mp(MediaPlayer *mp)
    mpframe getFrame_mp(MediaPlayer *mp)
    void free_mpframe(mpframe *fr)
    int getVidWidth_mp(MediaPlayer *mp)
    int getVidHeight_mp(MediaPlayer *mp)
    
cdef extern from "timehelper.h":
    int h_time() nogil
    void h_sleep(unsigned int usec) nogil

# alibrary init, shutdown
def initialize():
    initialize_al()

def shutdown():
    shutdown_al()

cdef class Media:
    cdef MediaPlayer med
    
    cdef inited
    cdef filepath
    def __init__(self, filepath):
        # Mutex for video buffer
        self.inited = False
        self.filepath = filepath
    
    def init(self):
        """ Start reading the file to determine file type """
        # print "initialize"
        # The media playing object
        ret = init_mp(&self.med, self.filepath)
        
        if ret == 0:
            self.inited = True
    
    def close(self):
        if self.inited:
            close_mp(&self.med)
    
    def stop(self):
        interrupt_mp(&self.med)
        reset_mp(&self.med)
                
    def play(self):
        if not self.inited:
            print "PLAY FAILED: not initialized"
        else:
            play_mp(&self.med)
        
    def getDuration(self):
        return getDuration_mp(&self.med) / 1000.0
        
    def seek(self, stime):
        seek_mp(&self.med, stime*1000)
        
    def loop(self):
        if not self.inited:
            print "LOOP FAILED: not initialized"
        else:
            loop_mp(&self.med)
        
    def pause(self):
        interrupt_mp(&self.med)
        
    def isPlaying(self):
        return getState_mp(&self.med) == 1
        
    def getFrameSize(self):
        return (getVidWidth_mp(&self.med), getVidHeight_mp(&self.med))
        
    def getFrame(self):
        # Returns a python string with image data, along with image size in pixels
        cdef mpframe fr
        # getFrame does a conversion to RGB space
        fr = getFrame_mp(&self.med)
        # python needs to do a conversion to a string, I'm afraid.
        # printf("Data: %s\n", fr.data[:len])
        cdef ret
        if fr.len > 0:
            ret = (fr.data[:fr.len], fr.width, fr.height)
            # printf("Data len: %d (%d x %d)\n", fr.len, fr.width, fr.height)
        else:
            ret = ("", 0, 0)
        free_mpframe(&fr)
        return ret
