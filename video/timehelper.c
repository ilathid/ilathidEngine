#include "timehelper.h"

// start_time is the initial timer value
void startTimer_th(thTimer *th, unsigned int start_time){
    struct timespec tt;
    if(clock_gettime(CLOCK_REALTIME, &tt) == 0){
        th->st = tt;
        th->st.tv_sec -= start_time / 1000;
        th->st.tv_nsec -= (unsigned int)(start_time % 1000)*1000000u;
        // underflow: wraps
        // TODO: This looks really ugly, but I think it works
        if(th->st.tv_nsec > 1000000000u){
            th->st.tv_nsec += 1000000000u;
            th->st.tv_sec--;
            }
        }
    }

unsigned int getTime_th(thTimer *th){
    unsigned int tm = 0;
    // The following will only work on freebsd i think
    // microseconds
    struct timespec tt;
    // if(clock_gettime(CLOCK_REALTIME_FAST, &tt) == 0){
    if(clock_gettime(CLOCK_REALTIME, &tt) == 0){
        tm = (tt.tv_sec - th->st.tv_sec)*1000 + (tt.tv_nsec - th->st.tv_nsec)/1000000;
        }
    // posix
    // tm clock_gettime(CLOCK_REALTIME, void)
    // Also: windows
    // Look up linux, mac api
    return tm;
    }


time_t base_sec = 0;

void h_setBaseTime(void){
    struct timespec tt;
    // if(clock_gettime(CLOCK_REALTIME_FAST, &tt) == 0){
    if(clock_gettime(CLOCK_REALTIME, &tt) == 0){
        base_sec = tt.tv_sec;
        }
    }

unsigned int h_time(void){
    unsigned int tm = 0;
    // The following will only work on freebsd i think
    // microseconds
    struct timespec tt;
    // if(clock_gettime(CLOCK_REALTIME_FAST, &tt) == 0){
    if(clock_gettime(CLOCK_REALTIME, &tt) == 0){
        tm = (tt.tv_sec - base_sec)*1000000 + tt.tv_nsec/1000;
    }
    // posix
    // tm clock_gettime(CLOCK_REALTIME, void)
    // Also: windows
    // Look up linux, mac api
    return tm;
}

void h_sleep(unsigned int usec){
    usleep(usec);
}
