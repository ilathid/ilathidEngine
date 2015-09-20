#ifndef MEDIAPLAYER_H
#define MEDIAPLAYER_H

#include <stdio.h>
#include <pthread.h>
#include "packetbuffer.h"
#include "libavutil/avutil.h"
#include "libavutil/samplefmt.h"
#include "libavcodec/avcodec.h"
#include "libavformat/avformat.h"
#include "libswscale/swscale.h"
#include "libavutil/pixfmt.h"
#include "pthread.h"
#include "timehelper.h"
#include "alibrary.h"
#include "packetbuffer.h"

#define MAX_AUDIO_FRAME_SIZE 192000 // 1 second of 48khz 32bit audio

typedef enum {
    MP_EVENT_NONE,
    MP_EVENT_PAUSE,
    MP_EVENT_EOF
} mpevent;

typedef struct{
    char *filepath;
    
    int inited;                 // flag to indicate the media is opened
    int duration;
    
    PacketBuffer abuffer;       // static buffer for audio packets
    PacketBuffer vbuffer;       // static buffer for video packets
    AVStream *vstream;          
    AVStream *astream;
    AVFormatContext *fmt_ctx;

                                // Small buffer for processed audio
    short int *outbuf;
    int outbuf_size;
    int outbuf_len;

    ADevice device;             // audio output device (alibrary.h)
    thTimer playTimer;           // playback is from this base startTime
    unsigned int pauseTime;       // used when stopped to remember playback time
    
    pthread_t thread;           // decoding thread

    int tstate;                 
    mpevent event;              // for thread termination
    int looping;                // just for transfer into thread

    pthread_mutex_t mut_pic;    // mutex for rendered image    
    int picacq;                 // flag to indicate if memory should be freed
    AVPicture picbuf;           // last rendered picture
    int picw, pich;             // picture properties
    
    struct SwsContext* conv;    // remember context for better mem management, speed
    
} MediaPlayer;

// mpframe is for passing data out of MediaPlayer
typedef struct {
    char *data;
    int len;        // total data length, in bytes
    int width;
    int height;
} mpframe;

int init_mp(MediaPlayer *mp, char *filepath);
void close_mp(MediaPlayer *mp);
void setVolMono_mp(MediaPlayer *mp, float vol);
void setVol_mp(MediaPlayer *mp, float voll, float volr);
int hasAudio_mp(MediaPlayer *mp);
int hasVideo_mp(MediaPlayer *mp);
int getPlaybackTime_mp(MediaPlayer *mp);
// void setPauseTime_mp(MediaPlayer *mp, int pauseTime);
int getPauseTime_mp(MediaPlayer *mp);
void reset_mp(MediaPlayer *mp);
void play_mp(MediaPlayer *mp);
long getDuration_mp(MediaPlayer *mp);
void seek_mp(MediaPlayer *mp, int time);
void loop_mp(MediaPlayer *mp);
int getState_mp(MediaPlayer *mp);
void interrupt_mp(MediaPlayer *mp);
mpframe getFrame_mp(MediaPlayer *mp);
void free_mpframe(mpframe *fr);
int getVidWidth_mp(MediaPlayer *mp);
int getVidHeight_mp(MediaPlayer *mp);
int _pread_mp(MediaPlayer *mp, int apackets, int vpackets);
void *_playbackLoop_mp(MediaPlayer *mp);
LONG _correctPts_mp(AVStream *stream, LONG pts);
void _processAudio_mp(MediaPlayer *mp);
void _processVideo_mp(MediaPlayer *mp);

#endif
