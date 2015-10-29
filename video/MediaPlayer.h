#include "MediaDecoder.h"
#include "Mixer.h"

#ifndef MEDIAPLAYER_H
#define MEDIAPLAYER_H

#define MP_STOP	0
#define MP_PLAY	1

// definition for mpGLUpdate.c
// void update_tex(char *pixels, int gltex, int w, int h);

typedef struct MediaPlayer{
	AudioStream *str;
	const char *filename;
	MediaDecoder *md;
	MPTthr pb_thread;
	int state; // MP_STOP, MP_PLAY
	int looping;
    void (*vidcbk)(char *, void *);
    void *vidcbk_data;
} MediaPlayer;

void mp_init(MediaPlayer *mp, const char *filename, int looping, const char *audio_class);
void mp_play(MediaPlayer *mp);
void mp_stop(MediaPlayer *mp);
void mp_reset(MediaPlayer *mp);
void mp_close(MediaPlayer *mp);
void mp_setVidCallback(MediaPlayer *mp, void (*vidcbk)(char *, void *), void *vidcbk_data);
int mp_getWidth(MediaPlayer *mp);
int mp_getHeight(MediaPlayer *mp);
int mp_hasAudio(MediaPlayer *mp);
int mp_hasVideo(MediaPlayer *mp);
int mp_isPlaying(MediaPlayer *mp);
int mp_getAudio(MediaPlayer *mp, float *data, int len);

#endif
