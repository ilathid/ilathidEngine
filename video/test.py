from Media import Media, initialize, shutdown
import time

def test():
    print "init"
    initialize()

    print "create"
    m = Media("void.mpg")
    print "init"
    m.init()
    print "play"
    m.play()
    
    while m.isPlaying():
        time.sleep(.01)
        a = m.getFrame()
        del a
    
    m.close()

    shutdown()

test()
