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

static void _dovpacket(MediaDecoder *md, ogg_packet packet);
static void _dotpacket(MediaDecoder *md, ogg_packet packet);

// took variable names from theoraplay

int _readMediaData(MediaDecoder *md)
{
    char *buf; int readlen;
    // get a pointer to the buffer from the sync stream
    if(ogg_sync_buffer(&md->sync, 4096) == NULL) return 1;
    
    // read file data into the buffer
    readlen = fread(buf, sizeof(char), 4096, md->file);
    
    // indicate to the sync stream how much was read
    if(ogg_sync_wrote(&md->sync, readlen) != 0 || readlen == 0) return 1;
    
    // TODO what to do if an error occured?
    return 0;
}

int _readOggPage(MediaDecoder *md, ogg_page *page)
{
    while(ogg_sync_pageout(&md->sync, page) != 1)
    {
        if(_readMediaData(md) != 0) return 1;
    }
    return 0;
}

// load a file by filename. Could do by file IO object for more flexibility?
// abufsize is number of samples in the audio buffer.
// actual buffer will be 4*channelnum*abufsize, for 32-bit pcm format
void md_init(MediaDecoder *md, const char *filename, int abufsize)
{
    md->has_audio = 0;
    md->has_video = 0;
    
    // open file
    md->filename = filename;
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
    
    // init state variables
    tsetup = NULL;
    md->tdec = NULL;
    
    ogg_page hpage;
    ogg_packet hpacket;
    
    int vcount = 0;
    int tcount = 0;
    
    // create streams and look for headers
    int headers_done = 0;
    while( _readOggPage(md, &hpage) == 0 && !headers_done)
    {
        int vdec_res, tdec_res;
        
        if( ogg_page_bos(&hpage) ) // create a new stream. I assume the page has at least 1 whole packet (it should)
        {   
			ogg_stream_state new_stream;
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
            ogg_stream_pagein(&md->vstream, &hpage);
            if(ogg_stream_packetout(&md->vstream, &hpacket) == 1)
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
            ogg_stream_pagein(&md->tstream, &hpage);
            if(ogg_stream_packetout(&md->tstream, &hpacket) == 1)
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
        if( vorbis_synthesis_init(&md->vdsp, &md->vinfo) == 0)
			vorbis_block_init(&md->vdsp, &md->vblock);
		else
		{
			printf("vorbis synthesis init error\n");
			// free any codec setup info
			ogg_stream_clear(&md->vstream);
			th_setup_free(tsetup);
			md->has_audio = 0;
		}	
    }
    
    if( md->has_video ){
        // as per theoraplay, it would be nice to check colorspace, etc and fail here rather than later
        if ((md->tinfo.frame_width > 99999) || (md->tinfo.frame_height > 99999))
        {
            printf("Video frames too large!\n");
        }
        else if( md->tinfo.colorspace != TH_CS_ITU_REC_470M ) // TODO what goes here?
        {
            printf("Used the %d colorsapce\n", md->tinfo.colorspace);
            printf("Please use the %d colorspace\n", TH_CS_ITU_REC_470M);
        }
        else // allocate the decoder
            md->tdec = th_decode_alloc(&md->tinfo, tsetup);
        
        if( md->tdec == NULL )
        {
			// free any codec setup info
			ogg_stream_clear(&md->tstream);
			th_setup_free(tsetup);
			md->has_video = 0;
		}
        
        // Perform any additional decoder configuration with th_decode_ctl().
        // Do I need this?
        // post-processing level can be adjusted
    }

	// Initialize the buffers
    if( md->has_audio ){
        // A sample (is) a chunk of audio data of the size specified in format mulitplied by the number of channels - sdlaudiospec.html       
        
        // bps = bytes per samples
        md->bps = sizeof(float)*md->vinfo.channels;
        // convert number of samples to size in bytes
        md->abufsize = abufsize*md->bps;
		md->aBuffer = (char *)malloc(sizeof(char)*(abufsize));
		md->abuflen = 0;
        md->acnt = 0;
        MptMutCreate(md->ablenmut);
    }
    
    if( md->has_video ){
        // how many video frames?
        // its possible this is not encoded in the video. Should I just enforce that it is?
        if(md->tinfo.fps_denominator == 0)
        {
            printf("Warning: no fps information encoded in the file %s\n", filename);
            ogg_stream_clear(&md->tstream);
			th_setup_free(tsetup);
			md->has_video = 0;
        }
        else
        {
			// set up the video buffer
			// buftime = abufsize/md->vinfo.rate, vidframes = buftime * fps
			int vbuflen = 0;
			if(md->has_audio)
				vbuflen = (md->abufsize * md->tinfo.fps_numerator - 1) / (md->tinfo.fps_denominator * md->vinfo.rate) + 1;
			vbuflen = max(vbuflen, 4); // have at least 4 video frames in the buffer
			// theoraplay suggests pixels are 8-bit pixels in YUV, with UV at 1/2 density
			md->bpf = md->tinfo.pic_width * md->tinfo.pic_height * 2;
			// the following is very confusing. Sorry about that...
			VBinit(&md->vBuffer, vbuflen); // initialize pointers array
			md->vcnt = 0;
		}
    }
    
    // lastly, we have a packet to handle
    if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        _dovpacket(md, hpacket);
    else if( md->has_video && ogg_page_serialno(&hpage) == md->tstream.serialno )
        _dotpacket(md, hpacket);
    // The following I believe is not necessary since the decoder should free the packet internally
    // else
	// 	ogg_packet_clear(hpacket);
    
    // clear the structures that should only survive for as long as the init function
    th_comment_clear(&tcomment);
    vorbis_comment_clear(&vcomment);
}

void md_reset(MediaDecoder *md, int clear_buffers)
{
	// todo: find out how to reset the decoder state, as if we are about to seek
	// reset file position to the beginning. We will end up reading headers again: is this ok?
	
	// cheat for now
	md_close(md);
	md_init(md, md->filename, md->abufsize/md->bps);
}

int md_fillBuffers(MediaDecoder *md)
{
    ogg_page page;
    ogg_packet packet;
    
    int res;
    
    // process more of the file as long as all used buffers have room
    while( (res = _readOggPage(md, &page)) == 0
         && (!md->has_audio || md->abufsize - md->abuflen > md->abufsize/4)
         && (!md->has_video || VBroom(&md->vBuffer) > 0))
    {
        // is it an audio page?
        if( md->has_audio && ogg_page_serialno(&page) == md->vstream.serialno )
        {
            ogg_stream_pagein(&md->vstream, &page);
            if(ogg_stream_packetout(&md->vstream, &packet) == 1)
                _dovpacket(md, packet);
        }
        // is it a video page?
        if( md->has_video && ogg_page_serialno(&page) == md->tstream.serialno )
        {
            ogg_stream_pagein(&md->tstream, &page);
            if(ogg_stream_packetout(&md->tstream, &packet) == 1)
                _dotpacket(md, packet);
        }
    }
    
    // if there was a file-read error or we reached the end of the file, this will return 1
    return res;
}

// taken from theoraplay.c
void _VideoClip(th_ycbcr_buffer ycbcr, char *pixels, th_info *tinfo)
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

} // end _VideoClip

static void _dotpacket(MediaDecoder *md, ogg_packet packet)
{
	VideoFrame *frm;
    th_ycbcr_buffer ycbcr;
    int k;
    
    if(VBroom(&md->vBuffer) <= 0)
		return;
    
    // decode the video page packet
    // if there is a problem, or eg this is a header, we don't do anything more with it
    if(th_decode_packetin(md->tdec, &packet, NULL))
		return;
	
	th_decode_ycbcr_out(md->tdec, ycbcr);
    
    frm = VBgetAddItem(&md->vBuffer);
    
    // copy ycbcr data into frm->pixels with clipping
    _VideoClip(ycbcr, frm->pixels, &md->tinfo);
    
    // set the associated audio sample for this video frame
    // current audio sample = processed samples + samples on buffer
    frm->async = md_getNextSampleNum(md);
    // if there is no audio, return video time in milliseconds according to framerate information
    if(frm->async == -1) frm->async = (1000*md->vcnt * md->tinfo.fps_denominator) / md->tinfo.fps_numerator;
    md->vcnt++;
    // that's it, the video frame is already added
}

// TODO the following has issues
static void _dovpacket(MediaDecoder *md, ogg_packet packet)
{
    // pass the packet data into the decoder and get a vorbis block
    int channels,samples,k,j;
    float **pcm;
    float *buf;
	
	// if there is a problem eg this is a header, we don't do anything more with it
    if(vorbis_synthesis(&md->vblock, &packet))
		return;
	
	if(vorbis_synthesis_blockin(&md->vdsp, &md->vblock))
		return;
	
    // get pcm audio data
    samples = vorbis_synthesis_pcmout(&md->vdsp, &pcm);
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
	MptMutUnlock(md->ablenmut);
	
	// count samples decoded onto the buffer
	md->acnt += samples;
	
	// tell the decoder how much data we used
	vorbis_synthesis_read(&md->vdsp, samples);
}

//////////////////////////////////////
// Video and Audio Access Functions //
//////////////////////////////////////

// get the last video frame whose play time is before asample
// return NULL if there is none
VideoFrame *md_getVideo(MediaDecoder *md, int asample)
{
	VideoFrame *frm,*nxt;
	
	if(md->vBuffer.len <= 0)
		return NULL;
	
	frm = VBgetRemoveItem(&md->vBuffer);
	if(md->vBuffer.len <= 0)
		return frm;
		
	// get the first frame such that the following frame comes after asample
	// if we run out of frames, use the last frame from the stack, so that
	// there is at least some video playing as the player tries to catch up
	nxt = VBpeak(&md->vBuffer);
	while(md->vBuffer.len > 0 && nxt->async < asample)
	{
		frm = VBgetRemoveItem(&md->vBuffer);
		nxt = VBpeak(&md->vBuffer);
	}
	return frm;
}

int md_getNextVideoSync(MediaDecoder *md)
{
	VideoFrame *frm;
	frm = VBpeak(&md->vBuffer);
	return frm->async;
}

// get number of samples decoded - # of samples of the buffer
// ie this is one less than the sample number of the first sample on the buffer
int md_getNextSampleNum(MediaDecoder *md)
{
	if(md->has_audio)
		return md->acnt - (md->abufsize - md->abuflen)/md->bps;
	return -1;
}

// len is the number length of the data stream, which are floats
// len will be num_samples * num_channels
// we return a length of data which is a multiple of num_channels so that length <= len
int md_getAudio(MediaDecoder *md, float *data, int len)
{
	int buflen, k;
    // samples exist from k=0 to k=len
    // once we are done getting samples, we need to move remaining samples to the front
    
    // ensure quested data divides the number of channels
    len = len - (len % md->vinfo.channels);
    
    // if samples is less than len, get the samples, move remainder over
    // if samples is larger than or equal to len, just get len samples
    
    MptMutLock( md->ablenmut );
    buflen = md->abuflen / sizeof(float); // how many samples are in the buffer?
    
    if( len > buflen )
		len = buflen;
	
	// read the samples
	for( k=0;k<len;k++ )
		data[k] = md->aBuffer[k];
	
	// move remaining data to the front of the buffer
	for( k=len;k<buflen;k++ )
		md->aBuffer[k-len] = md->aBuffer[k];
    md->abuflen = (buflen - len) * sizeof(float);
    
    MptMutUnlock(md->ablenmut);
    
    return len;
}

int md_getAudioTime(MediaDecoder *md)
{
	return (1000*(md->abufsize - md->abuflen))/(md->bps * md->vinfo.rate);
}

/*
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
*/

int md_skipAudio(MediaDecoder *md, int samples)
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
void md_close(MediaDecoder *md)
{
    fclose(md->file);
    
    th_info_clear(&md->tinfo);
	vorbis_info_clear(&md->vinfo);
	
    if(md->has_audio)
    {
		ogg_stream_clear(&md->tstream);
		vorbis_block_clear(&md->vblock);
		vorbis_dsp_clear(&md->vdsp);
		free(md->aBuffer);
	}
	if(md->has_video)
    {
		ogg_stream_clear(&md->vstream);
		VBdestroy(&md->vBuffer);
	}
}
