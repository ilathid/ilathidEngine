#Engine parameters

import os

class Parameters:
    @classmethod
    def ifSet(self, name, default):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return default

    testCustomAge = None
    visualizeHotspots = False

    #Screen Settings
    #windowsize = (800,600)
    colordepth = 24

    backgroundfile = None
    backgrounddatfile = None
    backgroundalpha = None

    #Slide settings
    slidesize = (512,384)
    slidepos = None

    #Encryption settings
    encryption_key = 'ilathid'
    encryption_rounds = 2

    #Zip mode settings
    #Set to 1 to completely disable zipmode
    zipmodedisabled = 0
    #Current zip state
    zipstate = 0

    #Game settings
    firstslide = None
    firstuislide = None

    #Menu settings
    menu_rect = None

    # #Save settings
    # previewsize = (133,100)

    # #Inventory settings
    # itemsize = 40
    # inv_vertical = 0
    # inv_rect = None
    # showatstart = 1
    # show_alpha = 255
    # hide_alpha = 50
    # scroll_file = 'scroll.bmp'
    # scroll_datfile = None
    # scroll_alpha = (0,0)

    # #Movie settings
    # movieinterval = 34

    # def getmovieinterval():
    #     return movieinterval

    # def setmovieinterval(interval):
    #     global movieinterval
    #     movieinterval = interval

    #Transition Settings
    # transquality = 'Best'
    # scroll_best = 30
    # scroll_normal = 40
    # scroll_fastest = 50

    # By how much to increment transparency every frame (over 255)
    # We're using OpenGL and any reasonably modern GPU, even those of phones,
    # can handle the best settings.
    # fade_best = 7
    # fade_normal = 7
    # fade_fastest = 7

    delay_best = 25 # approx 40 FPS
    delay_normal = 25
    delay_fastest = 25

    #Paths
    # item_path = os.path.join('enginedata')
    # cursor_path = os.path.join('engine','enginedata','cursors')
    # save_path = os.path.join('data','save')
    # data_path = ('data')

    # Scale cursor, in screen pixels cursor
    cursor_scale = 2
    
    # Pixel distance (manhattan) to signal beginning of dragging
    drag_threshold = 5
    grab_view = False
    lock_view = True
    draw_hotspots = False
    
    max_fps = 30
    
    # All slides are from images of similiar sizes. You can use images of other sizes, but objects placed on the slide will be placed as if the slide is of the size given. Also, aspect will be adjusted.
    slide_size_3d    = (1024,1024)
    slide_size_2d    = (800,600)
    slide_2d_padding = (0,0,0,0) # top, bottom, left, right
    
    vfov = 53.0
    windowsize = (640,480)
    fullscreen = True
    backgroundcolor = (0, 0, 0)
    
    # Archive Parameters
    age_folder = "AgeData"
    age_type   = "file"
    engineData_folder = "Data"
    engineData_type   = "file"
