#include "VideoFrame.h"
#include "VideoBuffer.h"
#include "AudioBuffer.h"
#include "MPThreading.h"

#ifndef MEDIADECODER_H
#define MEDIADECODER_H

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
    
    // audio buffer
    // CBuffer aBuffer;
    char *aBuffer;
    int bps; // bytes per sample
    int abufsize;
    int abuflen;
    MPTmut ablenmut;
    long acnt;
    
    // video buffer
    PBuffer vBuffer;
    int bpf; // bytes per video frame
    
} MediaDecoder;

typedef struct VideoFrame{
    // timestamp
    char *pixels;
    int async;
} VideoFrame;

#endif
