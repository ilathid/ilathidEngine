#include "timehelper.h"

void startTimer_th(thTimer *t, TH_LONG start_time){
        t->st = start_time;
#ifdef __MINGW32__
        LARGE_INTEGER tc;
        QueryPerformanceCounter(&tc);
        t->start = tc.QuadPart;
        QueryPerformanceFrequency(&tc);
        t->freq = tc.QuadPart;
#else
        getTime(&(t->start));
#endif
}

TH_LONG getTime_th(thTimer *t){
        TH_LONG tim;
#ifdef __MINGW32__
        LARGE_INTEGER tc;
        QueryPerformanceCounter(&tc);
        tim = tc.QuadPart - t->start;
        tim = 1000000 * tim;
        tim = tim / t->freq;
#else
        struct timespec end;
        getTime(&(end));
        tim = ( end.tv_sec - t->start.tv_sec )*1000
                + ( end.tv_nsec - t->start.tv_nsec )/1000000;
#endif
        return tim + t->st;
}

// millisecond sleep
void h_sleep(int ms){
#ifdef __MINGW32__
    Sleep(ms);
#else
    usleep(ms*1000);
#endif
}
