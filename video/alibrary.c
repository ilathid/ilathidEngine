#include "alibrary.h"
#include "timehelper.h"

void init_ad(ADevice *ad, int bytes, int channels, int rate){
    int driver;
    int res;
    
    ad->nsstart = 0;
    ad->nsdelta = 0;
    
    ad->opened = 0;

    ad->voll = 128; // default median volume
    ad->volr = 128; // default median volume

    driver = ao_default_driver_id();

    ad->fmt.bits = bytes*8;
    ad->fmt.channels = 2; // I just always convert
    ad->fmt.rate = rate;
    //ad->fmt.rate = 44100;
    ad->fmt.byte_format = AO_FMT_NATIVE;
    ad->fmt.matrix = (char *)0;
    
    // chan rate bits
    // channels, s/sec, bits/s
    
    // rate*chan = true samples per second
    // bits*rate*chan = true bits/sec

    printf("Audio Driver: %d\n", driver);
    printf("bits: %d\n", ad->fmt.bits);
    printf("channels: %d\n", ad->fmt.channels);
    printf("rate: %d\n", ad->fmt.rate);
    printf("byte format: %d\n", ad->fmt.byte_format);
    printf("matrix: %d\n", (int)ad->fmt.matrix);
    
    // how many bytes per second does the device play?
    ad->byterate = ad->fmt.channels * ad->fmt.bits * ad->fmt.rate / (8);
    printf("\nbyterate: %d\n", ad->byterate);
    
    ao_sample_format fmt = ad->fmt;
    
    
    
    ad->device = ao_open_live(driver, &fmt, NULL); // # get device pointer
    if(ad->device != NULL){
        ad->opened = 1;
        printf("Open!\n\n");
        }
    }

void setVol_ad(ADevice *ad, float voll, float volr){
    if(voll < 0.0 || voll > 2.0){
        printf("alibrary: setVol voll must be 0.0 <= vol <= 2.0\n");
        return;
        }
    ad->voll = (char)(floor(0.5 + voll*127.5));
    printf("  Left volume set to %i\n", ad->voll);
    if(volr < 0.0 || volr > 2.0){
        printf("alibrary: setVol volr must be 0.0 <= vol <= 2.0\n");
        return;
        }
    ad->volr = (char)(floor(0.5 + volr*127.5));
    printf("  Right volume set to %i\n", ad->volr);
    }

/** How long until the device has played all of its current buffer?
 */
int atime_ad(ADevice *ad){
    int ret;
    unsigned int ti = h_time();
    if (ad->nsstart + ad->nsdelta < ti)
        ret = 0;
    else
        ret = ad->nsstart + ad->nsdelta - ti;
    return ret/1000;
    }

void adjustSample_ad(ADevice *ad, char *data, int len){
    // for now it does both channels together, and I don't know what to do about
    // endianess
    // volume control
    int channels = ad->fmt.channels;
    if(channels > 2){
        printf("alibray: Too many channels, can't adjust stereo volume.\n");
        channels = 1; // treat like all channels are the same
        }
    
    if(ad->voll != 128 || (channels > 1 && ad->volr != 128)){
        if(ad->fmt.bits == 8){
            // adjust as char
            int channel;
            int i;
            int vol;
            for(i = 0; i < len; i++){
                if(i % channels == 0){
                    vol = (((int)data[i] * (int)ad->voll)/128);
                    }
                else{
                    vol = (((int)data[i] * (int)ad->volr)/128);
                    }
                if (vol > 127) data[i] = 127;
                else if (vol < -128) data[i] = -128;
                else data[i] = (char)vol;
                }
            }
        else if(ad->fmt.bits == 16){
            // interpret as short int
            short int *data2 = (short int *)data;
            int len2 = len / 2;
            // adjust as short
            int i;
            int vol;
            for(i = 0; i < len2; i++){
                if(i % channels == 0){
                    vol = (((int)(data2[i]) * (int)ad->voll)/128);
                    }
                else{
                    vol = (((int)(data2[i]) * (int)ad->volr)/128);
                    }
                if (vol > 32767) data2[i] = 32767;
                else if (vol < -32768) data2[i] = -32768;
                else data2[i] = (short int)vol;                
                }
            }
        else
            printf("Failed to adjust volume\n");
        }
    /*
    ad->fmt.bits    bits per sample per channel
    ad->fmt.channels channels per sample
    ad->fmt.rate     samples per second
    ad->fmt.byte_format = AO_FMT_NATIVE; // endianess
    ad->fmt.matrix   ??
    */
    }
    
void play_ad(ADevice *ad, char *data, int len){
    if (ad->opened != 1){
        printf("Device not open!\n");
        return;
        }

    unsigned int ti = h_time();
    
    // 90 milliseconds limit
    if(ad->nsstart + ad->nsdelta > 90000 + ti){
        printf("play_ad: Error: Too much audio on buffer %u, %u\n", ad->nsstart + ad->nsdelta, 90000 + ti);
        return;
        }
    
    if (ad->nsstart + ad->nsdelta < ti){
        ad->nsstart = ti;
        ad->nsdelta = 0;
        // printf("RAN OUT\n");
    }
    
    // printf("Added %d millisec (%d bytes), to be played at time %d\n", (1000000 * len) / ad->byterate, len, ad->nsstart + ad->nsdelta);

    //printf(" %d", len);
    ad->nsdelta += (len*1000000) / ad->byterate; // round down
    
    adjustSample_ad(ad, data, len);
    
    if(ao_play(ad->device, data, len) == 0){
        printf("Audio failed to play on device...\n"); // 0 = failure
        //ao_close(ad->device);
        //ad->opened = 0;
        }
    }
    
void close_ad(ADevice *ad){    
    // free memory? TODO
    printf("Cleaning\n");
    //fftw_free(out);
    
    if(ad->opened == 1) ao_close(ad->device);
    }

void initialize_al(void){
    ao_initialize();  
    

    }

void shutdown_al(void){
    ao_shutdown();    

    }
