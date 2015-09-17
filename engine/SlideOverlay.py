"""
An Overlay Slide is a slide.
Only enter Overlay Slides using the SlideManager push operation.
Also, the engine needs to check if the destination slide of a slide change is an overlay slide.
If it is, the engine needs to signal the current slide to save its render (as an image), and then the engine needs to pass this image to the overlay slide.

The overlay slide should (eventually) have an optional blur function for the incoming image, which will probably be a very nice effect.

When you leave the overlay slide (unless it is a linking book or something), you just pop it off of the slide manager and return to the slide it was covering up.

(So going to an overlay slide needs to 'pause' or 'freeze' a slide (and all its timers, movies, etc). There are other things (menus) which need to do the same.
"""

# TODO
