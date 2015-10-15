#include "MediaPlayer.h"

static void *_worker_thread(void *data);

void mp_init(MediaPlayer *mp, const char *filename, int looping, const char *audio_class, int gltex)
{
	// create a media player object
	// MediaPlayer *mp = (MediaPlayer *)malloc(sizeof(MediaPlayer));
	// a media player is used to play video or audio. It streams the data
	// from a file as it decodes it.
	
	// opens the playback file and preps the decoders
	mp->md = (MediaDecoder *)malloc(sizeof(MediaDecoder));
	md_init(mp->md, filename, 4*ABUFLEN); // decoder audio buffer is 4 times SDL audio buffer
	
	if(mp->md->has_audio)
	{
		// create an audio stream and connect it to the md object already
		// this could be changed, so that the get_audio is in this file,
		// if things like pausing are needed, so that the audio playback
		// can be paused without emptying the md audio buffer
		mp->str = mixer_new_stream(mp, audio_class, mp->md->vinfo.channels);
	}
	
	// stop
	mp->state = MP_STOP;
	mp->looping = looping;
	mp->gltex = gltex;
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
	
	if(!mp->md->has_audio){
		// set up a millisecond-accurate timer for video playback
		ctimer = MptTimer();
	}
	
	// stop should reset the decoder state and stop the playback thread (??)
	while(1)
	{
		while(!exitloop)
		{
			int res, vtime, atime;
			VideoFrame *frm;
			//!  fill buffers
			res = md_fillBuffers(mp->md);
			//   > if result of fill buffers is 1, we are done. (exit at the end loop of loop block)
			//   > also, we are done at this point if a flag is set indicating mp_stop was called
			if(res != 0 || mp->state == MP_STOP) exitloop = 1;
			//   call int md_getNextVideoSync(MediaDecoder md) to get next video time in samples
			vtime = md_getNextVideoSync(mp->md);
			//   get the next audio samepl num, asample
			atime = md_getNextSampleNum(mp->md);
			//   use asample and next video sample time to get a wait time in samples, 
			//   and convert to a wait time in seconds using the audio samplerate (vsamp - asamp)/samplerate
			stime = 0;
			if(mp->md->has_audio)
			{
				if(vtime > atime)
					stime = (1000*(vtime - atime)) / mp->md->vinfo.rate;
			}
			else
			{
				atime = MptGetTime( ctimer );
				if(vtime > atime)
					stime = vtime - atime;
			}
			//!  if long enough, sleep that long
			if(stime > 50) MptSleep(stime);
			//   run VideoFrame *md_getVideo(int asample) to get a video frame (skips up to vbuflen video frames to catch up)
			frm = md_getVideo(mp->md, atime);
			//!  draw the video frame:
			if(frm != NULL)
				update_tex(frm->pixels, mp->gltex, mp->md->tinfo.pic_width, mp->md->tinfo.pic_height);
		} // if buffer was full, or flag inficates stop, exit
		if(!mp->looping)
			break;
		// if looping is on, md_reset(don't clear buffers) and then go back to the top
		md_reset(mp->md, 0);
	}
	// sleep untill buffers are empty
	// if not looping, get audio time in md audio buffer, and sleep longer than that for SDL to clear the buffer
	stime = md_getAudioTime(mp->md);
	MptSleep( 100 + stime );
	md_reset(mp->md, 1);
	// call the player "stopped"
	mp->state = MP_STOP;
	return NULL;
}

int mp_getAudio(MediaPlayer *mp, float *data, int len)
{
	// for now we just pass on the audio. We could do pause logic here?
	return md_getAudio(mp->md, data, len);
}
