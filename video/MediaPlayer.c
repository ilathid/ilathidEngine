#include "MediaPlayer.h"

/*
TODO:
- update ffmpeg on my device (I am at 0.7.13, version has moved through .8, .9, 1.0)

- Major cleanup of everything   
- thread needs to be protected from sig events
- I need to try to understand how to properly cleanup items. If need be, for example, the rendered image data could be copied into a non-AVPicture object, so that the AVPicture can be freed correctly.
- Make some test cases. Try playing as many videos as possible
- check for the presence of vstream and astream
- Looping playback
- Comments and documentation
*/

void _init_values_mp(MediaPlayer *mp){
    mp->inited = 0;
    mp->looping = 0;
    mp->filepath = NULL;
    mp->vstream = NULL;
    mp->astream = NULL;
    mp->thread = NULL;
    mp->conv = NULL;
    mp->tstate = 0;
    mp->event = MP_EVENT_NONE;
    mp->picacq = 1;
    mp->outbuf_len = 0;
    mp->outbuf_size = 0;
    // mp->startTime = 0;
    mp->pauseTime = 0;
    mp->fmt_ctx = NULL;
    }

/** Initialize a media player object.
 *  The given file is opened, I believe.
 *  The corresponding memory cleaning routine is close_mp.
 */
int init_mp(MediaPlayer *mp, char *filepath){
    int err = 0;
    int i;
    AVCodec *codec;
    
    // initialize values
    _init_values_mp(mp);
    
    mp->outbuf_size = AVCODEC_MAX_AUDIO_FRAME_SIZE + ALIBRARY_AUDIO_SIZE;
    mp->outbuf = (short int *)malloc(sizeof(short int)*(mp->outbuf_size));
    mp->outbuf_len = 0;
    
    printf("outbuf_size %d\n", mp->outbuf_size);
    
    pthread_mutex_init(&mp->mut_pic, NULL);
    mp->filepath = filepath;
    
    // Libavcodec
    //===========
    // Register codecs in libav
    av_register_all();
    // Open the media file
    err = avformat_open_input(&mp->fmt_ctx, mp->filepath, NULL, NULL);
    if (err != 0){
        // failed to open the file
        char errbuf[128];
        av_strerror(err, errbuf, sizeof(errbuf));	
        printf("Failed to open file! %s\n", errbuf);
        
        // cleanup
        return -1;
        }
    // avformat_find_stream is an involved function which probes some of the
    // file packets to be sure of the properties of the file.
    err = avformat_find_stream_info(mp->fmt_ctx, NULL);
    if (err != 0){
        char errbuf[128];
        av_strerror(err, errbuf, sizeof(errbuf));
        printf("Could not read media info! %s\n", errbuf);

        // close the file
        av_close_input_file(mp->fmt_ctx);
        
        return -1;
        }
    // Find what streams are available
    for(i=0;i < mp->fmt_ctx->nb_streams;i++){
        if (mp->vstream == NULL && mp->fmt_ctx->streams[i]->codec->codec_type == AVMEDIA_TYPE_VIDEO)
            mp->vstream = mp->fmt_ctx->streams[i];
        if (mp->astream == NULL && mp->fmt_ctx->streams[i]->codec->codec_type == AVMEDIA_TYPE_AUDIO)
            mp->astream = mp->fmt_ctx->streams[i];
        }
    if (mp->vstream != NULL){
        // initialize the video codec
        codec = avcodec_find_decoder(mp->vstream->codec->codec_id);

        if (codec == NULL){
            // raise Exception("No video Decoder Found")
            printf("No video Decoder Found\n");
            mp->vstream = NULL;
            return -1;
            }
        printf("Found Video Codec: %s\n", codec->name);
        
        // Initialize the context
        if (avcodec_open(mp->vstream->codec, codec)){
            // raise Exception("Failed to open video codec context")
            printf("Failed to open video codec context\n");
            mp->vstream = NULL;
            return -1;
            }
        else{
            printf("Video timebase: %d/%d\n", mp->vstream->time_base.num, mp->vstream->time_base.den);
            }
        }
        // At this point, the codec context is ready for use.
        // Codec context is mp->vstream->codec
        // Codec is mp->vstream->codec->codec
        
    // TODO: I assume that codec is freed by vstream->codec->
    if (mp->astream != NULL){
        // initialize the audio codec

        codec = avcodec_find_decoder(mp->astream->codec->codec_id);

        if (codec == NULL){
            // raise Exception("No audio Decoder Found")
            printf("No audio Decoder Found\n");
            mp->astream = NULL;
            return -1;
            }
        printf("Found Audio Codec: %s\n", codec->name);
        
        // Initialize the context
        if (avcodec_open(mp->astream->codec, codec)){
            // raise Exception("Failed to open audio codec context")
            printf("Failed to open audio codec context\n");
            mp->astream = NULL;
            return -1;
            }
        else{
            // set up the audio output device
            init_ad(&mp->device, av_get_bytes_per_sample(mp->astream->codec->sample_fmt), mp->astream->codec->channels, mp->astream->codec->sample_rate);
            if (mp->device.opened == 1)
                printf("Successfully opened audio device\n");
            else
                printf("Failed to opene audio device\n");
            }
//#endif
        }
    if (mp->astream == NULL && mp->vstream == NULL){
        printf("Media file lacks playable stream!\n");
        
        // close the file
        av_close_input_file(mp->fmt_ctx);
        return -1;
        
        }
    // initialize packet buffers
    // packet buffers hold mpeg, mp2, etc compressed packets
    init_pb(&mp->abuffer);
    init_pb(&mp->vbuffer);
    mp->inited = 1;
    
    return 0;
    }

int getVidWidth_mp(MediaPlayer *mp){
    if (mp->vstream == NULL)
        return 0;
    else
        return mp->vstream->codec->width;
    }

int getVidHeight_mp(MediaPlayer *mp){
    if (mp->vstream == NULL)
        return 0;
    else
        return mp->vstream->codec->height;
    }

void close_mp(MediaPlayer *mp){
    /*clean:
    mp->filepath
    mp->vstream
    mp->astream
    mp->thread
    mp->conv
    mp->fmt_ctx
    */

    free(mp->outbuf);

    // free sws context, if allocated
    if (mp->conv != NULL)
        sws_freeContext(mp->conv);

    clear_pb(&mp->abuffer);
    clear_pb(&mp->vbuffer);
    
    //printf("here\n");
    
    // av_register_all();

    // close codec
    
    if(mp->vstream != NULL){
        avcodec_close(mp->vstream->codec);
        mp->vstream = NULL;
        }
    if(mp->astream != NULL){
        avcodec_close(mp->astream->codec);
        mp->astream = NULL;
        }
    
    // mp->vstream->codec->codec_id
    
    // close stream?

    // close context
    av_close_input_file(mp->fmt_ctx);

    close_ad(&mp->device);
    
    // reset values
    _init_values_mp(mp);

    mp->inited = 0;
    
    // close mutex
    pthread_mutex_destroy(&mp->mut_pic);
    }
    
int _pread_mp(MediaPlayer *mp, int apackets, int vpackets){
    /*
    Reads at most this many packets into the buffers.
    Returns number of bytes read
    */
    int tot;
    AVPacket p;
    AVPacket *bufp;
    int ifread;
            
    // if(getSize_pb(&mp->abuffer) > 0) return 0;
            
    tot = apackets + vpackets;
    // printf("pread total: %d\n", tot);
    
    // print mp->vstream->index
    // print mp->astream->index
    // int cnt = 0;
    while (apackets > 0 && vpackets > 0){
        //print "Read a packet"
        ifread = av_read_frame(mp->fmt_ctx, &p);
        if (ifread == 0){
            //printf("Freeing %d\n", cnt);
            //printf("READpsize %d\n", p.size);
            // cnt++;
            // av_free(p.data);
            //av_dup_packet(&p);
            //av_free_packet(&p);
            //continue;
            //printf("pts: %ld\n", (long int)p.dts);
            
            // av_dup_packet(&p)
            // Create a reference to the packet's internal memory
            //print p.stream_index
            //print mp->vstream->index
            //print mp->astream->index
            //print p.size
            if (mp->vstream != NULL && p.stream_index == mp->vstream->index){
                bufp = getWrite_pb(&mp->vbuffer);
                vpackets -= 1;
                }
            else if(mp->astream != NULL && p.stream_index == mp->astream->index){
                bufp = getWrite_pb(&mp->abuffer);
                apackets -= 1;
                //printf("Packet size: %d\n", p.size);
                }
            else{
                av_free_packet(&p);
                p.dts = -1;
                //printf(" DD\n");
                continue;
                }
            // Copy internal pointer objects
            // av_free_packet(&p);
            //int siz = p.size;
            //uint8_t *dat = p.data;
            *bufp = p;
            // av_free_packet(&p);
            //av_free_packet(bufp);
            //bufp->size = siz;
            //bufp->data = dat;
            //printf("%d: D2 %u\n", cnt, bufp->data);
            
            //printf("pts2: %d\n", bufp.dts)
            
            // Make sure packet has its own memory
            if(av_dup_packet(bufp)){
                // ONLY free if duplication occured
                //printf("DUP AND FREE\n");
                av_free_packet(&p);
                }
            
            // printf("%d: D3 %u\n", cnt, bufp->data);
            // if(cnt == 65) break;
            }
        else{
            // av_free_packet(&p);
            // p->dts = 0;
            //printf("Failed to read... eof?\n");
            //TODO eof should only need to be tested once, then some flag should be set
            break;
            }
        }
    // printf("Done filling packets\n");
    return tot - apackets - vpackets;
    }
    
void _processVideo_mp(MediaPlayer *mp){
    AVFrame *f;
    AVPacket *p;
    AVPicture temp_pic;
    int is_frame = 0;
    int dlen;
    AVPacket orig;
    
    //printf("VIDEO\n");
    
    if(mp->vstream == NULL){
        printf("Media has no video stream!!\n");
        return;
        }
    
    if (getSize_pb(&mp->vbuffer) > 0)
        p = getRead_pb(&mp->vbuffer);
    else{
        printf("processVideo: No video on buffer.\n");
        return;
        }
    
    f = avcodec_alloc_frame();

    // remember original data position    
    orig = *p;
    
    while (p->size > 0){
        dlen = avcodec_decode_video2(mp->vstream->codec, f, &is_frame, p);
        //dlen = p->size;
        if (dlen < 0){
            printf("Failed to decode video %d\n", dlen);
            *p = orig;
            return;
            }
        p->size -= dlen;
        p->data += dlen; // # pointer arithmatic?
        
        if (is_frame){
            // printf("Frame pts, pkt_pts, pkt_dts: %d, %d, %d\n", f->dts, f->pkt_pts, f->pkt_dts);
            // TODO consider not using avpicture, i just use it as a container anyway.
            avpicture_alloc(&temp_pic, 2, f->width, f->height);
            
            mp->conv = sws_getCachedContext(mp->conv, f->width, f->height, f->format, f->width, f->height, PIX_FMT_RGB24, SWS_BILINEAR, NULL, NULL, NULL);
            // print "Planned transformation"
            
            // Convet the image into pic, using the above context (convet to rgb)
            sws_scale(mp->conv, (const uint8_t * const*)f->data, f->linesize, 0, f->height, temp_pic.data, temp_pic.linesize);

            // printf("%u\n", (unsigned int)f->data[0][129*129*3]);
            
            pthread_mutex_lock(&mp->mut_pic);
            if (mp->picacq == 0){
                //printf("Will free %d\n", &mp->picbuf);            
                avpicture_free(&mp->picbuf);
                }
            mp->picbuf = temp_pic;
            mp->picacq = 0;
            mp->picw = f->width;
            mp->pich = f->height;
            pthread_mutex_unlock(&mp->mut_pic);
            
            }
        //else
        //    //printf("No Frame\n");
        }
    
    // reset pointer
    *p = orig;
    
    // Free old frame
    av_free(f);
    // free(f);
    av_free_packet(p);
    p->dts = -1;
    }

void setVolMono_mp(MediaPlayer *mp, float vol){
    setVol_ad(&mp->device, vol, vol);
    }

void setVol_mp(MediaPlayer *mp, float voll, float volr){
    setVol_ad(&mp->device, voll, volr);
    }

/** Internal process one packet of sound and play it.
 */
void _processAudio_mp(MediaPlayer *mp){
    /* Question: If it's called a packet, why is it used as a buffer? */
    AVPacket *p;
    int dlen;
    
    // Decoded Audio Buffer
    
    int cnt;
    cnt = 0;
    
    if(mp->astream == NULL){
        printf("Error: Media has no audio stream!!\n");
        return;
        }
    
    if (getSize_pb(&mp->abuffer) > 0)
        p = getRead_pb(&mp->abuffer);
    else{
        printf("processAudio: No audio on buffer.\n");
        return;
        }
    //printf("data:%u\n", p->data);
    //av_free(p->data);
    //printf("X\n");
    //av_free_packet(p);
    //return;
    // printf("%d, %s\n", getLeft_pb(&mp->abuffer), p->data);
    // remember initial packet
    AVPacket orig = *p;

    // mp->outbuf is a buffer
    // At this point it must have less than ALIBRARY_AUDIO_SIZE of audio, and at least
    // AVCODEC_MAX_AUDIO_FRAME_SIZE of free space.
    
    // 

    short int *bufi = mp->outbuf + mp->outbuf_len;
    int outsized;
    int pind;
    int i;
    
    // bufi is guarenteed at this point to contain AVCODEC_MAX_AUDIO_FRAME_SIZE of free space
    while (p->size > 0){
        outsized = mp->outbuf_size - mp->outbuf_len;
        //printf("outsized %d (%d, %d)\n", outsized, mp->outbuf_size, mp->outbuf_len);
        dlen = avcodec_decode_audio3(mp->astream->codec, &(mp->outbuf[mp->outbuf_len]), &outsized, p);
        // printf(" PACKET(A): %d\n", p->dts);
        if (dlen < 0){
            //printf("Failed to decode audio %d\n", dlen);
            *p = orig;
            return;
            }
        p->size -= dlen;
        p->data += dlen; // pointer arithmatic?
        mp->outbuf_len += outsized;
        
        // printf("len %d\n", outsized);
        
        // send to alibrary as many packets as possible
        for(pind = 0; pind + ALIBRARY_AUDIO_SIZE <= mp->outbuf_len; pind += ALIBRARY_AUDIO_SIZE){
            //printf("Playing %ld", mp->outbuf + pind);
            play_ad(&mp->device, (char*)(mp->outbuf + pind), ALIBRARY_AUDIO_SIZE);
            }
        //printf("\n");
        // reorganize the leftover bytes on the buffer
        mp->outbuf_len = mp->outbuf_len % ALIBRARY_AUDIO_SIZE;
        if(pind > 0 && mp->outbuf_len > 0){
            //printf("Reorganizing %d bytes\n", mp->outbuf_len);
            for(i = 0; i < mp->outbuf_len; i++){
                mp->outbuf[i] = mp->outbuf[pind + i];
                }
            }

        cnt += 1;
        }
    //printf("Finished audio with %d on buffer\n", mp->outbuf_len);
    *p = orig;
    // printf("-> %d\n", p->size);
    av_free_packet(p);
    p->dts = -1;
    }
    
int hasAudio_mp(MediaPlayer *mp){
    return mp->astream != NULL;
    }
            
int hasVideo_mp(MediaPlayer *mp){
    return mp->vstream != NULL;
    }
        
int getPlaybackTime_mp(MediaPlayer *mp){
    return getTime_th(&mp->playTimer);
    //return h_time()/1000 - mp->startTime;
    }   

// void setPauseTime_mp(MediaPlayer *mp, int pauseTime){
//     mp->pauseTime = pauseTime;
//     }    
int getPauseTime_mp(MediaPlayer *mp){
    return mp->pauseTime;
    }

/** Stops video playback. (resets timers, clears old buffers)
 */
void reset_mp(MediaPlayer *mp){
    //printf("here...\n");
    clear_pb(&mp->abuffer);
    clear_pb(&mp->vbuffer);
    //printf("cleared\n");

    // If the codec is open, flush its buffers    
    if (mp->vstream != NULL)
        avcodec_flush_buffers(mp->vstream->codec);
    if (mp->astream != NULL)
        avcodec_flush_buffers(mp->astream->codec);
    //printf("flushed\n");
    // seek to start of video
    // seek_target= av_rescale_q(0, AV_TIME_BASE_Q, pFormatCtx->streams[stream_index]->time_base)
    
    if (mp->astream != NULL)
        av_seek_frame(mp->fmt_ctx, mp->astream->index, 0, AVSEEK_FLAG_BYTE);
    else if (mp->vstream != NULL)
        av_seek_frame(mp->fmt_ctx, mp->vstream->index, 0, AVSEEK_FLAG_BYTE);
    //printf("seeked\n");
        
    mp->pauseTime = 0;
    }

void loop_mp(MediaPlayer *mp){
    if (mp->tstate == 0){    
        mp->looping = 1;
        play_mp(mp);
        }
    }

/** Being playing the media. Must be inited 
 */
void play_mp(MediaPlayer *mp){
    if (mp->inited == 0){
        printf("play_mp: media not initiated.\n");
        }
    else{
        if (mp->tstate == 0){
            mp->tstate = 1;
            mp->event = MP_EVENT_NONE;
            // This is safe. If a thread is already running, it must be
            //  practically done since tstate was 0. So its reference 
            // isn't needed anyway.
            pthread_create( &mp->thread, NULL, (void *(*)(void *))_playbackLoop_mp, (void *)mp );
            //printf("Created thread: %x\n", (unsigned int)mp->thread);
            }
        else{
            printf("play_mp failed: Media is already playing.\n");
            }
        }
    }

long getDuration_mp(MediaPlayer *mp){
    AVStream *strm;
    if (mp->astream != NULL)
        strm = mp->astream;
    else if(mp->vstream != NULL)
        strm = mp->vstream;
    else
        return 0;
    //printf("In Duration: %ld, %d, %d, %f\n", (long)strm->duration, strm->time_base.num, strm->time_base.den, (double)strm->duration * (double) strm->time_base.num / (double)strm->time_base.den);
    return (strm->time_base.num * strm->duration * 1000) / (strm->time_base.den);
    }

// time is in 1/1000 sec
void seek_mp(MediaPlayer *mp, int time){
    if (mp->tstate == 0){
        // choose a stream
        AVStream *strm;
        if (mp->astream != NULL)
            strm = mp->astream;
        else if(mp->vstream != NULL)
            strm = mp->vstream;
        else{
            printf("Seek_mp: no stream\n");
            return;
            }
        // get time in correct time base
        int64_t tb = ((int64_t)strm->time_base.den * (int64_t)time) / ((int64_t)strm->time_base.num * 1000);
        //printf("Seeking to %ld\n", tb);
        if(time < mp->pauseTime){ // is behind us
            if(mp->pauseTime - time < time) // is best to go backwards
                av_seek_frame(mp->fmt_ctx, strm->index, tb, AVSEEK_FLAG_BACKWARD);
            else{ // go to the beginning, then forwards
                av_seek_frame(mp->fmt_ctx, strm->index, 0, AVSEEK_FLAG_BYTE);
                av_seek_frame(mp->fmt_ctx, strm->index, tb, 0);
                }
            }
        else{// it is ahead.
            //printf("Seeking\n");
            av_seek_frame(mp->fmt_ctx, strm->index, tb, 0);
            }
        mp->pauseTime = time;
        }
    else
        printf("seek_mp failed: Media is currently playing. Pause or stop first.");
    }

/** Returns 1 if media is playing, 0 otherwise
 */
int getState_mp(MediaPlayer *mp){
    return mp->tstate;
    }

/** Stops the media if it is playing. On next play, the media will resume at
 *  the same location. (Use reset_mp to reset)
 */
void interrupt_mp(MediaPlayer *mp){
    // returns playback time when playback loop terminated
    // TODO mutex protect state?
    if (getState_mp(mp) == 1){
        mp->event = MP_EVENT_PAUSE;
        pthread_join(mp->thread, NULL);
        }
    mp->thread = NULL;
}

// convert to milliseconds
int _correctPts_mp(AVStream *stream, int pts){
    if (pts == -1) return -1;
    // printf("pts: %d; corrected: %d\n", pts, (stream->time_base.num * pts) / (stream->time_base.den/1000));
    return (stream->time_base.num * pts) / (stream->time_base.den/1000);
    }

/** internal thread function for playback.
 *  Assumes mpstate=1 on entry.
 */
void *_playbackLoop_mp(MediaPlayer *mp){
    int tim, nexta, nextv, sleep_time;
    
    // fix first dts issue
    int firstdts = -1;
    if(mp->vstream != NULL)
        firstdts = _correctPts_mp(mp->vstream, mp->vstream->first_dts);
    if(mp->astream != NULL)
        if(firstdts == -1 || mp->astream->first_dts < firstdts)
            firstdts = _correctPts_mp(mp->astream, mp->astream->first_dts);
    
    // set med timers according to pauseTime
    if (mp->pauseTime > 0)
        startTimer_th(&mp->playTimer, mp->pauseTime);
    else
        startTimer_th(&mp->playTimer, firstdts);

    // reset pauseTime for next time
    mp->pauseTime = 0;
    //printf("<<<PLAY>>>\n");
    while (mp->event == MP_EVENT_NONE){
        // read more data
        // Read file data into buffers if needed

        if((getLeft_pb(&mp->abuffer) > 0 && getSize_pb(&mp->abuffer) < 100) || (getLeft_pb(&mp->vbuffer) > 0 && getSize_pb(&mp->vbuffer) < 100))
            _pread_mp(mp, getLeft_pb(&mp->abuffer), getLeft_pb(&mp->vbuffer));
        
        
        //printf("(%d %d)\n", getSize_pb(&mp->abuffer), getSize_pb(&mp->vbuffer));
        sleep_time = 0;
        
        // get smallest upcoming pts
        tim = getPlaybackTime_mp(mp);
        nexta = -1;
        nextv = -1;
        if (mp->astream != NULL)
            nexta = _correctPts_mp(mp->astream, nextPts_pb(&mp->abuffer));
        if (mp->vstream != NULL)
            nextv = _correctPts_mp(mp->vstream, nextPts_pb(&mp->vbuffer));
    
        // printf("pbt %d; t %d pts(%d, %d); diff to audio time %d\n", tim, tim+mp->startTime, nexta, nextv, nexta - tim + atime_ad(&mp->device));
        //printf("nexta, nextv; tim: %d, %d; %d\n", nexta, nextv, tim);
        // printf("atime %d\n", atime_ad(&mp->device));
        
        if (nextv == -1 && nexta == -1){
            mp->event = MP_EVENT_EOF; // interrupt
            printf("Can't find a valid dts packet => EOF\n");
            }
        else if(nextv == -1 || (nexta != -1 && nexta < nextv)){
             // time until audio
            if(nexta  < 25 + tim + atime_ad(&mp->device))
                _processAudio_mp(mp);
            else{
                //printf("Audio left: %d\n", atime_ad(&mp->device));
                sleep_time = nexta - tim - atime_ad(&mp->device);
                }
            }
        else if(nexta == -1 || nextv <= nexta){
            // time until video
            if(nextv < tim + 3)
                _processVideo_mp(mp);
            else{
                // printf("Time of video: %d (%d)\n", nextv, tim);
                sleep_time = nextv - tim;
                }
            }
            // no else
        
        // sleep as needed
        if (sleep_time > 3){
            //printf("Sleeping %d...\n",sleep_time - 3);
            h_sleep((sleep_time - 3)*1000);
            }
        if (sleep_time < 0){
            mp->event = MP_EVENT_EOF; // interrupt
            printf("ERROR: neg sleep\n");
            }
            
        // deal with looping
        if(mp->event == MP_EVENT_EOF && mp->looping == 1){
            //printf("Looping\n");
            reset_mp(mp);
            startTimer_th(&mp->playTimer, firstdts);
            mp->event = MP_EVENT_NONE;
            }
        }
    
    //printf("Time on audio buffer:%d\n", atime_ad(&mp->device));
    
    //printf("Interrupt event\n");
    // turn off looping
    mp->looping = 0;
    
    // deal with EOF event
    if (mp->event == MP_EVENT_EOF){
        // is this safe?
        reset_mp(mp);
        }
    else{
        //printf("Set pauseTime\n");
        mp->pauseTime = getPlaybackTime_mp(mp);
        }
    mp->event = MP_EVENT_NONE;
    mp->tstate = 0;
    }

/** Get the most recently decoded video frame.
 */
mpframe getFrame_mp(MediaPlayer *mp){
    mpframe ret;
    
    if(mp->picacq == 1){
        // If there is no image, or the image is the same as one previously
        // acquired, just send an empty image. The caller must detect.
        ret.width = 0;
        ret.height = 0;
        ret.data = NULL;
        ret.len = 0;
        }
    else{
        pthread_mutex_lock(&mp->mut_pic);
        
        ret.data = *mp->picbuf.data;
        ret.width = mp->picw;
        ret.height = mp->pich;
        ret.len = 3*mp->picw*mp->pich; // hopefully this is right...
        //ret.len = av_image_fill_arrays(NULL, NULL, NULL, PIX_FMT_RGB24, mp->picw, mp->pich, 1);
        mp->picacq = 1;
        pthread_mutex_unlock(&mp->mut_pic);    
        }
    return ret;
    }
    
/** Free a mpframe given by getFrame_mp. This is needed because the data
 *  which was taken from an AVPicture seems to need a special AVPicture
 *  cleanup function.
 */
void free_mpframe(mpframe *fr){
    av_free(fr->data);
    }
