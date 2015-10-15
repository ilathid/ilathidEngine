#include <stdio.h>
#include <sys/time.h>
#include <string.h> // memcpy

#include "ogg/ogg.h"
#include "vorbis/codec.h"
#include "theora/theoradec.h"
//#include "theora/theora.h"

#include "VideoBuffer.h"
#include "Mixer.h"

#ifdef _WIN32
#include <windows.h>
#define MPTmut	HANDLE
#define MPTthr	HANDLE
#define MPTtimer	SYSTEMTIME
#else
#include <pthread.h>
#include <unistd.h>
#define MPTmut	pthread_mutex_t
#define MPTthr	pthread_t
#define MPTtimer	struct timeval
#endif

#ifndef MEDIADECODER_H
#define MEDIADECODER_H

static MPTtimer MptTimer()
{
    MPTtimer ret;
#	ifdef _WIN32
    GetSystemTime(&ret);
#	else
    gettimeofday(&ret, NULL);
#	endif
    return ret;
}

static void MptSleep(int tmsec)
{
#	ifdef _WIN32
    sleep(tmsec);
#	else
    usleep(tmsec*1000);
#	endif
}

// get time elapsed on the timer in milliseconds
static int MptGetTime(MPTtimer timer)
{
    MPTtimer ntime;
    int ret;
#	ifdef _WIN32
    GetSystemTime(&ntime);
    ret = (ntime.wHour - timer.wHour)*(24*60*1000) + (ntime.wMinute - timer.wMinute)*(60*1000) + (ntime.wSecond - timer.wSecond)*(1000) + (ntime.wMilliseconds - timer.wMilliseconds);
#	else
    gettimeofday(&ntime, NULL);
    ret = (ntime.tv_sec - timer.tv_sec)*1000 + (ntime.tv_usec - timer.tv_usec) / 1000;
#	endif
    return ret;
}

#ifdef _WIN32
static MPTthr MptThrCreate(_In_ LPTHREAD_START_ROUTINE lpStartAddress, void *data)
{
    return CreateThread(NULL, 0, lpStartAddress, data, 0, NULL);
}
#else
static MPTthr MptThrCreate(void *(*start_routine)(void *), void *data)
{
    MPTthr ret;
    if(pthread_create(&ret, NULL, start_routine, data))
	printf("Failed to create thread!\n");
    return ret;
}
#endif

static void MptThrJoin(MPTthr target_join)
{
#	ifdef _WIN32
    WaitForSingleObject(target_join, INFINITE);
#	else
    pthread_join(target_join, NULL);
#	endif
}

static void MptThrExit()
{
#	ifdef _WIN32
    ExitThread(0);
#	else
    pthread_exit(NULL);
#	endif
}

static void MptMutCreate(MPTmut mut)
{
#	ifdef _WIN32
    mut = CreateMutex(NULL, 0, NULL);
#	else
    pthread_mutex_init(&mut, NULL);
#	endif
}

static void MptMutDestroy(MPTmut mut)
{
#	ifdef _WIN32
    CloseHandle(mut);
#	else
    pthread_mutex_destroy(&mut);
#	endif
}

static void MptMutLock(MPTmut mut)
{
#	ifdef _WIN32
    WaitForSingleObject(mut, INFINITE);
#	else
    pthread_mutex_lock(&mut);
#	endif
}

static void MptMutUnlock(MPTmut mut)
{
#	ifdef _WIN32
    ReleaseMutex(mut);
#	else
    pthread_mutex_unlock(&mut);
#	endif
}

typedef struct MediaDecoder{
    // has video/audio
    int has_audio;
    int has_video;

    // ogg state
    ogg_sync_state sync;
    
    // vorbis state
    vorbis_info vinfo;
    ogg_stream_state vstream;
    vorbis_dsp_state vdsp;
    vorbis_block vblock;
    
    // theora state
    th_info tinfo;
    ogg_stream_state tstream;
    th_dec_ctx *tdec;
    
    // file pointer
    FILE *file;
    const char *filename;
    
    // audio buffer
    // CBuffer aBuffer;
    char *aBuffer;
    int bps; // bytes per sample
    int abufsize;
    int abuflen;
    MPTmut ablenmut;
    long acnt;
    int vcnt;
    
    // video buffer
    VBuffer vBuffer;
    int bpf; // bytes per video frame
    
} MediaDecoder;

void md_init(MediaDecoder *md, const char *filename, int abufsize);
int md_fillBuffers(MediaDecoder *md);
VideoFrame *md_getVideo(MediaDecoder *md, int asample);
int md_getNextVideoSync(MediaDecoder *md);
int md_getNextSampleNum(MediaDecoder *md);
int md_getAudio(MediaDecoder *md, float *data, int len);
int md_getAudioTime(MediaDecoder *md);
int md_skipAudio(MediaDecoder *md, int samples);
void md_close(MediaDecoder *md);
void md_reset(MediaDecoder *md, int clear_buffers);

#endif
