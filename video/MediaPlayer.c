#include "MediaPlayer.h"

// TODO
// change timing, not to depend on audio. ie mark video timestamps as video frame number
// and associate audio and video time using framerate and sample rate

// TODO
// create a generic push interface for video data
// re-make totest.c not to use MPP interface, but to make function calls directly, and to have a mp structure.
// organize and create mp access functions for width, height, etc.

static void *_worker_thread(void *data);

void mp_init(MediaPlayer *mp, const char *filename, int looping, const char *audio_class)
{
	// create a media player object
	// MediaPlayer *mp = (MediaPlayer *)malloc(sizeof(MediaPlayer));
	// a media player is used to play video or audio. It streams the data
	// from a file as it decodes it.
	
	// opens the playback file and preps the decoders
	mp->md = (MediaDecoder *)malloc(sizeof(MediaDecoder));
    printf("initializing md\n");
	md_init(mp->md, filename, 16*ABUFLEN, 24);
	
    mp->vidcbk = NULL;
    
	if(mp->md->has_audio)
	{
		// create an audio stream and connect it to the md object already
		mp->str = mixer_new_stream(mp, audio_class, mp->md->vinfo.channels);
        printf("stream initialized\n");
	}
	
	// stop
	mp->state = MP_STOP;
	mp->looping = looping;
    printf("mp_init done\n");
}

void mp_setVidCallback(MediaPlayer *mp, void (*vidcbk)(char *, void *), void *vidcbk_data)
{
    mp->vidcbk = vidcbk;
    mp->vidcbk_data = vidcbk_data;
}

void mp_play(MediaPlayer *mp)
{
	// start playback from whatever state the player is in
	mp->state = MP_PLAY;
	mp->pb_thread = MptThrCreate(&_worker_thread, mp);
}

void mp_stop(MediaPlayer *mp)
{
	// stops playback, but maintains state
	mp->state = MP_STOP;
	MptThrJoin(mp->pb_thread);
}

// TODO needs implementing internally
void mp_reset(MediaPlayer *mp)
{
	// cleans decoder state, and resets the decoder file pointer
	// player must be 'stopped' when this occurs
	if(!mp->state == MP_STOP)
	{
		printf("Can't reset while the player is playing\n");
		return;
	}
	// assume no-one called mp_stop at the same time
	md_reset(mp->md, 0);
}

void mp_close(MediaPlayer *mp)
{
	// clear all memory for this media player
	if(!mp->state == MP_STOP)
	{
		printf("Can't close while the player is playing\n");
		return;
	}
	mixer_close_stream(mp->str);
	md_close(mp->md);
	free(mp->md);
}

int mp_getWidth(MediaPlayer *mp)
{
    if(mp->md->has_video)
        return mp->md->tinfo.pic_width;
    return 0;
}

int mp_getHeight(MediaPlayer *mp)
{
    if(mp->md->has_video)
        return mp->md->tinfo.pic_height;
    return 0;
}

int mp_hasAudio(MediaPlayer *mp) { return mp->md->has_audio; }
int mp_hasVideo(MediaPlayer *mp) { return mp->md->has_video; }

// todo a media player can be given an external timer. How would this work?
static void *_worker_thread(void *data)
{
	MPTtimer ctimer; int stime;
	// also need: flag for stop
	int exitloop = 0;
	int looping = 1;
	
	// could use pthread_cond_wait to pause the thread, but because I can,
	// I believe it is better to destroy the thread and then recreate it,
	// only keeping the decoder state.	
	MediaPlayer *mp = (MediaPlayer *)data;
	
	// is there anything to play?
	if(!mp->md->has_audio && !mp->md->has_video)
		exitloop = 1;
	
    // TODO I want the option to take in an external timer
	ctimer = MptTimer();
	
    if( mp->md->has_video )
        stime = vindex2time(mp->md, 1);
    else if( mp->md->has_audio )
        stime = (1000*ABUFLEN) / mp->md->vinfo.rate;
    
	// stop should reset the decoder state and stop the playback thread (??)
	while(!exitloop)
	{
        printf("play!\n");
		while(!exitloop)
		{
			int buffull, res, vtime, atime, ctime;
			VideoFrame *frm;
            printf("\n");
			
            // res = md_fillBuffers(mp->md);
            res = md_incBuffers(mp->md);
            buffull = (res < 0);
            if(buffull)
                printf("    buffers are full\n");
            else
                printf("    res=%d\n", res);
            
            // res > 0 indicates eof or file read failure, and we have no more data to play.
			if(res > 0 || mp->state == MP_STOP) exitloop = 1;
            if(exitloop) printf("   Will Exit\n");
			
            // check if it is time to show the video, and otherwise how long should we pause?
            ctime = MptGetTime( ctimer );
            if( mp_hasAudio(mp) && mp_hasVideo(mp))
                printf("    Playback time: %d (sample %ld, frame %d)\n", ctime, (ctime*mp->md->vinfo.rate) / 1000, time2vindex(mp->md, ctime));
            
            // if it is time, process a video frame
            if( mp->md->has_video )
            {
                VideoFrame *frm = NULL;
                // vtime = vindex2time(mp->md, md_getNextVideoIndex(mp->md));
                vtime = md_getNextVideoIndex(mp->md);
                
                // when we find the right frame to display OR there is no 'next' frame,
                // then we either have the frame or ran out
                // printf("    Comparing %d and %d\n", vtime, time2vindex(mp->md, ctime));
                while( vtime <= time2vindex(mp->md, ctime) && vtime != -1)
                {
                    if( frm != NULL )
                        printf("    Skipped a video frame %d\n", vtime);
                    // buffull = 0;
                    frm = md_getVideo(mp->md);
                    vtime = md_getNextVideoIndex(mp->md);
                }
                
                if(frm != NULL && mp->vidcbk != NULL)
                {
                    printf("    Rendering Video %d\n", frm->vindex);
                    mp->vidcbk(frm->pixels, mp->vidcbk_data);
                }
            }
            
            // skip audio if necessary
            if( mp->md->has_audio )
            {
                // here I use atime as sample time
                atime = (ctime * mp->md->vinfo.rate) / 1000;
                printf("    current sample time: %d, vs %d on buffer\n", atime, md_getNextSampleNum(mp->md));
                // there are as many as ABUFLEN data in the SDL audio buffer, but I ignore it
                // convert atime to a difference between playback sample and current sample from stream
                atime = atime - md_getNextSampleNum(mp->md);
                if( atime > (80 * mp->md->vinfo.rate) / 1000) // 100 here is time
                {
                    // buffull = 0;
                    md_skipAudio(mp->md, atime);
                    printf("    Skipped %d audio\n", atime);
                }
            }
            
            // if the buffers are full, wait either until video time, or for a specified time (ie 100ms)
            if( buffull )
            {
                // stime = 40;
                printf("    Sleep for for %d \n", stime);
                MptSleep( stime );
            }
		} // exit on exitloop
		if(mp->looping)
		{
            exitloop = 0;
            printf("restarting stream\n");
            // if looping is on, md_reset(don't clear buffers) and then go back to the top
            md_reset(mp->md, 0);
        }
	}
    // tell the stream to end once it runs out of data
    mixer_end_stream(mp->str);
	// sleep untill buffers are empty
	stime = md_getAudioTime(mp->md);
	printf("last sleep for %d\n", 100 + stime);
    MptSleep( 100 + stime );
	// call the player "stopped". 
    mp->state = MP_STOP;
    // close and free data for the decoder
    md_close(mp->md);
	return NULL;
}

int mp_getAudio(MediaPlayer *mp, float *data, int len)
{
    // for now we just pass on the audio. We could do pause logic here?
    if(mp->state == MP_PLAY)
        return md_getAudio(mp->md, data, len);
    return 0;
}
