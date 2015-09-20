# This is my proposed movie player for the python engine of ilathid.

import threading
import time
import pymedia
import pymedia.muxer as muxer
import pymedia.audio.acodec as acodec
import pymedia.video.vcodec as vcodec
import pymedia.audio.sound as sound
# import ao

# AudioPlayback is a buffer for processed audio around the sound module. I use it because the pymedia snd module will block if its internal buffer is full, which is undesireable for the main video playback. I also can't make use of pymedia.snd.getSpace() because it is broken in (at least) linux, and doesn't seem to give all that reasonable of data.
# The result is that the snd module only needs a snd.play(data) function, which is good because it means something like libao could just as easily be used.
class AudioPlayback:
    eob = 0.0       # What time is the buffer filled until?
    aBuffer = []    # Buffer of Decoded Audio
    t   = None      # Playback Thread
    snd = None      # Sound Module
    
    def __init__(self, snd):
        self.aBuffer = []
        self.snd = snd
        self._blk  = threading.Semaphore(1)
        self._stop = threading.Event()  # Stop Event. Stops once the buffer is empty
        self._fstop = threading.Event() # Force Stop. Stops immediately
        self._hasAudio = threading.Event()

    def begin(self):
        if self.t == None or not self.t.isAlive():
            self._stop.clear()
            self._fstop.clear()
            self.eob = time.time() # Start with an empty buffer
            for data in self.aBuffer:
                del data
            self.t = threading.Thread(None, target=self.process)
            self.t.start()

    # Soft stop: stop the processing thread after it has emptied the current buffer
    def stop(self):
        self._stop.set()
    
    # Force stop: stop as soon as possible
    def fstop(self):
        self._fstop.set()
        if self.t != None and self.t.isAlive():
            self.t.join()
    
    # How much time is left on the audio buffer?
    def getLeft(self):
        return self.eob - time.time()
    
    # Add audio to the audio buffer, to be played by the processing thread
    def play(self, data, sndlen):
        if self._stop.isSet() or self._fstop.isSet():
            print(str(self.__class__.__name__) + ".play(): Sound module has been stopped")
            return False
        # add to buffer
        self._blk.acquire()
        self.aBuffer.append(data)
        if len(self.aBuffer) == 1:
            self._hasAudio.set()
        self._blk.release()
        
        # Adjust buffer length variable
        if self.eob < time.time():
            self.eob = time.time() + sndlen
        else:
            self.eob = self.eob + sndlen
    
    # process audio, run in a thread. Wait for audio in the buffer, and send it to the sound
    # module. This way, if the sound module blocks, the video playback thread can continue 
    # adding audio to the buffer without blocking.
    def process(self):
        # loop until stop
        while not self._fstop.isSet():
            self._hasAudio.wait(.05) # .05 second wait, in case of fstop event
            if self._hasAudio.isSet():
                self._blk.acquire()
                data = self.aBuffer.pop(0)
                if len(self.aBuffer) == 0:
                    self._hasAudio.clear()
                self._blk.release()
            
                # Process the data. May block, but that is okay
                self.snd.play( data )
            elif self._stop.isSet(): # Soft stop waits until the buffer is empty
                # print "LEN",len(self.aBuffer),"Soft Stop Sound"
                self._fstop.set()
        # self.snd.stop()

# This is the internal movie player module. I kept this seperate to simplify things, and in case movie frames are not always read from a file.
class MovieInternal:
    vfTime  = 0.0   # Video Frame Period (1/frame rate). Needs to be adjusted on the fly.
    eaq   = 0.05    # Audio Queue Time: how many seconds ahead can we plan (queue) audio?
    eag   = 0.01   # Audio Gap Tolerance: for small gaps, just run sound together. Don't wait .001 seconds (or something) for the right time to play the next audio segment
    
    tstart  = 0.0   # time at which video playback started.
    frame   = 0     # for calculating vtime
    vtime_start = 0.0
    
    aBuffer = []    # Buffer (pointers) to raw audio frames, in order
    a_i     = 0     #  Current 'location' of playback of the audio buffer
    vBuffer = []    # Buffer (pointers) to raw video frames, in order (?) (what about IPBB?)
    v_i     = 0
    
    adecoder   = None
    vdecoder   = None
    callback = None # Callback Class, Implements callback( vfr ), where data is vfr.data
    
    demux = None # Demuxer
    
    # Get current playback time
    def ctime(self):
        return time.time() - self.tstart
    
    # Get desired plaback time of the given video frame. Uses a mixture of PTS, framerate
    def vtime(self, vfr):
        # Get expected vtime using frame rate
        vtime = self.frame * self.vfTime + self.vtime_start # use estimate
        
        # correct for PTS data, using averaging in case of bogus values (??)
        vtime2 = vfr[1]
        if vtime2 > 0:
            vtime = vtime2
            #vtime = (vtime + vtime2)/2.0
            
        return vtime
    
    def atime(self, afr):
        # TODO: What if there is no PTS data on the audio? Can I use another method?
        if afr[1] < 0:
            raise Exception("No Audio PTS Data Found")
        return afr[1]
    
    # Calculate the length (time) of a piece of audio data.
    def adata2time(self, afr):
        return float(len(afr.data))/(2*afr.channels*afr.sample_rate)

    def set_vi(self, v_i):
        self.v_i = v_i
        if v_i < 0:
            self.v_i = 0
        if v_i > len(self.vBuffer) - 1:
            self.v_i = len(self.vBuffer) - 1
    
    def vi(self):
        return self.v_i

    def afr(self):
        if self.a_i <= len(self.aBuffer) - 1:
            return self.aBuffer[self.a_i]
        else:
            return None

    def vfr(self):
        if self.v_i <= len(self.vBuffer) - 1:
            return self.vBuffer[self.v_i]
        else:
            return None

    def set_ai(self, a_i):
        self.a_i = a_i
        if a_i < 0:
            self.a_i = 0
        if a_i > len(self.aBuffer) - 1:
            self.a_i = len(self.aBuffer) - 1
    
    def ai(self):
        return self.a_i

    # Process and handle either audio or video, depending on a set of conditions
    # Returns time before more action is needed
    def playbackBuffers(self):
        ctime = self.ctime()
        t1 = 0.0
        t2 = 0.0
        afr = self.afr()
        if not afr:
            t1 = 1.0
        else:
            # time of the current sound.
            atime = self.atime(afr)        
            # print atime, ctime
            # How much audio is currently queued on the buffer?
            qtime = self.snd.getLeft()
            
            # Is it time to deal with the next raw sound on the buffer?
            # 1. is the next audio segment supposed to be played in the past?
            # 2. is the next audio segment supposed to be played within eaq of the present,
            #    and would the next audio segment be started within eag of the end of the
            #    last sound?        
            if (ctime > atime) or (qtime > 0 and atime < ctime + self.eaq and atime < ctime + qtime + self.eag):
                adata = self.processAudio(afr)
                sndlen = self.adata2time(adata)
                # Skip if the start of the next sound is closer than the end of the current
                # sound. (but using 3/4)
                if ctime + qtime > atime + 3.0*sndlen / 4:
                    print(" A Delete Too Late")
                    print("  ",ctime, qtime, atime, sndlen)
                else:            
                    # Queue the audio segment
                    self.snd.play( adata.data, sndlen )         
            else:
                t1 = qtime - self.eaq
        
        if t1 == 0:
            return 0
            
        # Decide if to process video
        vfr = self.vfr()
        if not vfr:
            t2 = 1.0
        else:
            # Time of the current video frame
            vtime = self.vtime(vfr)
            # print vtime, self.v_i, ctime, self.frame, self.vfTime, self.vtime_start
            # 517
            # Handle the video frame if its time has come (or gone)
            if self.vtime(vfr) < ctime:
                vdata = None
                while vfr != None and vdata == None:
                    vdata = self.processVideo(vfr)
                    vfr = self.vfr()
                if vfr == None:
                    t2 = 1.0
                else:
                    # If we are on time, show the frame
                    # Otherwise, delete, one frame at a time: audio has presedence            
                    if (ctime - vtime) <= self.vfTime*5:
                        if vdata.data != None:
                            self.callback( vdata )
                            # print "<Video>"
                        else:
                            print("<VIDFAIL>")
                    else:
                        print("  V Delete Late")
                        del vdata                
            else:
                t2 = vtime - ctime
        if t2 == 0.0:
            return 0
        
        # Otherwise, return the shorter time
        return min(t1, t2)
    
    # Process an audio frame if needed.
    # If audio is processed, return 0.0
    # If no audio is on the buffer, return 1.0
    # If audio is on the buffer but was not processed, return time until we should handle it.
    def processAudio(self, afr):
        # print "|",
        adata = self.adecoder.decode( afr[0] )
        self.a_i = self.a_i + 1
        return adata
    
    # Process a video frame if needed.
    # If a frame is processed, return 0.0
    # If no fame is on the buffer, return 1.0
    # If frame is on the buffer but was not processed, return time until we should handle it.
    def processVideo(self, vfr):
        # Need to process video
        # print "_",
        
        ##
        try:
            vdata = self.vdecoder.decode( vfr[0] )
        except Exception as e:
            print(e)
            vdata = None
        
        #for i in range(5): # Try more than once
        #    try:
        #        vdata = self.vdecoder.decode( vfr[0] )
        #    except Exception as e:
        #        print e
        #        vdata = None
        #        self.vdecoder.reset()
        #    if vdata != None: break
        #    # break
        
        # Some video segments are empty...
        if vdata != None:
            # correct self.vfTime in case of changes, using an average
            if vdata.rate > 1000:
                vfTime2 = 1000.0 / vdata.rate
            else:
                vfTime2 = 1.0 / vdata.rate
            self.vfTime = (self.vfTime + vfTime2) / 2.0
            
            # if PTS, use for vtime calc
            if vfr[1]>0:
                self.vtime_start = self.vtime(vfr) # vrdata[1]
                self.frame = 0
            else:
                self.frame = self.frame + 1
        else:
            # I figure the following is unacceptable. Meens the vdecoder was not init'zed
            # if vfr[1]>0:
            #     raise Exception("PTS Video Frame Failed to Render")
            # print "F",
            if vfr[1]>0:
                print("PTS Video Frame Failed to Render")
        # print "["+str(self.v_i)+"]",
        self.v_i = self.v_i + 1
        return vdata


# TODO: Turn the following into the class "Movie"
# TODO: "Movie" can play EITHER data or a file (by file path)
#       The file-based mode disables seek. Loop looses all options but on/off
# Play movies from loaded data. Data is just the whole mpg file
class MoviePreloaded(MovieInternal):
    event = []
    state = None
    video_index = -1 # id for raw video frames
    audio_index = -1 # id for raw audio frames
    snd = None
    
    def __del__(self):
        self.demux.reset()
        del self.demux
        del self.adecoder
        del self.vdecoder
    
    def __init__(self, data, callbackClass=None):
        print("Init", len(data))
        if len(data) > 10485160*3:
            raise Exception("MORE THAN 30 MEGABYTES!!! TOO BIG!!!")
        # initialize variables
        self.state = self.STOP
        self.unpause_time = 0.0
        self.callback = callbackClass
    
        # Load the demuxer
        self.demux = muxer.Demuxer('mpg')
        
        # Parse the data: takes time
        # Needed to load stream information
        # TODO: if file-based, demux only a sample
        
        self.demux.reset() # TODO: This line fails internally in pymedia.
        
        pstream = self.demux.parse( data )
        del data
        
        # initialize decoders
        # find the video stream
        for streami in range(len(self.demux.streams)):
            stream = self.demux.streams[streami]
            if stream['type'] == muxer.CODEC_TYPE_VIDEO:
                self.video_index = streami
                self.vdecoder = self.makeVDecoder()
                break

        # find the audio stream
        for streami in range(len(self.demux.streams)):
            stream = self.demux.streams[streami]
            if stream['type'] == muxer.CODEC_TYPE_AUDIO:
                self.audio_index = streami
                self.adecoder = self.makeADecoder()
                break
        
        if self.audio_index == -1 and self.video_index == -1:
            self.video_index = 0
        
        # TODO: if file, the following should be in a function.
        # (So put it there)
        # seperate audio and video buffers, store (data, pts)
        for data in pstream:
            if data[0] == self.video_index:
                self.vBuffer.append((data[1], data[ 3 ] / 90000.0))
            if data[0] == self.audio_index:
                self.aBuffer.append((data[1], data[ 3 ] / 90000.0))
        
        # Create sound output
        if len(self.aBuffer) > 0:
            afr = self.adecoder.decode( self.aBuffer[0][0] )
            self.adecoder.reset()
            
            sndModule = sound.Output( afr.sample_rate, afr.channels, sound.AFMT_S16_NE )
            self.snd = AudioPlayback(sndModule)
        
        # prep video output
        if len(self.vBuffer) > 0: # better be true
            for data in self.vBuffer:
                vfr = self.vdecoder.decode( data[0] )
                if vfr != None and vfr.data != None: break
            
            # print self.vdecoder.getParams().viewkeys()
            
            self.vdecoder.reset()
            
            # Store video size
            self.size = vfr.size
            self.aspect = vfr.aspect_ratio

            # Frame time        
            if vfr.rate > 1000:
                self.vfTime = 1000.0 / vfr.rate
            else:
                self.vfTime = 1.0 / vfr.rate

    def makeVDecoder(self):
        print("Making vDecoder", self.demux.streams)
        try:
            return pymedia.video.ext_codecs.Decoder( self.demux.streams[self.video_index] )
        except:
            # Fall back to SW video codec
            return vcodec.Decoder( self.demux.streams[self.video_index] )

    def makeADecoder(self):
        return acodec.Decoder( self.demux.streams[self.audio_index] )

    def setCallback(self, callbackClass):
        self.callback = callbackClass

    def getSize(self):
        return self.size

    # Movie Controls
    PAUSE = 1
    STOP  = 2
    PLAY  = 3
    SEEK  = 4    
    END   = 5
    
    # Pause Control/Event
    def pause(self):
        if self.state == self.PLAY:
            self.event.append(self.PAUSE)
            return True
        return False

    # Stop Control/Event

    def isPlaying(self):
        return self.state == self.PLAY

    def stop(self):
        if self.state == self.PLAY:
            self.event.append(self.STOP)
            return True
        if self.state == self.PAUSE:
            self._Stop()
            return True
        return False
    
    # Play Control/Event
    #  If looping parameters are given, a new loopcycle is calculated
    #  Playback will continue until loopend, and then loop from loopstart to loopend.
    #  If loopseek is set, playback starts from loopstart the first time.
    def play(self, options={}): #loop=False, loopstart=0, loopend=0, loopseek=False):
        vlinfo = None
        if self.state == self.STOP or self.state == self.PAUSE:
            # TODO: the following needs a big "if" for file-based.
            # file-based has its own logic, which is just: loop is on or off.
            # Looping
            if self.state == self.STOP and 'loop' in options and options['loop']:
                print("Looping")
                if 'loopstart' in options and options['loopstart'] > 0:
                    self._Seek(options['loopstart'])
                vlframe = self.vi()
                if 'loopend' in options:
                    loopend = options['loopend']
                else:
                    loopend = -1
                    
                if not 'loopseek' in options or not options['loopseek']:
                    self._Stop()
                vlinfo = {"loopend":loopend, "vlframe":vlframe}
            self.event.append(self.PLAY)
            # Playback until next event
            t = threading.Thread(None, target=self._Play, kwargs={'vlinfo':vlinfo})
            t.start()
            return True
    
    def _Play(self, vlinfo=None):
        if self.snd != None:
            self.snd.begin()

        print("_Play")        
        while len(self.event) > 0:
            # Handle Events
            ev = self.event.pop(0)
            if ev == self.PLAY:
                self.state = self.PLAY
            if ev == self.SEEK: # TODO: Seek is disabled for file-based
                self._Seek(self.seek_time)
                self.state = self.PLAY # just in case?
            if ev == self.STOP or ev == self.END: # TODO: file-based, self.END triggers loop here, rather than internally to play()
                self._Stop()
                self.state = self.STOP
            if ev == self.PAUSE:
                self.state = self.PAUSE
                # Stop the sound module
            
            # playback until next event
            if self.state == self.PLAY:
                self.playback(vlinfo=vlinfo)
         
        # Stop the sound module
        if self.snd != None:
            self.snd.stop()
    
    # Playback Thread
    def playback(self, vlinfo=None):
        self.tstart = time.time() - self.unpause_time
        self.vtime_start = self.unpause_time
        self.frame = 1
        # time.sleep(5)
        p1 = False
        print(vlinfo)
        # Stop playback for: 1 Any event 2 neither audio nor video content remains
        while len(self.event) == 0 and (self.a_i <= len(self.aBuffer) - 1 or self.v_i <= len(self.vBuffer) - 1): # and self.state == self.PLAY
        
            # file-reader as well.
            if vlinfo != None and not p1 and self.v_i >= vlinfo['vlframe']:
                print("saveloop")
                p1 = True
                # print "t,vi,ai,frame,vtime_start",time.time()-self.tstart, vlinfo['vlframe'],self.v_i,self.a_i,self.frame,self.vtime_start
                # 258
                ltime = time.time()-self.tstart
                lv_i = self.v_i
                la_i = self.a_i
                lframe = self.frame
                lvtime = self.vtime_start
        
            # Play some movie, and sleep if appropriate
            stime = self.playbackBuffers()
            if stime > 0.005: # TODO: if file-based, we should read more file as needed/in free time
                time.sleep(min(stime/2, 0.1))
                # print "Sleep ",stime
            
            # Looping
            if p1 and ((vlinfo['loopend'] > 0 and self.ctime() > vlinfo['loopend']) or self.v_i >= len(self.vBuffer) - 1):
                print('restoreloop', lv_i)
                self.v_i = lv_i
                self.a_i = la_i
                self.tstart = time.time() - ltime
                self.frame = lframe
                self.vtime_start = lvtime
                
                # self.vdecoder.reset()
                try:
                    vfr = self.vfr()
                    vdata = None
                    while (vfr != None):
                        self.vdecoder.reset()
                        self.vdecoder.decode(vfr[0])
                        self.vdecoder.decode(vfr[0])
                        vdata = self.processVideo(vfr)
                        if vdata and vdata.data:
                            break
                        vfr = self.vfr()
                except Exception as e:
                    print(e)

                # print self.tstart
                # p1 = False
                # print "t,vi,ai,frame,vtime_start",time.time()-self.tstart, vlinfo['vlframe'],self.v_i,self.a_i,self.frame,self.vtime_start
                
        # Have we reached the end of the playback buffers?
        if len(self.event) == 0:
            self.event.append(self.END)
        
        # Where is playback at currently?
        self.unpause_time = time.time() - self.tstart

    def _Stop(self):
        print("_Stop")    
        # reset functions do goofy things. Remake the decoders (for next time)
        # if self.audio_index != -1:
        #     del self.adecoder
        #     self.adecoder = self.makeADecoder()
        # del self.vdecoder
        # self.vdecoder = self.makeVDecoder()
        
        # TODO: file-based reset file pointer, read some data, parse
        self.snd.fstop()
        self.vdecoder.reset()
        if self.audio_index != -1:
            self.adecoder.reset()
        self.adecoder = self.makeADecoder()
        # Reset playback location
        self.a_i = 0
        self.v_i = 0
        
        self.unpause_time = 0.0
    
    def _Pause(self):
        print("_Pause")
    
    # Seek Control/Event
    def seek(self, time):
        # TODO: if file-based, fail
        if self.state == self.PLAY:
            self.seek_time = time
            self.event.append(self.SEEK)
        if self.state == self.PAUSE or self.state == self.STOP:
            # Just seek right away
            self._Seek(time)
    
    # Seek to the specified time
    def _Seek(self, seek_time):
        print("_Seek")
        try:
            self._Stop()
            (vlframe, vltime) = self.vseek(seek_time)
            print("Seeking frame, time", (vlframe, vltime, seek_time))
            self.a_i = self.aseek(vltime)
            self.v_i = vlframe
            self.unpause_time = vltime
            self.state = self.PAUSE
        except Exception as e:
            print(e)
            self._Stop()
    
    # vseek
    def vseek(self, time):
        # Finds the first iframe after 'time'
        # Leaves the vdecoder reader to play back AFTER this iframe.
        # If you want to play from this iframe, just remake vdecoder: it is an i-frame (yeah, right)
        
        # For now I assume the presence of PTS data
        
        #What is the earliest pts available?
        pts1 = 0.0
        # pts1 = 0
        # for vfr in self.vBuffer:
        #     if vfr != None and vfr[1] > 0:
        #         pts1 = vfr[1]
        #         break
        
        # What is the latest pts available?
        pts2 = 0
        for i in range(len(self.vBuffer)-1, 0, -1):
            vfr = self.vBuffer[i]
            if vfr != None and vfr[1] > 0:
                pts2 = vfr[1]
                break            
        
        if pts1 >= pts2:
            # can't trust PTS: use frate
            pts1 = 0.0
            pts2 = len(self.vBuffer) * self.vfTime

        print("pts bounds",pts1, pts2)
                
        # Try to guess the video index. Back up a bit...
        guess_i = len(self.vBuffer) * (time-pts1)/float(pts2-pts1)
        self.set_vi(max(int(guess_i-300), 0))
        
        # Find the first PTS time-stamp before "time"
        while self.vfr()!=None and self.vfr()[1] < time:
            self.v_i = self.v_i + 1
        while self.vfr()!=None and (self.vfr()[1] < 0 or self.vfr()[1] > time):
            self.v_i = self.v_i - 1
            
        if self.vfr() == None or self.vfr()[1] < 0:
            # We couldn't find the desired time. We just fail nicely.
            raise Exception("Failed to Seek: seek out of bounds")
            
        self.frame = 1
        self.vtime_start = self.vfr()[1]
           
        print("Guessing video index",self.vi())
        print("vtime_start",self.vtime_start)
        
        # Start decoding, frames, looking for something that can be the 'first' frame after
        # a seek operation
        vfr = self.vfr()
        vdata = None
        while (vfr != None):
            self.vdecoder.reset()
            self.vdecoder.decode(vfr[0])
            self.vdecoder.decode(vfr[0])
            vdata = self.processVideo(vfr)
            if vdata and vdata.data and self.vtime(vfr) >= time:
                # Success!
                break
            print(self.vtime(vfr), time)
            vfr = self.vfr()
            # self.vdecoder = self.makeVDecoder()
        
        if vfr == None:
            raise Exception("Failed to Seek")
        
        # self.vi() is the iframe index.
        return (self.vi()-1, self.vtime(vfr))

    # aseek
    def aseek(self, time):
        if len(self.aBuffer) == 0:
            return 0
        # Find the first audio frame after time.
        # Assume all audio frames have PTS data?
            
        # For now I assume the presence of PTS data
        pts1 = 0.0
        # for vfr in self.aBuffer:
        #     if vfr != None and vfr[1] > 0:
        #         pts1 = vfr[1]
        #         break
        
        pts2 = 0
        for i in range(len(self.aBuffer)-1, 0, -1):
            vfr = self.aBuffer[i]
            if vfr != None and vfr[1] > 0:
                pts2 = vfr[1]
                break
        
        if pts1 >= pts2:
            # can't trust PTS
            raise Exception("Audio seek Failed(1)!")
        
        guess_i = int((time-pts1)/float(pts2-pts1))
        if guess_i < 0 or guess_i > len(self.vBuffer):
            raise Exception("Audio seek Failed(2)!")
        
        scanahead = False
        while guess_i < len(self.aBuffer) and self.aBuffer[guess_i][1] < time:
            scanahead = True
            guess_i = guess_i + 1
        
        while not scanahead and guess_i > 0 and self.aBuffer[guess_i][1] > time:
            guess_i = guess_i - 1
        
        return guess_i
