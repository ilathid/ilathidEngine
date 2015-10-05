#include "MediaDecoder.h"

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
> samples = getAudio(**data, n_samp)
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

int _readMediaData(MediaDecoder *md)
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

int _readOggPage(MediaDecoder *md, ogg_page *page)
{
    while(ogg_sync_pageout(md->sync, page) != 1)
    {
        if(readMediaData(md) != 0) return 1;
    }
    return 0;
}

// load a file by filename. Could do by file IO object for more flexibility?
// abufsize is number of samples in the audio buffer.
// actual buffer will be 4*channelnum*abufsize, for 32-bit pcm format
int MDinit(MediaDecoder *md, const char *filename, int abufsize)
{
    md->has_audio = 0;
    md->has_video = 0;
    
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
        
        if( ogg_page_bos(&hpage) ) // create a new stream. I assume the page has at least 1 whole packet (it should)
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
                    vcount++;
                else if( res == 0 ) // is the first data packet
                    headers_done = 1;
            }
        }
        else if( tcount > 0 && ogg_page_serialno(&hpage) == md->tstream.serialno )
        {
            ogg_stream_pagein(md->tstream, &hpage);
            if(ogg_stream_packetout(md->tstream, &hpacket) == 1)
            {
                int res = th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket);
                if( res > 0 ) // is a header
                    tcount++;
                else if( res == 0 )// is the first data packet
                    headers_done = 1;
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
            printf("Used the %d colorsapce\n", tinfo.colorspace);
            printf("Please use the %d colorspace\n", TH_CS_ITU_REC_470M);
        }
        else // allocate the decoder
            md->tdec = th_decode_alloc(md->tinfo, &tsetup);
        
        if( !md->has_audio )
        {
            // free the audio decoder
            // TODO
        }
        // free any codec setup info
        th_setup_free(&setup);
        // Perform any additional decoder configuration with th_decode_ctl().
        // Do I need this?
    }

	// Initialize the buffers
    if( md->has_audio ){
        // A sample (is) a chunk of audio data of the size specified in format mulitplied by the number of channels - sdlaudiospec.html       
        
        // bps = bytes per samples
        md->bps = sizeof(float)*vinfo.channels;
		md->aBuffer = (char *)malloc(sizeof(char)*(abufsize*md->bps));
		md->abufsize = abufsize;
		md->abuflen = 0;
        md->samplecnt = 0;
        MptMutCreate(md->ablenmut);
    }
    
    if( md->has_video ){
        // how many video frames?
        // its possible this is not encoded in the video. Should I just enforce that it is?
        if(md->tinfo.fps_denominator == 0)
        {
            printf("Warning: no fps information encoded in the file %s\n", filename);
            exit(1);
        }
        // buftime = abufsize/vinfo.rate
        // vidframes = buftime * fps
        int vbuflen = (abufsize * md->tinfo.fps_numerator - 1) / (md->tinfo.fps_denominator * md->vinfo.rate) + 1;
        vbuflen = max(vbuflen, 4); // have at least 4 video frames in the buffer
        // theoraplay suggests pixels are 8-bit pixels in YUV, with UV at 1/2 density
        md->bpf = w * h * 2;
        // the following is very confusing. Sorry about that...
        VBinit(md->vBuffer, vbuflen, md->bpf); // initialize pointers array
    }
    
    // lastly, we have a packet to handle
    if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        dovpacket(md, hpacket);
    
    if( md->has_video && ogg_page_serialno(&hpage) == md->tstream.serialno )
        dotpacket(md, tpacket);
    
    // TODO what needs to be cleaned up here?
    th_comment_clear(&tcomment);
    vorbis_comment_clear(&vcomment);
}

void md_fillBuffers(MediaDecoder md)
{
    ogg_page page;
    ogg_packet packet;
    
    // process more of the file as long as all used buffers have room
    while( readOggPage(md, &page) == 0
         && (!md->has_audio || md->abufsize - md->abuflen > (abufsize*md->bps)/4)
         && (!md->has_video || VBroom(md->vBuffer) > 0))
    {
        // is it an audio page?
        if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        {
            ogg_stream_pagein(md->vstream, &page);
            if(ogg_stream_packetout(md->vstream, &packet) == 1)
                dovpacket(md, packet);
        }
        // is it a video page?
        if( md->has_video && ogg_page_serialno(&page) == md->tstream.serialno )
        {
            ogg_stream_pagein(md->tstream, &page);
            if(ogg_stream_packetout(md->tstream, &packet) == 1)
                dotpacket(md, packet);
        }
    }
}

// taken from theoraplay.c
void VideoClip(th_ycbcr_buffer ycbcr, unsigned char *pixels, th_info *tinfo)
{
    int i;
    int w = tinfo->pic_width;
    int h = tinfo->pic_height;
    int yoff = (tinfo->pic_x & ~1) + ycbcr[0].stride * (tinfo->pic_y & ~1);
    int uvoff = (tinfo->pic_x / 2) + (ycbcr[1].stride) * (tinfo->pic_y / 2);
    
	for (i = 0; i < h; i++, pixels += w)
		memcpy(pixels, ycbcr[0].data + yoff + ycbcr[0].stride * i, w);
	for (i = 0; i < (h / 2); i++, pixels += w/2)
		memcpy(pixels, ycbcr[1].data + uvoff + ycbcr[1].stride * i, w / 2);
	for (i = 0; i < (h / 2); i++, pixels += w/2)
		memcpy(pixels, ycbcr[2].data + uvoff + ycbcr[2].stride * i, w / 2);

} // end VideoClip

void dotpacket(MediaDecoder md, ogg_packet packet)
{
	VideoFrame *frm;
    th_ycbcr_buffer ycbcr
    int k;
    
    if(VBroom(md->vBuffer) <= 0)
		return;
    
    // decode the video page packet
    if(th_decode_packetin(md->tdec, &packet, NULL))
		return;
	
	th_decode_ycbcr_out(md->tdec, ycbcr);
    
    frm = VBgetAddItem(md->vBuffer);
    
    // copy ycbcr data into frm->pixels with clipping
    VideoClip(ycbcr, frm->pixels);
    
    // set the associated audio sample for this video frame
    // current audio sample = processed samples + samples on buffer
    frm->async = getNextSampleNum(md);
    // that's it, the video frame is already added
}

// TODO the following has issues
void dovpacket(MediaDecoder md, ogg_packet packet)
{
    // pass the packet data into the decoder and get a vorbis block
    int channels,samples,k,j;
    float **pcm;
    float *buf;

    if(vorbis_synthesis(&md->vblock, &packet))
		return;
	
	if(vorbis_synthesis_blockin(md->vdsp, &md->vblock))
		return;
	
    // get pcm audio data
    samples = vorbis_synthesis_pcmout(md->vdsp, &pcm);
	// pcm[channel][sample], sample = 0 .. samples-1
    
    MptMutLock(md->ablenmut);
    // reduce samples number if there isn't room
    samples = min(samples, (md->abufsize - md->abuflen)/md->bps);
	if(samples > 0)
	{
		// interlace the audio data and put it on the end of the buffer
		channels = md->vinfo.channels;
		buf = (float *)(md->aBuffer + md->abuflen);
		for(k=0;k<channels;k++)
			for(j=0;j<samples;j++)
				buf[ j*channels + k ] = pcm[k][j];
		md->abuflen += samples*md->bps;
	}
	MptMutUnLock(md->ablenmut);
	
	// tell the decoder how much data we used
	vorbis_synthesis_read(md->vdsp, samples);
}

//////////////////////////////////////
// Video and Audio Access Functions //
//////////////////////////////////////

// TODO the following

// get the last video frame whose play time is before asample
// return NULL if there is none
VideoFrame *getVideo(int asample)
{
	VideoFrame *frm,*nxt;
	
	if(md->vBuffer.len <= 0)
		return NULL;
	
	frm = VBgetRemoveItem(md->vBuffer);
	if(md->vBuffer.len <= 0)
		return frm;
		
	// get the first frame such that the following frame comes after asample
	// if we run out of frames, use the last frame from the stack, so that
	// there is at least some video playing as the player tries to catch up
	nxt = VBpeak(md->vBuffer);
	while(md->vBuffer.len > 0 && nxt->async < asample)
	{
		frm = VBgetRemoveItem(md->vBuffer);
		nxt = VBpeak(md->vBuffer);
	}
	return frm;
}

int getNextSampleNum(MediaDecoder md)
{
	return md->acnt + (md->abufsize - md->abuflen)/md->bps;
}

int getAudio(unsigned char *data, int len)
{
	int samples,bufsamples;
	Sint16 *dst = (Sint16 *)data;
    // samples exist from k=0 to k=len
    // once we are done getting samples, we need to move remaining samples to the front
    
    // if samples is less than len, get the samples, move remainder over
    // if samples is larger than or equal to len, just get len samples
    
    MptMutLock(md->ablenmut);
    samples = len / (sizeof(Sint16) * md->vinfo.channels);
    bufsamples = md->abuflen / md->bps;
    
    if( samples > bufsamples)
		samples = bufsamples;
	
	for( k=0;k<samples;k++ )
	{
		if( md->aBuffer[k] >= 1.0f )
			dst[k] = 32767;
		else if( md->aBuffer[k] <= -1.0f )
			dst[k] = -32768;
		else
			dst[k] = md->aBuffer[k] * 32767.0f;
	}
	
	// move remaining data to the front of the buffer
	for( k=samples;k<bufsamples;k++ )
		md->aBuffer[k-samples] = md->aBuffer[k];
    md->abuflen = (bufsamples - samples) * md->bps;
    
    MptMutUnlock(md->ablenmut);
    
    return samples * (sizeof(Sint16) * md->vinfo.channels) ;
}

int skipAudio(int samples)
{
	int k,bufsamples;
	
    MptMutLock(md->ablenmut);
    bufsamples = md->abuflen / md->bps;
    if( samples > bufsamples)
		samples = bufsamples;
    // move remaining data to the front of the buffer
	for( k=samples;k<bufsamples;k++ )
		md->aBuffer[k-samples] = md->aBuffer[k];
	md->abuflen = (bufsamples - samples) * md->bps;
		
	MptMutUnlock(md->ablenmut);
    
    return samples;
}

// Cleanup Functions
void close()
{
    fclose(md.file);
    // TODO cleanup
}
