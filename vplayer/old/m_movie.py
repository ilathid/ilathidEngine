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
import pymedia.audio.sound as sound
# import ao
import pygame

# PlaybackBuffer is a buffer for processed audio around the sound module. I use it because the pymedia snd module will block if its internal buffer is full, which is undesireable for the main video playback. I also can't make use of pymedia.snd.getSpace() because it is broken in (at least) linux, and doesn't seem to give all that reasonable of data.
# The result is that the snd module only needs a snd.play(data) function, which is good because it means something like libao could just as easily be used.
class PlaybackBuffer:
    eob = 0.0
    aBuffer = []
    def __init__(self, snd):
        self.snd = snd
        self.t = threading.Thread(None, target=self.process)
        self.aBuffer = []
        self.eob = time.time()
        self._blk  = threading.Semaphore(1)
        self._stop = threading.Event()  # Stop Event. Stops once the buffer is empty
        self._fstop = threading.Event() # Force Stop. Stops immediately
        self._notEmpty = threading.Event()

    def begin(self):
        self.t.start()        

    # Stop after buffer empties
    def stop(self):
        self._stop.set()
    
    # Stop even if there is audio on the buffer
    def fstop(self):
        self._fstop.set()
    
    def getLeft(self):
        return self.eob - time.time()
    
    # Called from outside the 'process' thread to add sound data to the buffer.
    def play(self, data, sndlen):
        if self._stop.isSet() or self._fstop.isSet():
            return False
        # add to buffer
        self._blk.acquire()
        self.aBuffer.append(data)
        if len(self.aBuffer) == 1:
            # print "1 sound"
            self._notEmpty.set()
        self._blk.release()
        
        # Adjust buffer length variable
        if self.eob < time.time():
            self.eob = time.time() + sndlen
        else:
            self.eob = self.eob + sndlen
    
    # threaded audio processor, waits for audio on the buffer and sends it to the snd module.
    # the snd module can block all it wants in this case. When the snd module un-blocks, more
    # sound can be fed to it (ie immediately)
    def process(self):
        # loop until stop
        while not self._fstop.isSet():
            self._notEmpty.wait(.5) # .5 second wait, in case of fstop event
            if self._notEmpty.isSet():
                if self._stop.isSet():
                    self._fstop.set()
                else:
                    self._blk.acquire()
                    data = self.aBuffer.pop(0)
                    if len(self.aBuffer) == 0:
                        self._notEmpty.clear()
                    self._blk.release()
                
                    # Process the data. May block, but that is okay
                    self.snd.play( data )

# This is the internal movie player module. I kept this seperate to simplify things, and in case movie frames are not always read from a file.
class MovieInternal:
    vfTime  = 0.0   # Video Frame Period (1/frame rate). Needs to be adjusted on the fly.
    eaq   = 0.05    # Audio Queue Time: how many seconds ahead can we plan (queue) audio?
    eag   = 0.01   # Audio Gap Tolerance: for small gaps, just run sound together. Don't wait .001 seconds (or something) for the right time to play the next audio segment
    
    tstart  = 0.0   # time at which video playback started.
    frame   = 0     # for calculating vtime
    vtime_start = 0.0
    
    aBuffer = []    # Buffer (pointers) to raw audio frames, in order
    vBuffer = []    # Buffer (pointers) to raw video frames, in order (?) (what about IPBB?)
    adecoder   = None
    vdecoder   = None
    callback = None # Callback Class, Implements onVideoReady( vfr ), where data is vfr.data
    
    # Get current playback time
    def ctime(self):
        return time.time() - self.tstart
    
    # Get pts of current video frame (where PTS data is not available
    def vtime(self, vfr):
        # Get expected vtime using frame rate
        vtime = self.frame * self.vfTime + self.vtime_start # use estimate
        
        # correct for PTS data, using averaging in case of bogus values (??)
        vtime2 = vfr[1]
        if vtime2 > 0:
            vtime = (vtime + vtime2)/2.0
            
        return vtime
    
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
            if data[0] == self.audio_index:
                self.aBuffer.append((data[1], data[ 3 ] / 90000.0))
    
    def playback_buffers(self):
        # play movie data
        # Returns time before action is needed
        
        ctime = self.ctime()
        t1 = self.processAudio(ctime)
        if t1 == 0:
            return 0
            
        # If no audio was handled, try a video frame
        t2 = self.processVideo(ctime)
        if t2 == 0.0:
            return 0.0
        
        # Otherwise, return the shorter time
        return min(t1, t2)
    
    def processAudio(self, ctime):
        if len(self.aBuffer) == 0:
            return 1.0
        # time of the current raw sound
        atime = self.aBuffer[0][1]
        
        # How much audio is on the buffer?
        qtime = self.snd.getLeft()
        
        # Should deal with audio on aBuffer?
        # 1. is the next audio segment supposed to be played in the past?
        # 2. is the next audio segment supposed to be played within eaq of the present,
        #    and would the next audio segment be played within eag of the end of the
        #    last sound?        
        if (ctime > atime) or (qtime > 0 and atime < ctime + self.eaq and atime < ctime + qtime + self.eag):
            # print "AUDIO"
            # Need to process audio
            ardata = self.aBuffer[0]
            adata = self.adecoder.decode( ardata[0] )
            # print len(adata.data)
            # If there is room on the buffer
            # print "free"
            self.aBuffer.pop(0)
            sndlen = self.adata2time(adata)
            # Drop if it the start of the next sound is closer than the end of the current
            # sound. (but using 3/4)
            
            if ctime + qtime > atime + 3.0*sndlen / 4:
                print ctime, qtime, atime, sndlen
                print "  A Delete Too Late"
            else:
                # sndarray = numpy.fromstring(adata.data)
                ## sndarray = numpy.transpose(numpy.vstack((sndarray, sndarray)))
                ##sound = pygame.sndarray.make_sound(sndarray)
                # sound.play()
                # t1 = time.time()
                ##self.snd.play(sound)
                # print "t2", time.time()-t1
                self.snd.play( adata.data, sndlen )         
            del(ardata)
            del(adata)
            return 0.0
        
        # when do we need action?
        return qtime

    def processVideo(self, ctime):
        if len(self.vBuffer) == 0:
            # Just deal with audio
            return 1.0
            
        vtime = self.vtime(self.vBuffer[0])
        if vtime < ctime:
            # Need to process video
            # Delete only one at a time: remember, audio has presedence
            vrdata = self.vBuffer.pop(0)
            vdata = self.vdecoder.decode( vrdata[0] )
            
            if vdata != None:
                # correct vfTime, using an average
                if vdata.rate > 1000:
                    vfTime2 = 1000.0 / vdata.rate
                else:
                    vfTime2 = 1.0 / vdata.rate
                self.vfTime = (self.vfTime + vfTime2) / 2.0
                
                # if PTS, use for vtime calc
                if vrdata[1]>0:
                    self.vtime_start = vtime # vrdata[1]
                    self.frame = 1
                else:
                    self.frame = self.frame + 1
                
                # If we are on time, show the frame
                if (ctime - vtime) <= self.vfTime*2:
                    self.callback.onVideoReady( vdata )
                else:
                    print "  V Delete Late"
                del vdata
            del vrdata
            return 0.0
            
        # When do we need action?
        return vtime - ctime


class MovieFile(MovieInternal):
    filename = ""
    mfile    = None     # file object for movie file

    video_index = -1 # id for raw video frames
    audio_index = -1 # id for raw audio frames
    
    READ    = 50000 # # bytes, 50000 should take about 0.005 to 0.01 seconds to read and sort
    demux    = None # Demuxer
    
    def __init__(self, filename):
        self.filename = filename
        
    def play(self, vol=0xaaaa, pos=0):
        # first two are flags for the thread
        self.event_stop = False
        self.event_pause = False
        # this is to block the thread untill it is un-paused
        self.snd = None

        t = threading.Thread(None, target=self.playback, kwargs={'pos':pos, 'vol':vol})
        t.start()
        
    def stop(self):
        self.event_stop = True

    def playing(self):
        return self.event_stop

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
            
            # print 'Opening sound', self.sample_rate, self.channels, sound.AFMT_S16_LE, 0
            sndModule = sound.Output( self.sample_rate, self.channels, sound.AFMT_S16_NE )
            
            self.snd = PlaybackBuffer(sndModule)
            self.snd.begin()
            # pygame.mixer.init(self.sample_rate, -16, self.channels, 4096) # 4096
            # pygame.mixer.set_num_channels(2)
            # self.snd = pygame.mixer.Channel(0)
            # self.snd = ao.AudioDevice(
            #         0,
            #         bits=16,
            #         rate=self.sample_rate,
            #         channels=self.channels,
            #         byte_format=1)
            
            print "Sample rate: " + str(self.sample_rate)
            print "Channels: " + str(self.channels)
            
            # self.fullspace = self.snd.getSpace()
            self.fullspace = 0
            print "FULLSPACE", self.fullspace
            
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
                    time.sleep(stime/2.0)
        if len(self.aBuffer) == 0:
            self.snd.stop()
        else:
            self.snd.fstop()
        self.event_stop = True
        print len(self.aBuffer)
        
    def read(self):
        # read and parse new data
        fdata = self.mfile.read(self.READ)
        if len(fdata) > 0:
            self.parse(fdata)
            return True
        else:
            return False
    
    # Display a video frame
    def onVideoReady(self, vfr):
        if vfr.data != None:
            self.overlay.display( vfr.data )

# External movie player class. To be replaced to fit in AoI
class m_movie(m_movie_internal):
    filename = ""
    mfile    = None     # file object for movie file

    video_index = -1 # id for raw video frames
    audio_index = -1 # id for raw audio frames
    
    READ    = 50000 # # bytes, 50000 should take about 0.005 to 0.01 seconds to read and sort
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
            
            # print 'Opening sound', self.sample_rate, self.channels, sound.AFMT_S16_LE, 0
            sndModule = sound.Output( self.sample_rate, self.channels, sound.AFMT_S16_NE )
            
            self.snd = PlaybackBuffer(sndModule)
            self.snd.begin()
            # pygame.mixer.init(self.sample_rate, -16, self.channels, 4096) # 4096
            # pygame.mixer.set_num_channels(2)
            # self.snd = pygame.mixer.Channel(0)
            # self.snd = ao.AudioDevice(
            #         0,
            #         bits=16,
            #         rate=self.sample_rate,
            #         channels=self.channels,
            #         byte_format=1)
            
            print "Sample rate: " + str(self.sample_rate)
            print "Channels: " + str(self.channels)
            
            # self.fullspace = self.snd.getSpace()
            self.fullspace = 0
            print "FULLSPACE", self.fullspace
            
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
                    time.sleep(stime/2.0)
        if len(self.aBuffer) == 0:
            self.snd.stop()
        else:
            self.snd.fstop()
        print len(self.aBuffer)
        
    def read(self):
        # read and parse new data
        fdata = self.mfile.read(self.READ)
        if len(fdata) > 0:
            self.parse(fdata)
            return True
        else:
            return False
    
    # Display a video frame
    def onVideoReady(self, vfr):
        if vfr.data != None:
            self.overlay.display( vfr.data )
