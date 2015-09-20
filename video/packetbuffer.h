#ifndef PACKETBUFFER_H
#define PACKETBUFFER_H

#include <stdio.h>
#include "libavcodec/avcodec.h"

#ifdef __MINGW32__
#include <windows.h>
#else
typedef int64_t LONG;
#endif

typedef struct{
    AVPacket packets[1000];
    int r_i;     // Where is reading happening from?
    int size;    // How many packets are in the buffer?
    int maxSize;
} PacketBuffer;

void init_pb(PacketBuffer *pb);

int getSize_pb(PacketBuffer *pb);

int getLeft_pb(PacketBuffer *pb);

AVPacket *getRead_pb(PacketBuffer *pb);

AVPacket *bottom_pb(PacketBuffer *pb);

LONG nextPts_pb(PacketBuffer *pb);

AVPacket *top_pb(PacketBuffer *pb);

AVPacket *getWrite_pb(PacketBuffer *pb);

void clear_pb(PacketBuffer *pb);

#endif
