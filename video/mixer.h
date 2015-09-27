#include "SDL.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

// for testing:
// cc -I/usr/local/include/SDL -c mixer.c -o mixer.o

// TODO stream has its own volume setting which should be combined with the class volume setting?

// includes SDL
// creates an SDL spec
// manages classes, streams
// the SDL callback looks at all streams, gets data from all streams, and mixes them according to classes and class volumes

// TODO: make sure these are the same in sdl 1.2 from sdl 2
#define SDL_AUDIO_MASK_BITSIZE (0xFF)
#define SDL_AUDIO_MASK_SIGNED (1<<15)
#define SDL_AUDIO_BITSIZE(x) (x & SDL_AUDIO_MASK_BITSIZE)
#define SDL_AUDIO_ISSIGNED(x) (x & SDL_AUDIO_MASK_SIGNED)

// len is of size 2048 x 2 x 2 (samples in buffer, channels, 16 bits = 2 bytes)
#define ABUFLEN 2048
#define ACHANNELS 2
#define ASAMPLEFREQ 22050
#define AFORMAT AUDIO_S16SYS // please use signed or unsigned, not float
#define ABITSIZE SDL_AUDIO_BITSIZE(AFORMAT & SDL_AUDIO_MASK_BITSIZE)

// dummy
typedef struct MediaPlayer {
    Uint16 audio_format;
    int audio_channels;
    int audio_freq;
    int (*get_audio)(Uint8 *stream, int len); // like copy from SDL. return value is 0 normally, 1 to terminate the stream
} MediaPlayer;

/*Function to find minimum of x and y*/
static int min(int x, int y)
{
  return y ^ ((x ^ y) & -(x < y));
}
 
/*Function to find maximum of x and y*/
static int max(int x, int y)
{
  return x ^ ((x ^ y) & -(x < y)); 
}

// classes can be added, not removed.
typedef struct AudioClass {
    char *name;
    int volume; // 0 to 255
} AudioClass;

// Streams can be removed
typedef struct AudioStream {
    int class;
    MediaPlayer *mp;
    //int (*callback)(Uint8 *stream, int vol, int len); // like copy from SDL. return value is 0 normally, 1 to terminate the stream
    struct AudioStream *next;
    SDL_AudioCVT cvt; // contains a buffer and used for conversion
} AudioStream;

typedef struct AudioMixer {
    // Audio Classes, max 100
    AudioClass classes[100];
    int num_classes;
    
    // Audio Stream List
    AudioStream *stream_first;
    AudioStream *stream_last;
    
    // SDL
    SDL_AudioSpec spec;
} AudioMixer;

void mixer_new_stream(MediaPlayer *mp, char *class);
void mixer_init();
