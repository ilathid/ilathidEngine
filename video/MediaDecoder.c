#include "MediaDecoder.h"

static int _dovpacket(MediaDecoder *md, ogg_packet *packet);
static void _dotpacket(MediaDecoder *md, ogg_packet *packet);

// took many variable names from theoraplay

int _readMediaData(MediaDecoder *md)
{
    char *buf; int readlen;
    
    // get a pointer to the buffer from the sync stream
    // printf("getting a sync buffer\n");
    buf = ogg_sync_buffer(&md->sync, 4096);
    
    // read file data into the buffer
    // printf("reading from the file\n");
    readlen = fread(buf, sizeof(char), 4096, md->file);
    
    // indicate to the sync stream how much was read
    // printf("indicating buffer is ready\n");
    if(ogg_sync_wrote(&md->sync, readlen) != 0 || readlen == 0)
        return 1; // failed
        
    // if(readlen < 4069) printf("missed data?\n");
    
    // success
    return 0;
}

// return 1 if we can't read a page (eos or error)
int _readOggPage(MediaDecoder *md, ogg_page *page)
{
    int res;
    //printf("  getting a page\n");
    while((res = ogg_sync_pageout(&md->sync, page)) != 1)
    {
        // if(res == 0) printf("more data needed\n");
        if(res == -1) printf("bytes were skipped!\n");
        if(_readMediaData(md) != 0)
        {
            printf("Couldn't read data!\n");
            return 1;
        }
        // printf("got more data: trying to pull a page again\n");
    }
    // printf("Got a page\n");
    return 0;
}

static int _abuf_dlen(MediaDecoder *md)
{
    // This is a length measure that is safe for WRITERS (ie len may decrease in the future)
    if( md->abuffull ) return md->abufsize;
    return (md->abufhead + md->abufsize - md->abuftail) % md->abufsize;
}

// load a file by filename.
// abufsize is an indicator of needed buffer size.
// if the file has video, it will seek to correspond sizes according to video fps and audio sample rate
void md_init(MediaDecoder *md, const char *filename, int abufsize, int vbufsize)
{
    // temporary state
    vorbis_comment vcomment;
    th_comment tcomment;
    th_setup_info *tsetup;
 
    ogg_page hpage;
    ogg_packet hpacket;
 
    md->has_audio = 0;
    md->has_video = 0;
    
    // open file. It will remain open until md_close is called
    md->filename = filename;
    md->file = fopen(filename, "rb");
    if(md->file == NULL) printf("failed to open %s\n", filename);
    else printf("Opened %s\n", filename);
    
    // prep decoders
    ogg_sync_init(&md->sync);
    vorbis_info_init(&md->vinfo);
    th_info_init(&md->tinfo);
    
    vorbis_comment_init(&vcomment);
    th_comment_init(&tcomment);
    
    // init state variables
    tsetup = NULL;
    md->tdec = NULL;
    
    int vcount = 0;
    int tcount = 0;
    
    // create streams and look for headers
    // Todo: this could be simplified if I know each bos page has only 1 packet. It probably does, but need to look up the specs.
    // If not, I should change this anyway to simplify the logic, probably grouping the bos logic with the rest of header packets logic
    int headers_done = 0;
    while( !headers_done && _readOggPage(md, &hpage) == 0 )
    {
        // printf("Read a page\n");
        int vdec_res, tdec_res;
        if( ogg_page_bos(&hpage) ) // create a new stream. I assume the page has at least 1 whole packet (it should)
        {   
            printf("New stream: ");
			ogg_stream_state new_stream;
            ogg_stream_init(&new_stream, ogg_page_serialno(&hpage));
            ogg_stream_pagein(&new_stream, &hpage);
            ogg_stream_packetout(&new_stream, &hpacket); // assume only a single packet in a bos page
            
            if ( vcount == 0 && vorbis_synthesis_headerin(&md->vinfo, &vcomment, &hpacket) == 0 )
            {
                printf("Vorbis\n");
                // copy the stream
                // md->vstream = new_stream;
                memcpy(&md->vstream, &new_stream, sizeof( new_stream ));
                md->has_audio = 1;
                vcount++;
                
                // // try to pull more vorbis packets?
                while(ogg_stream_packetout(&md->vstream, &hpacket) == 1 && !headers_done)
                {
                    int res = vorbis_synthesis_headerin(&md->vinfo, &vcomment, &hpacket);
                    if( res == 0 ) // is a header
                        vcount++;
                    else if( res == OV_ENOTVORBIS ) // is the first data packet
                        headers_done = 1;
                    // else
                    //     printf("Video header packet needs more data?\n");
                }
            }
            else if ( tcount == 0 && th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket) > 0)
            {
                printf("Theora\n");
                // copy the stream
                //md->tstream = new_stream;
                memcpy(&md->tstream, &new_stream, sizeof( new_stream ));
                md->has_video = 1;
                tcount++;
                
                // try to pull some more theora packets?
                while(ogg_stream_packetout(&md->tstream, &hpacket) == 1 && !headers_done)
                {
                    int res = th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket);
                    if( res > 0 ) // is a header
                        tcount++;
                    else if( res == 0 )// is the first data packet
                        headers_done = 1;
                    // else
                    //     printf("Theora header packet needs more data?\n");
                }
            }
            else
            {
                printf("Not recognized (%d)\n", ogg_page_serialno(&hpage));
                // delete the stream: we don't support other stream types
                ogg_stream_clear(&new_stream);
            }
        }
        else if( vcount > 0 && ogg_page_serialno(&hpage) == md->vstream.serialno )
        {
            // printf("new page is a vorbis page\n");
            ogg_stream_pagein(&md->vstream, &hpage);
            while(!headers_done && ogg_stream_packetout(&md->vstream, &hpacket) != 0)
            {
                int res = vorbis_synthesis_headerin(&md->vinfo, &vcomment, &hpacket);
                // printf("res=%d\n", res);
                if( res == 0 )
                    vcount++; // is a header
                else if( res != 0 )
                    headers_done = 1; // is the first data packet
                // else
                //     printf("header in did something funny...\n");
            }
        }
        else if( tcount > 0 && ogg_page_serialno(&hpage) == md->tstream.serialno )
        {
            int res;
            // printf("new page is a theora page\n");
            ogg_stream_pagein(&md->tstream, &hpage);
            while(!headers_done && (res = ogg_stream_packetout(&md->tstream, &hpacket)) != 0)
            {
                int res = th_decode_headerin(&md->tinfo, &tcomment, &tsetup, &hpacket);
                if( res > 0 ) // is a header
                    tcount++;
                else if( res == 0 )// is the first data packet
                    headers_done = 1;
                // else
                //     printf("header in did something funny...\n");
            }
        }
        else
        {
            printf("Got a non-bos that wasn't recognized as a header (%d)\n", ogg_page_serialno(&hpage));
        }
    }
    
    // we have our first data packet, but our decoders are not initialized
    if(md->has_audio)
        printf("Read a total of %d vorbis headers\n", vcount);
    if(md->has_video)
        printf("Read a total of %d theora headers\n", tcount);
    
    if( md->has_audio ){
        // print some comments
        printf("Vorbis Information:\n");
        printf("    version %d\n", md->vinfo.version);
        printf("    channels %d\n", md->vinfo.channels);
        printf("    sample rate %ld\n", md->vinfo.rate);
        
        printf("try initailzing the vorbis decoder: ");
        if( vorbis_synthesis_init(&md->vdsp, &md->vinfo) == 0)
        {
			vorbis_block_init(&md->vdsp, &md->vblock);
            printf("vorbis success\n");
        }
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
        printf("try initailzing the theora decoder: ");
        // as per theoraplay, it would be nice to check colorspace, etc and fail here rather than later
        
        if ((md->tinfo.frame_width > 99999) || (md->tinfo.frame_height > 99999))
        {
            printf("Video frames too large!\n");
        }
        // else if( md->tinfo.colorspace == TH_CS_ITU_REC_470BG ) // TODO what goes here?
        // {
        //     printf("Used the %d colorsapce\n", md->tinfo.colorspace);
        //     printf("Please use the %d colorspace\n", TH_CS_ITU_REC_470M);
        // }
        else // allocate the decoder
            md->tdec = th_decode_alloc(&md->tinfo, tsetup);
        
        if( md->tdec == NULL )
        {
			// free any codec setup info
			ogg_stream_clear(&md->tstream);
			th_setup_free(tsetup);
			md->has_video = 0;
            printf("failed\n");
		}
        
        // Perform any additional decoder configuration with th_decode_ctl().
        // Do I need this?
        // post-processing level can be adjusted
    }

	// Initialize the buffers
    if( md->has_audio ){
        // A sample (is) a chunk of audio data of the size specified in format mulitplied by the number of channels - sdlaudiospec.html       
        printf("initializing audio buffer\n");
        // bps = bytes per samples
        md->bps = sizeof(float)*md->vinfo.channels;
        
        if( md->has_video )
            md->abufsize = max(md->abufsize, (vbufsize * md->tinfo.fps_denominator * md->vinfo.rate) / md->tinfo.fps_numerator);
        
        // convert number of samples to size in bytes
        md->abufsize = abufsize*md->bps;
		md->aBuffer = (char *)malloc(sizeof(char)*(md->abufsize));
        md->abufhead = 0;
        md->abuftail = 0; // empty
        md->abuffull = 0;
        md->acnt = 0;
        md->toskipaudio = 0;
        // printf("md->ablenmut: %llx\n", (unsigned long long)md->ablenmut );
        //printf("Creating Lock\n");
        // md->ablenmut = MptMutCreate();
        // if( md->ablenmut == NULL )
        //     printf("Mutex Creation Failed!\n");
        // printf("md->ablenmut: %llx\n", (unsigned long long)md->ablenmut );
        // printf("md->ablenmut[0]: %d\n", (int)md->ablenmut[0] );
        // printf("Trying Lock\n");
        // MptMutLock( md->ablenmut );
        // MptMutUnlock( md->ablenmut );
        // printf("Lock Worked\n");
    }
    
    if( md->has_video ){
        printf("init videoa\n");
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
			if( md->has_video )
                vbufsize = max(vbufsize, (abufsize * md->tinfo.fps_numerator) / (md->tinfo.fps_denominator * md->vinfo.rate));

			vbufsize = max(vbufsize, 4); // have at least 4 video frames in the buffer
            
			// theoraplay suggests pixels are 8-bit pixels in YUV, with UV at 1/2 density
			md->bpf = md->tinfo.pic_width * md->tinfo.pic_height * 2;
            printf("Frame Rate FPS: %d / %d\n", md->tinfo.fps_numerator, md->tinfo.fps_denominator);
            printf("Creatings a video buffer of length %d, bpf=%d\n", vbufsize, md->bpf);
			VBinit(&md->vBuffer, vbufsize, md->bpf); // initialize pointers array
			md->vcnt = 0;
		}
    }
    
    printf("Initialization Success: has_audio=%d, has_video=%d\n", md->has_audio, md->has_video);
    
    // lastly, we have a packet to handle
    // printf("\nHandle the extra packet\n");
    if( md->has_audio && ogg_page_serialno(&hpage) == md->vstream.serialno )
        _dovpacket(md, &hpacket);
    else if( md->has_video && ogg_page_serialno(&hpage) == md->tstream.serialno )
        _dotpacket(md, &hpacket);
    // The following I believe is not necessary since the decoder should free the packet internally
    // else
	// 	ogg_packet_clear(hpacket);
    
    // clear the structures that should only survive for as long as the init function
    th_comment_clear(&tcomment);
    vorbis_comment_clear(&vcomment);
}

// reset is equivalent to close and re-init the decoder, optionally leaving data on buffers, for looping.
void md_reset(MediaDecoder *md, int clear_buffers)
{
	// todo: find out how to reset the decoder state, as if we are about to seek
	// reset file position to the beginning. We will end up reading headers again: is this ok?
	
	// cheat for now
	// TODO
}

static int _aHasRoom(MediaDecoder *md)
{
    return _abuf_dlen(md) < (7*md->abufsize)/8;
}

static int _vHasRoom(MediaDecoder *md)
{
    return VBroom(&md->vBuffer) > 0;
}

static void _clearAPackets(MediaDecoder *md)
{
    ogg_packet packet;
    while( _aHasRoom(md) && ogg_stream_packetout(&md->vstream, &packet) == 1)
        _dovpacket(md, &packet);
}

static void _clearVPackets(MediaDecoder *md)
{
    ogg_packet packet;
    int res;
    while(_vHasRoom(md) && (res = ogg_stream_packetout(&md->tstream, &packet)) == 1)
    {
        // printf("clearv: res=%d\n", res);
        _dotpacket(md, &packet);
    }
    // printf("Tried to get video: res=%d\n", res);
}

// Read 1 new page into the buffers
int md_incBuffers(MediaDecoder *md)
{
    int res;
    ogg_page page;
    
    // printf("Incrementing Buffers\n");
    
    // clear previously loaded page, if there is room on the buffers
    if(md->has_audio)
        _clearAPackets(md);
    if(md->has_video)
        _clearVPackets(md);
    
    // don't procede unless there is room on both buffers,
    // since we don't want to store an undetermined amt of
    // data on the decoders internal memory
    if(_vHasRoom(md) && _aHasRoom(md))
    {
        if((res = _readOggPage(md, &page)) != 0 )
            return res; // will be 1, indicating error or eos
        // printf("Read a page\n");
        // load the page
        if( md->has_audio && ogg_page_serialno(&page) == md->vstream.serialno )
        {
            // printf("Audio Page\n");
            ogg_stream_pagein(&md->vstream, &page);
            // clear this page's data again, if there is room on buffers
            _clearAPackets(md);
        }
        // is it a video page?
        if( md->has_video && ogg_page_serialno(&page) == md->tstream.serialno )
        {
            // printf("Video Page\n");
            ogg_stream_pagein(&md->tstream, &page);
            // clear this page's data again, if there is room on buffers
            _clearVPackets(md);
        }
    }
    
    if(!_vHasRoom(md))
        printf("Video Full!\n");
    
    if(!_aHasRoom(md))
        printf("Audio Full!\n");
    
    if(!_vHasRoom(md) || !_aHasRoom(md))
        return -1; // indicates buffers are full
    
    return 0;
}

int md_fillBuffers(MediaDecoder *md)
{
    ogg_page page;
    ogg_packet packet;
    
    int res,has_room;
    
    has_room = 1;
    res = 0;
    // process more of the file as long as all used buffers have room
    while( 1 )
    {
        // fill the buffers from whatever page data has already been fed in
        if( md->has_audio )
            while(_abuf_dlen(md) < (7*md->abufsize)/8 && ogg_stream_packetout(&md->vstream, &packet) == 1)
                _dovpacket(md, &packet);
        
        if( md->has_video )
            while(VBroom(&md->vBuffer) > 0 && ogg_stream_packetout(&md->tstream, &packet) == 1)
                _dotpacket(md, &packet);
        
        has_room = (!md->has_audio || _abuf_dlen(md) < (7*md->abufsize)/8)
                && (!md->has_video || VBroom(&md->vBuffer) > 0);
        
        // continue and read a page if room remains
        if( !has_room || (res = _readOggPage(md, &page)) != 0 ) break;
        
        // is it an audio page?
        if( md->has_audio && ogg_page_serialno(&page) == md->vstream.serialno )
        {
            // printf("Audio Page\n");
            ogg_stream_pagein(&md->vstream, &page);
        }
        // is it a video page?
        if( md->has_video && ogg_page_serialno(&page) == md->tstream.serialno )
        {
            // printf("Video Page\n");
            ogg_stream_pagein(&md->tstream, &page);
        }
    }
    if( _abuf_dlen(md) >= (7*md->abufsize)/8 ) printf("Audio FULL\n");
    if( VBroom(&md->vBuffer) <= 0 ) printf("Video FULL\n");
    
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

static void _dotpacket(MediaDecoder *md, ogg_packet *packet)
{
	VideoFrame *frm;
    th_ycbcr_buffer ycbcr;
    int k;
    
    // static int pcnt = 0;
    
    if(VBroom(&md->vBuffer) <= 0)
		return;
    
    // printf("Processed %d packets\n", pcnt);
    // pcnt++;
    // decode the video page packet
    // if there is a problem, or eg this is a header, we don't do anything more with it
    ogg_int64_t granulepos = 0;
    if(th_decode_packetin(md->tdec, packet, &granulepos) != 0)
		return;
	
	if(th_decode_ycbcr_out(md->tdec, ycbcr) != 0)
        return;
    
    frm = VBgetAddItem(&md->vBuffer);
    
    // copy ycbcr data into frm->pixels with clipping
    _VideoClip(ycbcr, frm->pixels, &md->tinfo);
    
    frm->vindex = md->vcnt;
    
    // printf("Buffering Video Packet (%d) gr %ld\n", frm->vindex, granulepos);
    
    // printf("Adding a video frame at async=%d\n", frm->async);
    md->vcnt++;
    // that's it, the video frame is already added
}

int time2vindex(MediaDecoder *md, int time_ms)
{
    return (time_ms * md->tinfo.fps_numerator) / (md->tinfo.fps_denominator * 1000);
}

int vindex2time(MediaDecoder *md, int vindex)
{
    return (1000*vindex * md->tinfo.fps_denominator) / md->tinfo.fps_numerator;
}

// TODO the following has issues
// returns 0 if the packet was accepted. Otherwise, the packet still needs to be read!
// for now, if a packet isn't read, it is simply dropped.
static int _dovpacket(MediaDecoder *md, ogg_packet *packet)
{
    // pass the packet data into the decoder and get a vorbis block
    int samples,shave,k,j,len;
    float **pcm;
    
    // printf("Processed Audio Packet\n");
    
	// if there is a problem eg this is a header, we don't do anything more with it
    if(vorbis_synthesis(&md->vblock, packet))
    {
        printf("Error: Can't get audio block!\n");
		return 1;
    }
    
	if(vorbis_synthesis_blockin(&md->vdsp, &md->vblock))
    {
        printf("Error: Decoder not accepting blocks!\n");
		return 1;
    }
    
    if( md->abuffull )
    {
        printf("Buffer is full!\n");
        return 1; // buffer is full! reject the packet
    }
    
    // MptMutLock(md->ablenmut);
    
    // get pcm audio data
    samples = vorbis_synthesis_pcmout(&md->vdsp, &pcm);
    shave = samples;
    
    len = (md->abufhead + md->abufsize - md->abuftail) % md->abufsize;
    
    //printf("getlen WRITE: t=%d, h=%d, s=%d => len=%d\n", md->abuftail, md->abufhead, md->abufsize, len);
    
    // printf("Buffer has %d bytes available\n", len);
    // it is safe for data to be read at the same time from this point
    
    samples = min(samples, (md->abufsize - len) / md->bps);
    
	if(samples > 0)
	{
        int channels = md->vinfo.channels;
        float *fbuffer = (float *)md->aBuffer;
        const int bufsize = md->abufsize / sizeof(float);
        const int bufhead = md->abufhead / sizeof(float);
		// interlace the audio data and put it on the end of the buffer
		for(k=0; k < md->vinfo.channels; k++)
			for(j=0; j < samples; j++)
				fbuffer[ (bufhead + j*channels + k) % bufsize ] = pcm[k][j];
        // move head ahead as if we added more data
        if(samples == (md->abufsize - len) / md->bps) md->abuffull = 1;
        md->abufhead = ( md->abufhead + samples*md->bps ) % md->abufsize;
	}
	// MptMutUnlock( md->ablenmut );
    
    //printf("    Put %d of %d samples on audio buffer (%d -> %d)\n", samples, shave, len/sizeof(float), ((md->abufhead + md->abufsize - md->abuftail) % md->abufsize) / sizeof(float));
    
	// count samples decoded onto the buffer
	md->acnt += samples;
    
    // printf("    _dovpacket read %d samples, %d bytes\n", samples, samples*md->bps);
	
    // printf("Buffering Audio Packet (%ld)\n", md->acnt);
    
    // MptMutUnlock(md->ablenmut);
    
	// tell the decoder how much data we used
	vorbis_synthesis_read(&md->vdsp, samples);
    return 0;
}

//////////////////////////////////////
// Video and Audio Access Functions //
//////////////////////////////////////

// get the last video frame whose play time is before asample
// return NULL if there is none
VideoFrame *md_getVideo(MediaDecoder *md)
{
    VideoFrame *frm;
    if(md->vBuffer.len <= 0)
    {
        printf("md_getVideo: buffer is empty\n");
		return NULL;
    }
    frm = VBgetRemoveItem(&md->vBuffer);
	if(md->vBuffer.len <= 0)
        printf("md_getVideo: returning last video on buffer\n");
        
    return frm;
}


int md_getNextVideoIndex(MediaDecoder *md)
{
    VideoFrame *frm;
    if(md->vBuffer.len <= 0)
    {
        printf("md_getVideo: buffer is empty\n");
		return -1;
    }
    frm = VBpeak(&md->vBuffer);
    return frm->vindex;
}

/*
VideoFrame *md_getVideo_n(MediaDecoder *md, int n);
{
	VideoFrame *frm,*nxt;
	
    // printf("md_getVideo: buffer has %d items\n", md->vBuffer.len);
	if(md->vBuffer.len <= 0)
    {
        printf("md_getVideo: buffer is empty\n");
		return NULL;
    }
    
	frm = VBgetRemoveItem(&md->vBuffer);
	if(md->vBuffer.len <= 0)
    {
        printf("md_getVideo: returning last video on buffer\n");
		return frm;
    }
		
	// get the first frame such that the following frame comes after asample
	// if we run out of frames, use the last frame from the stack, so that
	// there is at least some video playing as the player tries to catch up
	nxt = VBpeak(&md->vBuffer);
	while(md->vBuffer.len > 0 && nxt->async < asample)
	{
        printf("md_getVideo: skipping video frame\n");
		frm = VBgetRemoveItem(&md->vBuffer);
		nxt = VBpeak(&md->vBuffer);
	}
    printf("Getting video frame (%d)\n", frm->async);
	return frm;
}
*/

/*
 * int md_getNextVideoSync(MediaDecoder *md)
{
	VideoFrame *frm;
    if( !md->has_video )
        return -1;
    if( md->vBuffer.len <= 0) return -1;
	frm = VBpeak(&md->vBuffer);
	return frm->async;
}
* */

// get number of samples decoded - # of samples of the buffer
// ie this is one less than the sample number of the first sample on the buffer
int md_getNextSampleNum(MediaDecoder *md)
{
    // samples that have gone on the buffer - samples still on the buffer = samples removed from the buffer
	if(md->has_audio)
		return md->acnt - _abuf_dlen(md) / md->bps;
	return -1;
}

// len is the number length of the data stream, which are floats
// len will be num_samples * num_channels
// we return a length of data which is a multiple of num_channels so that length <= len
int md_getAudio(MediaDecoder *md, float *data, int len)
{
	int k, lenin, buflen, toskip;
    lenin = len;
    toskip = md->toskipaudio; // need to 'extract' this in case it changes
    
    if( md->abuffull )
        buflen = md->abufsize / sizeof(float);
    else
        buflen = ((md->abufhead + md->abufsize - md->abuftail) % md->abufsize) / sizeof(float);
    
    toskip = min(toskip,buflen); // can't skip more than we have
    
    md->toskipaudio -= toskip;
    
    len = min(len - (len % md->vinfo.channels), buflen - toskip);
    
    float *fbuffer = (float *)md->aBuffer;
    const int bufsize = md->abufsize / sizeof(float);
    const int buftail = ((md->abuftail + toskip) % md->abufsize) / sizeof(float);
    // interlace the audio data and put it on the end of the buffer
    for(k=0; k < len; k++)
        data[k] = fbuffer[ (buftail + k) % bufsize ];
    
    // move tail ahead as if removed data
    md->abuftail = ( md->abuftail + toskip + len*sizeof(float) ) % md->abufsize;
    
    // printf("  Got %d/%d requested samples buffer (%d -> %d)\n", len, lenin, buflen, ((md->abufhead + md->abufsize - md->abuftail) % md->abufsize) / sizeof(float));
    if( len > 0 ) md->abuffull = 0;
    
    // printf("Requested %d data points, gave %d\n", lenin, len);
    
    if( lenin != len )
        printf("SILENCE! %d floats removed from buffer -> %d remain\n", len, buflen - len); 
    
    return len;
}

void md_skipAudio(MediaDecoder *md, int len)
{
	md->toskipaudio += len*md->vinfo.channels;
}

int md_getAudioTime(MediaDecoder *md)
{
    // how much audio is on the buffer in ms?
	return (1000L*_abuf_dlen(md))/(md->bps*md->vinfo.rate);
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
