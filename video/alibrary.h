#ifndef ALIBRARY_H
#define ALIBRARY_H

#include <stdio.h>
#include "timehelper.h"
#include "ao/ao.h"
#include <pthread.h>
#include <math.h>

#define ALIBRARY_AUDIO_SIZE 4608
   
typedef struct {
    int opened;
    unsigned int byterate;
    ao_device *device;
    ao_sample_format fmt;
    unsigned int msBuffer; // when did the current sound data start playing?
    thTimer msTimer; // how much sound (in time) has been put on the buffer since
    //volume and such
    unsigned char voll;     // also used for mono
    unsigned char volr;
    // length of an audio sample
    int len;
} ADevice;

// audio on buffer = nsstart + nsdelta - h_time() 

void init_ad(ADevice *ad, int bits, int channels, int rate);
void setVol_ad(ADevice *ad, float voll, float volr);
int atime_ad(ADevice *ad);
void play_ad(ADevice *ad, char *data, int len);
void close_ad(ADevice *ad);
void initialize_al(void);
void shutdown_al(void);
void adjustSample_ad(ADevice *ad, char *data, int len);

#endif
