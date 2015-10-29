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
#   include <windows.h>
#   define MPTmut	HANDLE
#   define MPTthr	HANDLE
#   define MPTtimer	SYSTEMTIME
#else
#   include <pthread.h>
#   include <unistd.h>
#   define MPTmut	pthread_mutex_t
#   define MPTthr	pthread_t
#   define MPTtimer	struct timeval
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

static MPTmut *MptMutCreate()
{
    MPTmut *mut;
#	ifdef _WIN32
    mut = CreateMutex(NULL, 0, NULL);
#	else
    // need a malloc to copy windows!
    mut = (MPTmut *)malloc(sizeof(MPTmut));
    if(pthread_mutex_init(mut, NULL))
        return NULL;
#	endif
    return mut;
}

static void MptMutDestroy(MPTmut *mut)
{
#	ifdef _WIN32
    CloseHandle(mut[0]);
#	else
    pthread_mutex_destroy(mut);
    free(mut);
#	endif
}

static void MptMutLock(MPTmut *mut)
{
#	ifdef _WIN32
    WaitForSingleObject(mut[0], INFINITE);
#	else
    pthread_mutex_lock(mut);
#	endif
}

static void MptMutUnlock(MPTmut *mut)
{
#	ifdef _WIN32
    ReleaseMutex(mut[0]);
#	else
    pthread_mutex_unlock(mut);
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
    int abufhead;
    int abuftail;
    int abuffull;
    int toskipaudio;
    //  [	t-------h	]
    //  [-------h	t-------]
    //  [---h		    t---]
    //  full when h==t, empty when t==h-s
    // 
    //  len = (h - t + s)
    //  if( h != t ) len = len % s;
    // 
    //  When h==t, he get len=s, ie the buffer is full
    //  When h==t-s, we get len=0, ie the buffer is empty
    //  Otherwise, we get the correct length
    
    // MPTmut *ablenmut;
    long acnt;
    int vcnt;
    
    // video buffer
    VBuffer vBuffer;
    int bpf; // bytes per video frame
    
} MediaDecoder;

// create the decoder, open the file, init the decoders
void md_init(MediaDecoder *md, const char *filename, int abufsize, int vbufsize);

// put some data on the buffers
int md_incBuffers(MediaDecoder *md);
// fill the buffers
// int md_fillBuffers(MediaDecoder *md);

int md_readPage(MediaDecoder *md);

int md_processPackets(MediaDecoder *md);


// get the next video frame
VideoFrame *md_getVideo(MediaDecoder *md);

// get video frame index n, skipping any inbetween. Return NULL if n is not available
// VideoFrame *md_getVideo_n(MediaDecoder *md, int n);

// int md_getNextVideoSync(MediaDecoder *md);
int md_getNextSampleNum(MediaDecoder *md);

// get the index number of the next video frame
int md_getNextVideoIndex(MediaDecoder *md);

// get len data points of audio (ie len/channels number of samples)
int md_getAudio(MediaDecoder *md, float *data, int len);

// get time remaining on audio buffer
int md_getAudioTime(MediaDecoder *md);

void md_skipAudio(MediaDecoder *md, int samples);
void md_close(MediaDecoder *md);
void md_reset(MediaDecoder *md, int clear_buffers);

int time2vindex(MediaDecoder *md, int time_ms);
int vindex2time(MediaDecoder *md, int vindex);

#endif
