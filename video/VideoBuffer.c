#include "VideoBuffer.h"

void VBInit(VBuffer *buf, int bufsize, int vfsize)
{
    int k;
    buf->bufsize = bufsize; // maximum amnt of data that can be put on the buffer
    buf->buffer = (VideoFrame *)malloc(sizeof(VideoFrame)*(bufsize));
    buf->tail = 0;          // where are we reading data from? head is (tail+len) % bufsize
    buf->len = 0;           // how much data in samples is on the buffer
    // MptMutCreate(buf->lenlock); // NOTE: no need for mutex, incrementing is an atomic operation
    
    for(k=0;k<bufsize;k++)
    {
        buf->buffer[k].async = -1;
        buf->buffer[k].pixels = (char *)malloc(sizeof(char) * vfsize);
    } // end for
} // end VBinit

void VBdestroy(VBuffer *buf)
{
    int k;
    for( k=0; k<buf->bufsize; k++)
        free(buf->buffer[k].pixels);
    free(buf->buffer);
    // MptMutDestroy(buf->lenlock);
} // end VBdestroy

// get a reference to the next 'write' item.
VideoFrame *VBgetAddItem(VBuffer *buf)
{
    VideoFrame *f;
    int head = (buf->tail + buf->len) % buf->bufsize;
    f = buf->buffer + head;
    
    // CMutLock(buf->lenlock);
    buf->len++;
    // CMutUnlock(buf->lenlock);
    return f;
} // end VBgetAddItem

// get a reference to the next 'read' item without removing it
VideoFrame *VBpeak(VBuffer *buf)
{
	if(buf->len <= 0)
		return NULL;
	return buf->buffer + buf->tail;
} // end VBpeak

// get a reference to the next 'read' item while also removing it
VideoFrame *VBgetRemoveItem(VBuffer *buf)
{
    VideoFrame *f;
    if(buf->len <= 0)
		return NULL;
		
    f = buf->buffer + buf->tail;
    buf->tail = (buf->tail + 1) % buf->bufsize;
    // CMutLock(buf->lenlock);
    buf->len--;
    // CMutUnlock(buf->lenlock);
    return f;
} // end VBgetRemoveItem

// how much space left on the buffer?
int VBroom(VBuffer *buf)
{
    return buf->bufsize - buf->len;
} // end VBroom
