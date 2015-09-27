/**
 * TheoraPlay; multithreaded Ogg Theora/Ogg Vorbis decoding.
 *
 * Please see the file LICENSE.txt in the source's root directory.
 *
 *  This file written by Ryan C. Gordon.
 */

/*

Buffers:
> audio buffer is a circular array of pcm float samples. One such array for each channel.
> video buffer is a circular array of pointers to pre-allocated video frames
    - each frame has space for the output video of one video frame
    - memory must be initialized when video decoding is initialized, to match output w, h, colorspace

Functions
> fillBuffers()
    - reads ogg data to decode audio/video as necessary until one of the video/audio buffers is full
    - as video is read, it is converted into the desired output format as it is put into the buffer
> video = getVideo(*video, etc)
    - gets a video frame from the buffer
    - removes it from the video buffer.
    - mediadecoder owns the data. will be valid until fillBuffers is called.
> getNextVideoTime()
    - gets the time of the next ith video frame
> amnt = getBufferedSamples()
    - returns the number of buffered samples on the buffer
> amnt = getAudio(**data, n_samp)
    - get audio from the audio buffers
    - up to n_samp # of samples
    - samples are copied into data
> time = getNextAudioTime()
    - gets the time of the head audio data
    - tracked as audio is added to the buffer, according to the audio format
*/

/*

Structure:
- mediadecoder: above
- Media
    > external controls: play, stop, pause
    > timer
    > uses this file to fill buffers, get video frames, get audio
    > SDL callback points to the media file, which gets its audio from here
        - Media gets audio in pcm float format, adjusts volume, and sends the results in pcm float format to the mixer
        - mixer converts and mixes the audio in the output format

*/

// took variable names from theoraplay

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
    
    // video buffer
    
} MediaDecoder;

typedef struct VideoFrame{
    // timestamp
    // pixel data pointer
} VideoFrame;

// Circular Buffer Code
// TODO //

int readMediaData(MediaDecoder *md)
{
    char *buf; int readlen;
    // get a pointer to the buffer from the sync stream
    if(ogg_sync_buffer(md->sync, 4096) == NULL) return 1;
    
    // read file data into the buffer
    readlen = fread(buf, sizeof(char), 4096, md->file);
    
    // indicate to the sync stream how much was read
    if(ogg_sync_wrote(md->sync, readlen) != 0 || readlen == 0) return 1;
    
    // TODO what to do if an error occured?
}

int readOggPage(MediaDecoder *md, ogg_page *page)
{
    while(ogg_sync_pageout(md->sync, page) != 1)
    {
        if(readMediaData(md) != 0) return 1;
    }
    return 0;
}

// load a file by filename. Could do by file IO object for more flexibility?
void init(MediaDecoder *md, const char *filename, int abufsize)
{
    md->has_audio = 0;
    md->has_video = 0;

    // initialize buffers (step 1)

    // open file
    md->file = fopen(filename, "rb");
    
    // temporary state
    vorbis_comment vcomment;
    th_comment tcomment;
    th_setup_info *tsetup;
    
    // prep decoders
    ogg_sync_init(&md->sync);
    vorbis_info_init(&md->vinfo);
    th_info_init(&md->tinfo);
    
    vorbis_comment_init(&vcomment);
    th_comment_init(&tcomment);
    
    ogg_page hpage;
    ogg_packet hpacket;
    
    int vcount = 0;
    int tcount = 0;
    
    // create streams and look for headers
    int headers_done = 0;
    while( readOggPage(md, &hpage) == 0 && !headers_done)
    {
        int vdec_res, tdec_res;
        
        if( ogg_page_bos(&hpage) ) // create a new stream. I assume the page has at least 1 packet (it should)
        {   
            ogg_stream_init(&new_stream, ogg_page_serialno(&hpage));
            ogg_stream_pagein(&new_stream, &hpage);
            ogg_stream_packetout(&new_stream, &hpacket);
            
            if ( vcount == 0 && vorbis_synthesis_headerin(&md->vinfo, &vcomment, &hpacket) == 0 )
            {
                // copy the stream
                md->vstream = new_stream;
                md->has_audio = 1;
                vcount++;
            }
            else if ( tcount == 0 && th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket) == 0 )
            {
                // copy the stream
                md->tstream = new_stream;
                md->has_video = 1;
                tcount++;
            }
            else
            {
                // delete the stream: we don't support other stream types
                ogg_stream_clear(&new_stream);
            }
        }
        else if( vcount > 0 && ogg_page_serialno(&hpage) == md->vstream.serialno )
        {
            ogg_stream_pagein(md->vstream, &hpage);
            if(ogg_stream_packetout(md->vstream, &hpacket) == 1)
            {
                int res = vorbis_synthesis_headerin(&md->vinfo, &vcomment, &hpacket);
                if( res > 0 ) // is a header
                {
                    vcount++;
                }
                else if( res == 0 ) // is the first data packet
                {
                    headers_done = 1;
                }
            }
        }
        else if( tcount > 0 && ogg_page_serialno(&hpage) == md->tstream.serialno )
        {
            ogg_stream_pagein(md->tstream, &hpage);
            if(ogg_stream_packetout(md->tstream, &hpacket) == 1)
            {
                int res = th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket);
                if( res > 0 ) // is a header
                {
                    tcount++;
                }
                else if( res == 0 )// is the first data packet
                {
                    // maybe it's not a header. What should we do with the packet?
                    headers_done = 1;
                }
            }
        }
    }
    
    // we have our first data packet, but our decoders are not initialized
    if(md->has_audio)
        printf("Read a total of %d vorbis headers\n", vcount);
    if(md->has_video)
        printf("Read a total of %d theora headers\n", tcount);
    
    if( md->has_audio ){
        if( vorbis_synthesis_init(&md->vdsp, &md->vinfo) != 0)   md->has_audio = 0;
        else if( vorbis_block_init(&md->vdsp, &md->vblock) != 0) md->has_audio = 0;
        
        if(!md->has_audio)
        {
            printf("Failed to initialize vorbis decoder\n");
            // free the decoder
            // TODO
        }
    }
    
    if( md->has_video ){
        // as per theoraplay, it would be nice to check colorspace, etc and fail here rather than later
        if ((tinfo.frame_width > 99999) || (tinfo.frame_height > 99999))
        {
            printf("Video frames too large!\n");
            md->has_video = 0;
        }
        else if( tinfo.colorspace != TH_CS_ITU_REC_470M ) // TODO what goes here?
        {
            printf("Please use the **** colorspace\n");
        }
        else
        {
            // allocate the decoder
            md->tdec = th_decode_alloc(md->tinfo, &tsetup);
        }
        
        if( !md->has_audio )
        {
            // free the video decoder
            // TODO
        }
        
        // free any codec setup info
        th_setup_free(&setup);
        // Perform any additional decoder configuration with th_decode_ctl().
        // Do I need this?
    }
    
    // lastly, we have a packet to handle
    if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        do_vpacket(md, hpacket);
    
    if( md->has_video && ogg_page_serialno(&hpage) == md->tstream.serialno )
        do_tpacket(md, tpacket);
    
    // TODO what needs to be cleaned up here?
    th_comment_clear(&tcomment);
    vorbis_comment_clear(&vcomment);
}

void fillBuffers(MediaDecoder md)
{
    ogg_page page;
    ogg_packet packet;
    
    // process more of the file, filling the buffers
    while( readOggPage(md, &page) == 0 && 1/* no used buffer is full */ )
    {
        // is it an audio page?
        if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        {
            ogg_stream_pagein(md->vstream, &page);
            if(ogg_stream_packetout(md->vstream, &packet) == 1)
                do_vpacket(md, hpacket);
        }
        // is it a video page?
        if( md->has_video && ogg_page_serialno(&page) == md->tstream.serialno )
        {
            ogg_stream_pagein(md->tstream, &page);
            if(ogg_stream_packetout(md->tstream, &packet) == 1)
                do_tpacket(md, packet);
        }
    }
}

VideoFrame *getVideo()
{
    // get the next video frame from the queue, or NULL if none.
}

int getNextVideoTime()
{
    // get the timestamp of the next video frame on the queue, or -1 if none
}

int getABufSize()
{
    // return the number of samples in the audio buffer
}

int getAudio(void **data, n_samp)
{
    // get n_samp samples of audio data and store it in data. Return the actual number of samples returned
}

int getNextAudioTime()
{
    // get the timestamp associated with the end of the last audio returned from the buffer (ie of the next audio data)
}

// Cleanup Functions
void close()
{
    fclose(md.file);
    // TODO cleanup
}
