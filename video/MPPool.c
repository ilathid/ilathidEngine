#include "MediaPlayer.h"

void init_shaders();

#define MPP_MAX 100
MediaPlayer MPP_list[MPP_MAX];
char MPP_exists[MPP_MAX];
int MPP_inited = -1;
int MPP_new()
{
	int k;
	// check if this is the first time
	if(MPP_inited == -1)
	{
		for(k=0;k<MPP_MAX;k++)
			MPP_exists[k] = 0;
		MPP_inited = 0;
	}
	
	// get the first empty space
	for(k=0;k<MPP_MAX;k++)
		if(!MPP_exists[k]) break;
	if(k == MPP_MAX) return -1; // no more room
	MPP_exists[k] = 1;
	return k;
}
MediaPlayer *MPP_get(int mp_id)
{
	return MPP_list + mp_id;
}
void MPP_remove(int mp_id)
{
	MPP_exists[mp_id] = 0;
}




// access functions
int MPP_create(const char *filename, int looping, const char *audio_class)
{
	int mp = MPP_new();
    mp_init(MPP_get(mp), filename, looping, audio_class);
    return mp;
}
void MPP_play(int mp) { mp_play(MPP_get(mp)); }
void MPP_stop(int mp) { mp_stop(MPP_get(mp)); }
void MPP_close(int mp) { mp_close(MPP_get(mp)); }
int MPP_getWidth(int mp) { return mp_getWidth(MPP_get(mp)); }
int MPP_getHeight(int mp) { return mp_getHeight(MPP_get(mp)); }
// void MPP_init_shaders() { init_shaders(); }
