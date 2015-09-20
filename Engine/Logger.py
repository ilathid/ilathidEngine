#import logging

class Logger:
    
    messages = []
    callbacks = []
    
    @classmethod
    def addCallback(self, callback):
        Logger.callbacks.append(callback)
    
    @classmethod
    def log(self, text):
        Logger.messages.append(text)
        # Should the following not happen? Should processing only be occasional?
        Logger.process()

    @classmethod
    def process(self):
        while len(Logger.messages) > 0:
            text = Logger.messages.pop(0)
            print "Log: " + text
            for callback in Logger.callbacks:
                callback(text)
                # logging.warn(text)
