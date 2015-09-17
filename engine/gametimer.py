"""
                   .7a000BBBWBBBBB0B8Z;.                    
               :XZ80000Z7;,.   .:rXZ8B08827                 
             S0ZZ02r                  :ra0Z88X              
           aZa82;                         7aZZZS            
         SZaZ7                              .SZZZr          
       iZ2aS                 i                 SZa2:        
      2aa2.                 ,W                  ra2ar       
     a2aX                   S8:                   2SaS      
    ZS7.                    2X2                    i7SS     
   aXSXZS0WWWWWWB088BWWWW0aaXrX8aBWWWW088BWWWWWWW0S2SS27    
  ;SS2 X.         7        Xr;;X       i           7 ZXZ    
 .ZXS   Z7       XZZ      87rrrSX     7ZZ.       ;2   aXZ   
 ;SSr    ar     ra;S2     ar;;r7a    :2rXZ      :2    aXa,  
 arZ      Zr   72rrrS2   ZX;;rrrXS  :Z7rrX2    .0     i272  
 ar8       0, 8Ba222280 ,B2222222B rBa22228W: .Z       a7Z  
,SrZ        Zr:::::::,. ; ,,,:::. ;.,,::::,;i 0        S7a, 
,XXX         8         XX         a,         W         7X2: 
,X7X          W,     XZX2Z      ,aSSZ.     .Z          7X2i 
,S7Z           Zi  :2S7;rSS     Z7rrXar    Z           SXa. 
 2rZ            2 Sa7r;;;rSX  :a7r;;;7Sa  a            aXa  
 2Xa            :2X7;;rr7XSBX,WZX7;r;rrX2a            rSS7  
 i2X7          ZaX7SSZ88ZSi  7 .Xa88Z2X7rS2           a7Z.  
  8X2        0MBZar2        7a,       ;ZZ8B@2        :2X2   
  ,aS8      ;       Z      X2Xa7      7     7Z       aXZ    
   72SX              0    2S7r72r    a,             2Sai    
    222S              8  aZSXXX28X  2:             2Sa;     
     2a22             .Z;XXXX777X2 Si            ,aSZ7      
      Xa2ar             S         2,            2aaZ,       
        aaaZ.            B       a.           iaaZS         
         i8aZ2:           0     Si          rZaZa,          
           r8ZZZS         .Z   Xi        :2ZZZZi            
             ;aZZ8Za;       ; i,      7a8ZZZS,              
                iS0B0000Zar:SSX:7a8B00000X:                 
                    :XZ880B00Z80B08Za7.
"""

#Timer Class
import pygame, threading
import globals
from pygame.locals import *

class timer:
    # ID counter for saving
    _curid = 0

    def __init__(self, interval = None, function = None, start = 0):
        #Timer interval
        self._interval = interval
        #Remaining interval (used for saving/loading and pausing of the timer. Has a resolution of ~100ms)
        self._remaining = interval
        #Timer function to call when triggered
        self._function = function
        #Paused state
        self._paused = 0
        #Internal timer
        self._timer = None
        #Defaults
        self._defaults = None
        #timer ID
        self._id = timer._curid
        timer._curid += 1
        
        #Add ID to global timer list
        globals.timers[self._id] = self

        #State
        self._running = 0

        #Start the timer if requested and all required attributes are set
        if start:
            if self._interval != None and self._function != None:
                self.start()        

    #Timer interval
    def getinterval(self):
        return (self._interval)

    #Remaining time before trigger
    def getremaining(self):
        return (self._remaining)

    #Pause state
    def ispaused(self):
        return (self._paused)

    #Running state
    def isrunning(self):
        return (self._running)

    #Sets defaults timer should be restored to when "New Game" is selected
    def setdefault(self):
        self._default = self._save()

    #Loads defaults when "New Game" is selected
    def loaddefaults(self):
        self._load({self._id : self._defaults})

    #Save the current state of the timer
    def _save(self):
        saveval = {}
        saveval['interval'] = self._interval
        saveval['remaining'] = self._remaining
        saveval['function'] = self._function
        saveval['running'] = self._running
        saveval['paused'] = self._paused
            
        return saveval

    #Load the timer with the passed state.
    def _load(self, saveinfo):
        mysaveinfo = saveinfo[self._id]
        self._interval = mysaveinfo['interval']
        self._remaining = mysaveinfo['remaining']
        self._function = mysaveinfo['function']
        self._running = mysaveinfo['running']
        self._paused = mysaveinfo['paused']

    #Start the timer
    def start(self):
        if not self._running:
            #Set remaining time to be whole interval of the timer
            self._remaining = self._interval
            if self._interval >= 100:
                #If the interval is greater than 100ms, break it in 100ms chunks
                self._remaining -= 100
                #Create a 100ms timer
                self._timer = threading.Timer(0.1, self._inttrigger)
            else:
                #If the interval is less than 100ms, just start a timer for whatever the interval was
                self._remaining = 0
                #threading.Timer takes it's interval as a floating point second, instead of ms
                #So the math is to convert ms to floating point seconds
                self._timer = threading.Timer(float(self._interval) / 1000, self._inttrigger)
            #Set this timer to be running and start the internal timer
            self._running = 1
            self._timer.start()

    #Stops the timer if it is running
    def stop(self):
        if self._running:
            self._timer.cancel()
            self._running = 0

    #Calls the timers function once the timer has expired, then restarts the timer with the original interval
    def trigger(self):
        if self._running and not self._paused:
            self._function()
            self._running = 0
            self.start()

    #Internal function to handle the internal timers events, and notify the engine upon expiration        
    def _inttrigger(self):
        if self._running and not self._paused:
            if self._remaining == 0:
                #If there is no time remaining on the timer, inject an event to tell the engine the timer expired
                trigevent = pygame.event.Event(pygame.USEREVENT, {'timerid' : self._id})
                pygame.event.post(trigevent)
            else:
                if self._remaining >= 100:
                    #If the interval remaining is greater than 100ms, break it in 100ms chunks
                    self._remaining -= 100
                    self._timer = threading.Timer(0.1, self._inttrigger)
                else:
                    #If the interval remaining is less than 100ms, just start a timer for whatever is left
                    #threading.Timer takes it's interval as a floating point second, instead of ms
                    #So the math is to convert ms to floating point seconds
                    self._timer = threading.Timer(float(self._remaining) / 1000, self._inttrigger)
                    self._remaining = 0
                self._timer.start()
                    
    #Pause or unpause the timer, timer should still function within ~100ms of the time it is supposed to
    #Some time may be lost or gained, but it should always be under 100ms
    def pause(self):
        if self._paused:
            #Timer is paused so restart it
            if self._remaining >= 100:
                #If the interval remaining is greater than 100ms, break it in 100ms chunks
                self._remaining -= 100
                self._timer = threading.Timer(0.1, self._inttrigger)
            else:
                if self._remaining == 0:
                    #If the interval remaining is 0 (meaning the timer was stopped just before it triggered
                    #restart the timer for just the last "chunk" of time. This should be less than 100ms
                    self._timer = threading.Timer(float(self._interval % 100) / 100, self._inttrigger)
                else:
                    #If the interval remaining is less than 100ms, just start a timer for whatever is left
                    #threading.Timer takes it's interval as a floating point second, instead of ms
                    #So the math is to convert ms to floating point seconds
                    self._timer = threading.Timer(float(self._remaining) / 1000, self._inttrigger)
                    self._remaining = 0
            #Restart the timer
            self._timer.start()
        else:
            #Pause the timer by caneling the internal timer
            self._timer.cancel()
        #Toggle the paused state
        self._paused = not self._paused