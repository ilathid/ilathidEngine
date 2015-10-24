#include <unistd.h>
#include "Mixer.h"
#include "MPPool.h"
#include "MediaPlayer.h"

MediaPlayer *MPP_get(int mp_id);

void updatevid(char *pixels, void *funcdata)
{
    SDL_Overlay *mov = (SDL_Overlay *)funcdata;
    int w = mov->w;
    int h = mov->h;
    SDL_Rect dstrect = { 0, 0, w, h };
    // printf("Rendering Video\n");
    Uint8 *dst;
    int i;
    const Uint8 *y = (const Uint8 *) pixels;
    const Uint8 *u = y + (w * h);
    const Uint8 *v = u + ((w/2) * (h/2));
    
    SDL_LockYUVOverlay(mov);
    dst = mov->pixels[0];
    for (i = 0; i < h; i++, y += w, dst += mov->pitches[0])
        memcpy(dst, y, w);

    dst = mov->pixels[1];
    for (i = 0; i < h/2; i++, u += w/2, dst += mov->pitches[1])
        memcpy(dst, u, w/2);

    dst = mov->pixels[2];
    for (i = 0; i < h/2; i++, v += w/2, dst += mov->pitches[1])
        memcpy(dst, v, w/2);

    SDL_UnlockYUVOverlay(mov);   
    SDL_DisplayYUVOverlay(mov, &dstrect);
}

int main()
{   
    MediaPlayer *mp2p, *mp3p;
    int mp1,mp2,mp3,mp4,mp5;
    int k;
    SDL_Surface *dis2;
    SDL_Overlay *mov2;
    SDL_Surface *dis3;
    SDL_Overlay *mov3;
    printf("Initializing the Mixer\n");
    mixer_init();
    
    printf("Initialize SDL play window\n");
    
    if(SDL_Init(SDL_INIT_VIDEO) == -1)
        printf("Couldn't open SDL video: %s\n", SDL_GetError());
    
    mixer_new_class("sfx");
    mixer_new_class("sfx_quiet");
    mixer_set_volume("sfx", 200);
    mixer_set_volume("sfx_quiet", 120);
    
    printf("Openning the Video\n");
    //mp1 = MPP_create("./test.ogg", 0, "sfx_quiet");
    //mp2 = MPP_create("./small.ogv", 0, "sfx");
    mp2 = MPP_create("./big_buck_bunny_480p.ogv", 0, "sfx");
    //mp4 = MPP_create("./big_buck_bunny_480p.ogv", 0, "sfx");
    //mp5 = MPP_create("./big_buck_bunny_480p.ogv", 0, "sfx");
    
    mp2p = MPP_get(mp2);
    //mp3p = MPP_get(mp3);
    
    if(mp_hasVideo(mp2p))
    {
        printf("Creating the video screen\n");
        dis2 = SDL_SetVideoMode(MPP_getWidth(mp2),MPP_getHeight(mp2),0,SDL_HWSURFACE);
        mov2 = SDL_CreateYUVOverlay(MPP_getWidth(mp2), MPP_getHeight(mp2), SDL_IYUV_OVERLAY, dis2);
        mp_setVidCallback(mp2p, updatevid, (void *)mov2);
    }
    
    MPP_play(mp2);
    sleep(7);
    /*
    MPP_play(mp1);
    sleep(2);
    MPP_play(mp2);
    sleep(2);
    MPP_play(mp3);
    sleep(2);
    MPP_play(mp4);
    sleep(2);
    MPP_play(mp5);
    
    for(k = 0; k < 100; k++)
    {
        mixer_set_volume("sfx_quiet", 120-k);
        usleep(50000);
    }
    sleep(20);
    for(k = 0; k < 100; k++)
    {
        mixer_set_volume("sfx_quiet", 20+k);
        usleep(50000);
    }
    sleep(8);
    for(k = 0; k < 100; k++)
    {
        mixer_set_volume("sfx_quiet", 120-k);
        usleep(50000);
    }
    */
}

