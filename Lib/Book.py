"""
This is an example of a Lib class. The Lib directory is kind of like for 'extensions'. Things that could have been in the engine, but don't really belong there- 
I wanted to put some stuff in here just to develop and exemplify how such things could be done. This way the Lib mechanism is available for other uses. For example, if a puzzle has a LOT of specific code (like, maybe you have to play a game of checkers against some steam powered mechanical ai with scripted moves), you don't want to put that amount of code in the ages .py callbacks - it will most likely be useful to have a place for extensions classes for specific uses.

(Or not - time will tell)

Book is a general type of overlay slide (A slide that doesn't fill the whole screen and is drawn overtop of the last slide). There will probably be a lot of books in this engine, so this class makes sense. Books look different, but they each have pages which can be turned - making page-turn noises, etc.
"""

class Book(OverlaySlide):
    pass
    # TODO
