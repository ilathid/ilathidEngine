#include <stdio.h>
#include <stdlib.h>

#ifndef VIDEOBUFFER_H
#define VIDEOBUFFER_H

typedef struct VideoFrame{
    // timestamp
    char *pixels;
    int vindex;
} VideoFrame;

typedef struct VBuffer{
    VideoFrame *buffer;
    int bufsize;
    int tail;
    int len;
    // MptMut lenlock;
} VBuffer;

// P(ointer) buffer
void VBinit(VBuffer *buf, int bufsize, int vfsize);
void VBdestroy(VBuffer *buf);

// get a reference to the next 'push' item. grrr, ie get an invalid item, and overwrite its contents
VideoFrame *VBgetAddItem(VBuffer *buf);

// return a pointer to the next video frame without removing it from the buffer
VideoFrame *VBpeak(VBuffer *buf);

// return a pointer to the next video frame and remove it from the buffer. The memory may be re-written on the next Ppush
VideoFrame *VBgetRemoveItem(VBuffer *buf);

// How many more video frames could be added?
int VBroom(VBuffer *buf);

#endif
