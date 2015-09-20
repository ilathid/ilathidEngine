#include "MediaPlayer.h"
#include "alibrary.h"
#include <time.h>

int main(int argc, char **argv){
    int i;
    
    printf("Starting the test.\n");
    MediaPlayer mp;
    MediaPlayer mp2;
    MediaPlayer mp3;
    printf("Created the mp struct.\n");
    initialize_al();
    
    
    printf("Initialized the sound module.\n");
    init_mp(&mp, "test.mp3");
    //init_mp(&mp2, "void.mpg");
    //init_mp(&mp3, "wall.mpg");
    // init_mp(&mp, "rocks.mpg");
    
    printf("Loaded up the media file.\n");
    
    // seek to half way
    printf("Duration: %d\n", getDuration_mp(&mp));
    seek_mp(&mp, getDuration_mp(&mp) / 2-10);
    
    play_mp(&mp);

    setVol_mp(&mp, 1.5, 1.5);
    
    for(i = 0; i < 3; i++){
        sleep(2);
        //play_mp(&mp2);
        }
    //interrupt_mp(&mp);        
    printf("SWITCH!\n");
    setVol_mp(&mp, 1.5, 0);
    sleep(2);
    //play_mp(&mp);
    //loop_mp(&mp2);
    //play_mp(&mp3);
    sleep(2);
    sleep(2);
    interrupt_mp(&mp);
    //interrupt_mp(&mp3);
    
    reset_mp(&mp);
    
    close_mp(&mp);
    //close_mp(&mp2);
    //close_mp(&mp3);
    
    shutdown_al();
    
    }
