#include "Mixer.h"

/*

Changes:
- all data in is in pcm float format. We do a conversion to the desired output
- audio will be naievly converted up or down to the number of channels desired


*/

AudioMixer mixer;
int minit = 0;

// int mp_getAudio(struc MediaPlayer *mp, float *data, int len)

// data is where we should put the audio in the audio spec format
// len is the number of bytes requested
static void SDLCALL mixer_mix(void *userdata, Uint8 *data, int len)
{
    int req_samples;
    
    // printf("Mixing Audio\n");
    
    // initialize the stream to 0
    SDL_memset(data, 0, len*sizeof(Uint8));
    if(minit != 1) return; // this should not even be possible

    if(mixer.spec->format != AUDIO_S16SYS)
    {
	    printf("Audio format not supported: use AUDIO_S16SYS\n");
	    return;
    }
	
    Sint16 *cdata = (Sint16 *)data;
    req_samples = len/(ACHANNELS*ABITSIZE/8); // NOTE: I think SDL_AUDIO_BITSIZE gives the bit size for a single channel's sample, while SDL indicated elsewhere a sample is a set of data points for all channels in a stream
    
    // printf("\n  Mixer: requested %d data or %d samples\n", len, req_samples);
    
    // printf("want to mix %d samples\n", req_samples);
    
    // 2-loop method
    // This is just in case there are many audio streams, and we want to 
    // automatically decrease overall volume of the audio data chunk to remove clipping
    // printf("Reading Streams\n");
    AudioStream *stream = mixer.stream_first;
    AudioStream *prev = NULL;
    while(stream != NULL)
    {
        stream->got_len = stream->input_channels * req_samples;
        
        assert(stream->buflen >= get_len);
        // buffer must be large enough to hold ABUFLEN * stream->input_channels
        stream->got_len = mp_getAudio(stream->mp, stream->buffer, stream->got_len);
        
        if(stream->got_len != stream->input_channels * req_samples)
            printf( "FAILED TO GET AUDIO (got %d)\n", stream->got_len );
        
        // check if we should close and remove the stream
        if((stream->got_len == 0 && stream->flag == MIXER_STR_END) || stream->flag == MIXER_STR_CLOSE)
        {
            // This stream has ended. Skip it in the list
            if(prev == NULL)
                mixer.stream_first = stream->next;
            else
                prev->next = stream->next;
            // remove the stream
            SDL_free(stream->buffer);
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
        float volume; int mix,k;
        // printf("\n Got a stream for mixing...\n");
        // could get mp position, etc for stereo sound
        volume = mixer.classes[stream->class].volume / 255.0;
        
		// must mix down (or up) to ACHANNELS number of channels
		// Note: there should be a special case here for 3d sound, which is always 1-channel
		if(mixer.spec->channels == stream->input_channels)
		{
            //printf("Mixing same channel number\n");
		    // scale the sample and mix with capping
			for(k=0;k<stream->got_len;k++)
			{
				// mix audio into data stream
                // printf("%f ", stream->buffer[k]);
				mix = cdata[k] + (int)(32767.0f * (stream->buffer[k] * volume));
				cdata[k] = max(min(mix, 32767), -32768);
			}
            // printf("\n");
		}
		if(mixer.spec->channels > stream->input_channels)
		{
			if( mixer.spec->channels % stream->input_channels != 0)
				printf("Output channels (%d) must be a multiple of stream channels (%d)\n", mixer.spec->channels, stream->input_channels);
			else
			{
				int mult = mixer.spec->channels / stream->input_channels;
				for(k=0;k<stream->got_len;k++)
				{
					int j;
					// mix audio into data stream
					for(j = 0; j < mult; j++){
						mix = cdata[k*mult+j] + (int)(32767.0f * (stream->buffer[k] * volume));
						cdata[k*mult+j] = max(min(mix, 32767), -32768);
					}
				}
			}
		}
		if(mixer.spec->channels < stream->input_channels)
		{
			if( stream->input_channels % mixer.spec->channels != 0)
				printf("Stream channels (%d) must be a multiple of output channels (%d)\n", stream->input_channels, mixer.spec->channels);
			else
			{
				int mult = stream->input_channels / mixer.spec->channels;
				for(k=0;k<stream->got_len/mult;k++)
				{
					int j;
					mix = 0;
					// take an average
					for(j = 0; j < mult; j++)
						mix += (stream->buffer[k*mult+j] * volume);
					mix = cdata[k] + mix / mult;
					cdata[k] = max(min(mix, 32767), -32768);
				}
			}
		}
        stream = stream->next;
    }
    // printf("Done Mixing\n");
}

void mixer_new_class(const char *class)
{
	AudioClass *ac = mixer.classes + mixer.num_classes;
	ac->name = class;
	ac->volume = 255;
	mixer.num_classes++;
}

static int _get_class(const char *class)
{
    int k;
    // find the class
    for( k=0; k < mixer.num_classes; k++)
    {
        // printf("compare to %s\n", mixer.classes[k].name);
        if( strcmp( mixer.classes[k].name, class ) == 0 ) break;
    }
    if( k == mixer.num_classes )
        return -1;
    return k;
}

void mixer_set_volume(const char *class, int volume)
{
    int k;
    k = _get_class(class);
    if(k == -1)
    {
        printf("Can't set volume, no class called %s\n", class);
        return;
    }
    mixer.classes[k].volume = volume;
    // printf("Set volume to %d\n", volume);
}

AudioStream *mixer_new_stream(struct MediaPlayer *mp, const char *class, int num_channels)
{
    int k, sfmt, schannels, sfreq, sbitsize;

    printf("Called mixer_new_stream(mp,\"%s\",%d)\n", class, num_channels);

    if(minit != 1)
    {
        printf("Mixer is not initialized!\n");
        return NULL;
    }
    
    k = _get_class(class);
    if( k == -1 )
    {
        printf("mixer error: no class %s found.\n", class);
        return NULL;
    }
    
    AudioStream *news = (AudioStream *)malloc(sizeof(AudioStream));
    news->next = NULL;
    news->class = k;
    news->mp = mp;
    news->flag = MIXER_STR_CONT;
    news->input_channels = num_channels;
    
    news->buflen = ABUFLEN * num_channels; // ABUFLEN is number of samples / number of channels;
    news->buffer = (float *)malloc(sizeof(float)*news->buflen);
    
    // add to linked list
    if( mixer.stream_last == NULL )
    {
        printf("Added first stream\n");
        mixer.stream_first = news;
        mixer.stream_last = news;
    }
    else
    {
        printf("Added another stream\n");
        mixer.stream_last->next = news;
        mixer.stream_last = news;
    }
    return news;
}

// close the stream as soon as possible
void mixer_close_stream(AudioStream *str)
{
	str->flag = MIXER_STR_CLOSE;
}

// close the stream once the target audio buffer is empty
void mixer_end_stream(AudioStream *str)
{
	str->flag = MIXER_STR_END;
}

void mixer_init(){
    // check that sdl audio is initialized
    int res;
    printf("mixer initializing\n");
    // Uint32 was_init = SDL_WasInit(SDL_INIT_EVERYTHING);
    // if( !was_init )
    // {
    //     printf("Mixer: must initialize SDL first!\n");
    //     return;
    // }
    // if( was_init && !(was_init & SDL_INIT_AUDIO))
    //     SDL_InitSubSystem(SDL_INIT_AUDIO);

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
    //memset(mixer.spec, '\0', sizeof (SDL_AudioSpec));
    mixer.spec = (SDL_AudioSpec *)malloc(sizeof(SDL_AudioSpec));
    memset(mixer.spec, '\0', sizeof (SDL_AudioSpec));
    mixer.spec->freq = ASAMPLEFREQ;
    mixer.spec->format = AFORMAT;
    mixer.spec->channels = ACHANNELS;
    mixer.spec->samples = ABUFLEN;
    mixer.spec->callback = mixer_mix;
    mixer.spec->userdata = NULL;

    printf("Req: freq %d, format %d, channels %d, samples %d, callback %llx\n", mixer.spec->freq, mixer.spec->format, mixer.spec->channels, mixer.spec->samples, (unsigned long long)mixer.spec->callback);

    res = SDL_OpenAudio(mixer.spec, mixer.spec);
    if( res == -1 )
        fprintf(stderr, "Couldn't open audio: %s\n", SDL_GetError());
    else
    {
        printf("Got: freq %d, format %d, channels %d, samples %d, callback %llx\n", mixer.spec->freq, mixer.spec->format, mixer.spec->channels, mixer.spec->samples, (unsigned long long)mixer.spec->callback);

        minit = 1;
        
        // turn on the audio!
        SDL_PauseAudio(0);
    }
}

void mixer_close()
{
	// delete all streams
	AudioStream *stream = mixer.stream_first;
    AudioStream *prev = NULL;
    while(stream != NULL)
    {
		// remove the stream
		SDL_free(stream->buffer);
		free(stream);
		// prev stays the same
		stream = stream->next;
	}
	minit = 0;
    free(mixer.spec);
}
