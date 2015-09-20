#include "SDL.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

// TODO stream has its own volume setting which should be combined with the class volume setting?

// includes SDL
// creates an SDL spec
// manages classes, streams
// the SDL callback looks at all streams, gets data from all streams, and mixes them according to classes and class volumes

// len is of size 2048 x 2 x 2 (samples in buffer, channels, 16 bits = 2 bytes)
#define ABUFLEN 2048
#define ACHANNELS 2
#define ASAMPLEFREQ 22050
#define AFORMAT AUDIO_S16SYS // please use signed or unsigned, not float
#define ABITSIZE SDL_AUDIO_BITSIZE(AFORMAT & SDL_AUDIO_MASK_BITSIZE)

// dummy
typedef struct MediaPlayer {
    SDL_AudioFormat audio_format;
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

AudioMixer mixer;

// data is where we should put the audio in the audio spec format
// len is the number of bytes requested
static void SDLCALL mixer_mix(void *userdata, Uint8 *data, int len)
{
    int req_samples;
    req_samples = len/(ABITSIZE/8);
    
    // initialize the stream to 0
    SDL_memset(data, 0, len);
    
    // loop through the streams
    AudioStream *stream = mixer.stream_first;
    AudioStream *prev = NULL;
    while(stream != NULL)
    {
        int need_len,endstr;
        
        // I need to load audio into the conversion buffer.
        // I need enough audio so that after conversion we will have len bytes of audio data
        need_len = len / stream->cvt.len_ratio;
        
        // need_len must not exceed stream->cvt.len
        // this should be satisfied because the cvt.buf has space for as many samples as SDL's buffer
        SDL_assert(stream->cvt.len>=need_len);
        endstr = stream->mp->get_audio(stream->cvt.buf, need_len);
        
        if(endstr == 1)
        {
            // This stream has ended. Skip it in the list
            if(prev == NULL)
                mixer.stream_first = stream->next;
            else
                prev->next = stream->next;
            // remove the stream
            SDL_free(stream->cvt.buf);
            free(stream);
            // prev stays the same
            stream = stream->next;
        }
        else
        {
            prev = stream;
            stream = stream->next;
        }
    }
    
    // loop through the streams again
    stream = mixer.stream_first;
    while(stream != NULL)
    {
        int volume, k; long long int mix;
        Sint16 *buffer; // asserted
        int b_len;
        
        // could get mp position, etc for stereo sound
        volume = mixer.classes[stream->class].volume;
        
        // do conversion if needed
        if(stream->cvt.needed) SDL_ConvertAudio(&(stream->cvt));
        assert(stream->cvt.len_cvt <= len);
        
        // must cast the buffer so as to be able to work with it
        assert( ABITSIZE == 16 ); // just change the code if this changes
        assert( SDL_AUDIO_ISSIGNED( AFORMAT ));
        buffer = (Sint16 *)stream->cvt.buf;
        b_len = stream->cvt.len_cvt / (ABITSIZE/8);

        // mix is 63 bits long. stream is at most 32 bits. volume is at most 8 bits. volume*stream fits in mix
        // scale the sample and mix with capping
        for(k=0;k<b_len;k++)
        {
            // mix audio into data stream
            mix = data[k] + (buffer[k] * volume) / 255;
            // following is asserted
            data[k] = max(min(mix, 32767), -32768);
        }
        stream = stream->next;
    }
}

void mixer_new_stream(char *class, MediaPlayer *mp){
    int k, sfmt, schannels, sfreq, sbitsize;

    // find the class
    for( k=0; k < mixer.num_classes; k++)
        if( strcmp( mixer.classes[k].name, class ) == 0 ) break;
    if( k == mixer.num_classes )
    {
        printf("mixer error: no class %s found.\n", class);
        return;
    }
    
    AudioStream *news = (AudioStream *)malloc(sizeof(AudioStream));
    news->class = k;
    news->mp = mp;
    
    // build the converter
    sfmt = mp->audio_format;
    schannels = mp->audio_channels;
    sfreq = mp->audio_freq;
    sbitsize = (sfmt & SDL_AUDIO_MASK_BITSIZE);
    
    SDL_BuildAudioCVT(&(news->cvt), sfmt, schannels, sfreq, AFORMAT, ACHANNELS, ASAMPLEFREQ);
    news->cvt.len = ABUFLEN * schannels * sbitsize;
    news->cvt.buf = (Uint8 *) SDL_malloc(news->cvt.len * news->cvt.len_mult);
    
    // add to linked list
    if( mixer.stream_last == NULL )
    {
        mixer.stream_first = news;
        mixer.stream_last = news;
    }
    else
    {
        mixer.stream_last->next = news;
        mixer.stream_last = news;
    }
}

void mixer_init(){
    // assert
    if( ACHANNELS > 2 )
    {
        printf("MIXER ERROR: NO SUPPORT FOR MORE THAN 2 STREAM CHANNELS\n");
        return;
    }
    
    // init
    mixer.stream_first = NULL;
    mixer.stream_last = NULL;
    mixer.num_classes = 0;

    // A desired output format and frequency has to be chosen here
    // For now:
    //  AUDIO_S16SYS, 2 channels, 22050 freq
    memset(&(mixer.spec), '\0', sizeof (SDL_AudioSpec));
    mixer.spec.freq = ASAMPLEFREQ;
    mixer.spec.format = AFORMAT;
    mixer.spec.channels = ACHANNELS;
    mixer.spec.samples = ABUFLEN;
    mixer.spec.callback = mixer_mix;
}
