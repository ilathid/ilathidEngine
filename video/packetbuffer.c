#include "packetbuffer.h"

/** Initialize the buffer
 */
void init_pb(PacketBuffer *pb){
    int i;
    pb->r_i = 0;
    pb->size = 0;
    pb->maxSize = 600;
    // I depend on empty packets having 0 pts
    for(i = 0; i < pb->maxSize; i++){
        pb->packets[i].dts = -1;
        }
    }

/** How many items are on the buffer?
 */
int getSize_pb(PacketBuffer *pb){
    return pb->size;
    }

/** How many more items can the buffer hold?
 */
int getLeft_pb(PacketBuffer *pb){
    return pb->maxSize - pb->size;
    }

/** Get a reference to the oldest packet on the buffer. See also getRead
 */
AVPacket *bottom_pb(PacketBuffer *pb){
    // return the oldest packet on the buffer
    // Note: If you pull packets off the buffer, free them before writing more.
    AVPacket *ret;
    if (pb->size > 0)
        ret = &pb->packets[pb->r_i];
    else
        printf("ERROR: bottom: Buffer Empty!\n");
    return ret;
    }

/** Get a reference to the oldest packet on the buffer, and remove that packet from
 *  the buffer.
 *  Note: warning, you need to be done with the packet before you write to the
 *        packet buffer again, since it may write over it.
 */
AVPacket *getRead_pb(PacketBuffer *pb){
    // return the oldest packet on the buffer
    // Note: If you pull packets off the buffer, free them before writing more.
    AVPacket *ret;
    if (pb->size > 0)
        ret = &pb->packets[pb->r_i];
    else{
        printf("ERROR: bottom: Buffer Empty!\n");
        return NULL;
        }
    // printf("Read packet %u:: %d", &pb->packets[pb->r_i], pb->r_i);
    // printf("Read %d\n", pb->r_i);
    pb->r_i = (pb->r_i + 1) % pb->maxSize;
    pb->size --;
    return ret;
    }


/** Get the smallest pts timestamp on the buffer.
 *  An assumption is made here that the smallest pts is on one of the oldest
 *  4 packets on the buffer.
 */
int nextPts_pb(PacketBuffer *pb){
    // Return the newest packet on the buffer
    int pts = -1;
    int temp = 16;
    int i;
    int ind;
    if (pb->size > 0){
        if (pb->size < 16) temp = pb->size;
        ind = (pb->r_i) % pb->maxSize;
        i = (ind + temp) % pb->maxSize; 
        if(pb->packets[ind].dts >= 0)
            pts = pb->packets[ind].dts;
        //printf(".%d", pb->packets[ind].dts);
        for (ind ++; ind != i; ind = (ind + 1) % pb->maxSize){
            temp = pb->packets[ind].dts;
            if (temp >= 0 && (pts == -1 || temp < pts)) pts = temp;
            //printf(".%d", pb->packets[ind].dts);
            }    
        }
    else{
        //printf("ERROR: top: Buffer Empty!\n");
        }
    // printf("-> pts %d\n", pts);
    return pts;
    }

/** Get a reference to the newest (most recently added) packet on the buffer.
 *  I don't have the impression this function is useful.
 */
AVPacket *top_pb(PacketBuffer *pb){
    // Return the newest packet on the buffer
    AVPacket *ret;
    int ind;
    if (pb->size > 0){
        ind = (pb->r_i + pb->size - 1) % pb->maxSize;
        ret = &pb->packets[ind];
        }
    else{
        printf("ERROR: top: Buffer Empty!\n");
        }
    return ret;
    }

/** Get a reference to the next (ie 'a new') packet on the buffer, and add that packet to the buffer.
 */
AVPacket *getWrite_pb(PacketBuffer *pb){
    // Get a pointer to the next available packet, and increment the buffer
    int ind;
    AVPacket *ret;
    ind = (pb->r_i + pb->size) % pb->maxSize;
    // Is the buffer full already?
    if (pb->size == 0 || ind != pb->r_i){
        pb->size += 1;
        ret = &pb->packets[ind];
        //printf("write %d\n", ind);
        }
    else{
        printf("ERROR: write: Buffer Full!\n");
        }
    return ret;
    }

/** Clear all packets, freeing memory and resetting pts timestamps.
 */
void clear_pb(PacketBuffer *pb){
    // Free all the allocated packets        
    int ind;
    //printf("Clear\n");
    //printf("size: %d\n", pb->size);
    for(ind = 0; ind < pb->size; ind++){
        av_free_packet(&pb->packets[(pb->r_i + ind) % pb->maxSize]);
        pb->packets[(pb->r_i + ind) % pb->maxSize].dts = -1;
        }
    pb->size = 0;
    pb->r_i = 0;
    }
