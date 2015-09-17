import os

# This class is used to locate files
class FileManager:
    
    def __init__(self):
        self.slide_path = [os.path.join('engine', 'enginedata')]
        self.sound_path = [os.path.join('engine', 'enginedata')]
        self.image_path = [os.path.join('engine', 'enginedata')]
        self.movie_path = [os.path.join('engine', 'enginedata')]
        self.music_path = [os.path.join('engine', 'enginedata')]
    
    def push_dir(self, dirname):
        self.slide_path.append(os.path.join(dirname, 'slides'))
        self.sound_path.append(os.path.join(dirname, 'sound'))
        self.image_path.append(os.path.join(dirname, 'images'))
        self.movie_path.append(os.path.join(dirname, 'movies'))
        self.music_path.append(os.path.join(dirname, 'music'))
    
    # Setup the search paths for a given age
    def push_age(self, age_name):
        self.push_dir(os.path.join('data', 'ages', age_name))
        
    # Remove the search paths from the latest added age
    def pop_age(self):
        self.slide_path.pop()
        self.sound_path.pop()
        self.image_path.pop()
        self.movie_path.pop()
        self.music_path.pop()
    
    # Given a slide image filename, locates the file within data paths and returns the
    # path to this file
    def find_slide(self, filename):
        for curr_path in reversed(self.slide_path):
            if os.path.exists(os.path.join(curr_path, filename)):
                return os.path.join(curr_path, filename)
        
        raise Exception('Slide not found : <%s>' % filename)
    
    # Given a music filename, locates the file within data paths and returns the
    # path to this file
    def find_music(self, filename):
        for curr_path in reversed(self.music_path):
            if os.path.exists(os.path.join(curr_path, filename)):
                return os.path.join(curr_path, filename)
        
        raise Exception('Music not found : <%s>' % filename)
    
    
    # Given a movie filename, locates the file within data paths and returns the
    # path to this file
    def find_movie(self, filename):
        for curr_path in reversed(self.movie_path):
            if os.path.exists(os.path.join(curr_path, filename)):
                return os.path.join(curr_path, filename)
        
        raise Exception('Movie not found : <%s>' % filename)
    
    # Given a sound filename, locates the file within data paths and returns the
    # path to this file
    def find_sound(self, filename):
        for curr_path in reversed(self.sound_path):
            if os.path.exists(os.path.join(curr_path, filename)):
                return os.path.join(curr_path, filename)
        
        raise Exception('Sound not found : <%s>' % filename)
    
    # Given a image filename, locates the file within data paths and returns the
    # path to this file
    def find_image(self, filename):
        for curr_path in reversed(self.image_path):
            if os.path.exists(os.path.join(curr_path, filename)):
                return os.path.join(curr_path, filename)
        
        raise Exception('Image not found : <%s>' % filename)
    
filemanager = FileManager()
