# 3 options:
#  1: video player is dormant, and renders a frame and returns it on function call
#  2: video player is threaded, and a frame can be retrieved at any time via function call
#  3: video player is threaded, and a callback is made to external object with rendered frames
#
# For our purposes, 2 looks to be the best (in my opinion), since our engine is "active" (always running at some framerate). If we ever change this, then I would suggest option 3: the video player calls an external function to notify that a frame is ready.

# group=None, target=None, name=None, args=(), kwargs={}

import threading
import time


import pymedia
import pymedia.muxer as muxer
import pymedia.audio.acodec as acodec
import pymedia.video.vcodec as vcodec
# import pymedia.audio.sound as sound
import ao

import pygame

class m_PTS:
    def __init__(self):
        pass
        
    def compare(self, time):
        return 


class m_movie_internal:
    vfTime  = 0.0   # Video Frame Period (1/frame rate)
    
    eob = 0.0
    
    eaq   = 0.1    # Audio Queue Time
    eag   = 0.01   # Audio Gap Tolerance
    READ    = 50000 # Should take about 0.005 to 0.01 seconds to read and sort
    tstart  = 0.0   # time at which video playback started
                    # Adjust for offset & seeking (?)
    frame   = 0     # frame number of last processed frame. ie frame # from start of video
    vtime_start = 0.0

    aBuffer = []    # Buffer (pointers) to raw audio frames, in order
    vBuffer = []    # Buffer (pointers) to raw video frames, in order (?) (what about IPBB?)
    
    video_index = -1 # id for raw video frames
    audio_index = -1 # id for raw audio frames
    
    adecoder   = None
    vdecoder   = None
    demux    = None # Demuxer
    callback = None # Callback Class, Implements onVideoReady( vfr ), where data is vfr.data
    
    def ctime(self):
        return time.time() - self.tstart
    
    def vtime(self):
        return self.frame * self.vfTime + self.vtime_start
    
    def adata2time(self, data):
        return float(len(data.data))/(2*data.channels*data.sample_rate)
    
    def aBufferFull(self):
        return len(self.aBuffer) >= 100
        
    def vBufferFull(self):
        return len(self.vBuffer) >= 100
    
    def parse(self, data):
        # Parse raw mpeg file data
        pstream = self.demux.parse( data )
        for data in pstream:
            if data[0] == self.video_index:
                self.vBuffer.append((data[1], data[ 3 ] / 90000.0))
                # if data[ 3 ] > 0:
                    # print "v", data[ 3 ] / 90000.0
                    # print "t", data[ 3 ] / 90000.0 - self.ctime()
                    # print "u", self.vtime()
            if data[0] == self.audio_index:
                self.aBuffer.append((data[1], data[ 3 ] / 90000.0))
                # if data[ 3 ] > 0: print "a", data[ 3 ] / 90000.0
    
    def playback_buffers(self):
        # print "[gl", self.snd.getLeft(),"]"
        # play movie data
        # neither aBuffer NOR vBuffer may be empty
        # Returns time before action is needed
        ctime = self.ctime()

        # time of the current raw sound
        atime = self.aBuffer[0][1]
        # the following is 0 when getLeft should be 0, up to self.fullspace otherwise
        # qtime = float(self.fullspace - self.snd.getSpace()) / (2*self.channels*self.sample_rate)
        # qtime = self.snd.getLeft()
        # print "eob", self.eob
        
        # qtime: how much more audio needs to be played? negative if there has been a gap
        qtime = self.eob - time.time()
        
        # Should deal with audio on aBuffer?
        # 1. is the next audio segment supposed to be played in the past?
        # 2. if there is sound playing, is the next audio segment supposed to be
        #    played within eaq of the present, and would the next audio segment 
        #    be played within eag of the end of the last sound? (to avoid gaps
        #    once playback has started)
        if (atime < ctime) or (qtime > 0 and atime < ctime + self.eaq and atime < ctime + qtime + self.eag):
            # print "AUDIO"
            # Need to process audio
            ardata = self.aBuffer[0]
            adata = self.adecoder.decode( ardata[0] )
            # print len(adata.data)
            # If there is room on the buffer
            if True: # len(adata.data) < self.snd.getSpace():
                self.aBuffer.pop(0)
                sndlen = self.adata2time(adata)
                # Drop if it the start of the next sound is closer than the end of the current
                # sound. (but using 3/4)
                if ctime + qtime > atime + 3.0*sndlen / 4:
                    print ctime, self.eob, atime, sndlen
                    print "  A Delete Too Late"
                else:
                    self.snd.play( adata.data )         
                    if qtime < 0:
                        self.eob = time.time() + sndlen
                    else:
                        self.eob = self.eob + sndlen
                    # print "qtime", qtime
                del(ardata)
                del(adata)
            return 0
        
        vtime = self.vBuffer[0][1]
        if vtime < 0:
            vtime = self.vtime() # use estimate
            # print "EST"
        if atime < ctime + self.eaq and atime < ctime + qtime + self.eag:
            # print "AUDIO NEEDED"
            pass
        elif vtime < ctime:
            # print "VIDEO", ctime - vtime
            # Need to process video
            # Delete only one at a time: remember, audio has presedence
            vrdata = self.vBuffer.pop(0)
            vdata = self.vdecoder.decode( vrdata[0] )
            if vdata != None:
                if vrdata[1]>0:
                    self.vtime_start = vrdata[1]
                    self.frame = 1
                else:
                    self.frame = self.frame + 1
                if (ctime - vtime) <= self.vfTime*4:
                    self.callback.onVideoReady( vdata )
                else:
                    print "  V Delete Late"
                del vdata
            del vrdata
            return 0
        # how long until we should check the queues again? time to next frame,
        # or time on audio buffer
        return min(vtime - ctime, qtime - self.eag)

class m_movie(m_movie_internal):
    filename = ""
    mfile    = None     # file object for movie file

    video_index = -1 # id for raw video frames
    audio_index = -1 # id for raw audio frames
    
    callback = None # Callback Class, Implements onVideoReady( vfr ), where data is vfr.data
    vfTime   = 0.0   # Video Frame Period (1/frame rate)
    adecoder = None
    vdecoder = None
    demux    = None # Demuxer
    
    def __init__(self, filename):
        self.filename = filename
        
    def play(self, vol=0xaaaa, pos=0):
        # first two are flags for the thread
        self.event_stop = False
        self.event_pause = False
        # this is to block the thread untill it is un-paused
        self.snd = None
        self.Event_pauseEnd = threading.Event()
        t = threading.Thread(None, target=self.playback, kwargs={'pos':pos, 'vol':vol})
        t.start()
        
    def stop(self):
        self.event_stop = True

    def pause(self):
        self.event_pause = not self.event_pause
        # if self.event_pause:
            # self.snd.setVolume(0)
        # else:
            # vol = (self.vol & 0x003f) << 8
            # self.snd.setVolume(vol)
        
    def pause_fade(self):
        self.event_pause = not self.event_pause
        if self.event_pause:
            for i in range(self.vol, 0, -1):
                voli = (i & 0x003f) << 8
                # self.snd.setVolume(voli)
                # print voli
                time.sleep(.005)
        else:
            vol = (self.vol & 0x003f) << 8
            # self.snd.setVolume(vol)

    def setVolume(self, vol):
        # vol is from 1 to 64. No left-right control ( :<( )
        self.vol = vol
        vol = (vol & 0x003f) << 8; # grab 7 bits, shift by 8. So bits 15-8 are set or not.
        # if self.snd != None:
            # self.snd.setVolume(vol)
    
    def playback(self, vol=0, pos=0):
        # open the file
        self.mfile = open( self.filename, 'rb' )
        # create a demuxer using filename extension
        self.demux = muxer.Demuxer(self.filename.split( '.' )[ -1 ].lower())
        tempDemux  = muxer.Demuxer(self.filename.split( '.' )[ -1 ].lower())
        
        # read some of the file
        fdata = self.mfile.read( 300000 )
        pstream = tempDemux.parse( fdata )
        
        # initialize decoders
        # find the audio stream
        for streami in range(len(tempDemux.streams)):
            stream = tempDemux.streams[streami]
            print tempDemux.streams
            if stream['type'] == muxer.CODEC_TYPE_VIDEO:
                try:
                    # Set the initial sound delay to 0 for now

                    # It defines initial offset from video in the beginning of the stream
                    # self.resetVideo()
                    # seekADelta= 0
                    # Setting up the HW video codec
                    self.vdecoder = pymedia.video.ext_codecs.Decoder( stream )
                    print "GOT HW CODEC"
                except:
                    try:
                        # Fall back to SW video codec
                        self.vdecoder= vcodec.Decoder( stream )
                        print "GOT SW CODEC"
                    except:
                        traceback.print_exc()
                        print "FAILED TO INIT VIDEO CODEC"
                
                self.video_index = streami
                break

        for streami in range(len(tempDemux.streams)):
            stream = tempDemux.streams[streami]
            if stream['type'] == muxer.CODEC_TYPE_AUDIO:
                self.adecoder = acodec.Decoder( stream )
                self.audio_index = streami
                break
        
        print "Video index: " + str(self.video_index)
        print "Audio index: " + str(self.audio_index)
        
        # decode a frame to get bitrate, etc
        for vdata in pstream:
            if vdata[0] != self.video_index: continue
            vfr = self.vdecoder.decode( vdata[1] )
            if vfr == None: continue # WHY?
            break
        self.vdecoder.reset()
        
        if self.audio_index != -1:
            for vdata in pstream:
                if vdata[0] != self.audio_index: continue
                afr = self.adecoder.decode( vdata[1] )            
                break
            self.adecoder.reset()
            
            self.channels = afr.channels
            self.sample_rate = afr.sample_rate
            
            # self.snd = sound.Output( self.sample_rate, self.channels, sound.AFMT_S16_NE )
            self.snd = ao.AudioDevice(
                    0,
                    bits=16,
                    rate=self.sample_rate,
                    channels=self.channels,
                    byte_format=1)
            
            print "Sample rate: " + str(self.sample_rate)
            print "Channels: " + str(self.channels)
            
            self.setVolume(vol)
            # print self.snd.getVolume()
        
        # Set up output video method
        # self.snd = sound.Output( sdecoded.sample_rate, sdecoded.channels, sound.AFMT_S16_NE )
        pygame.init()
        pygame.display.set_mode( vfr.size, 0 )
        self.overlay = pygame.Overlay( pygame.YV12_OVERLAY, vfr.size )
        
        # set overlay loc?
        
        # Will need to adjust for aspect
        # if vfr.aspect_ratio> .0:
        #     self.pictureSize= ( vfr.size[ 1 ]* vfr.aspect_ratio, vfr.size[ 1 ] )
        # else:
        #     self.pictureSize= vfr.size
        
        print "vfr info: " + str(vfr)
        print dir(vfr)
        
        print vfr.rate # frames/second. Each vfr is a frame.
        print vfr.bitrate
        print vfr.aspect_ratio
        
        if vfr.rate > 1000:
            self.vfTime = 1000.0 / vfr.rate
        else:
            self.vfTime = 1.0 / vfr.rate
            
        self.tstart = time.time() - pos
                
        self.callback = self
        
        # Now I can trash the temporary muxer, and do things properly
        del(tempDemux)
        self.parse(fdata)
        
        file_ended = False
        while not self.event_stop:
            # Process audio/video, or read or sleep
            if len(self.aBuffer) == 0 or len(self.vBuffer) == 0:
                if not self.read():
                    file_ended = True
            if len(self.aBuffer) == 0:
                self.event_stop = True
                continue
            stime = self.playback_buffers()
            # "freetime"
            if stime > 0:
                if not self.vBufferFull() and not self.aBufferFull():
                    # print "READ"
                    if not self.read():
                        file_ended = True
                else:
                    # print "        Sleep", stime
                    # Sleep until a new frame is needed
                    time.sleep(stime)
        print len(self.aBuffer)
        
    def read(self):
        # read and parse new data
        fdata = self.mfile.read(self.READ)
        if len(fdata) > 0:
            self.parse(fdata)
            return True
        else:
            return False
        
    def onVideoReady(self, vfr):
        if vfr.data != None:
            self.overlay.display( vfr.data )
