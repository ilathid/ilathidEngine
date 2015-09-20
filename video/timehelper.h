#ifndef TIMEHELPER_H
#define TIMEHELPER_H

#include <time.h>

#ifdef __MINGW32__
#include <windows.h>
#endif

typedef long long int TH_LONG;

#ifndef __MINGW32__
#ifdef __FreeBSD__
static inline void getTime(struct timespec *t){
	clock_gettime(CLOCK_REALTIME, t);
}
#else
static inline void getTime(struct timespec *t){
	//clock_gettime(CLOCK_PROCESS_CPUTIME_ID, t);
	clock_gettime(CLOCK_REALTIME, t);
}
#endif
#endif

#ifdef __MINGW32__
typedef struct {
    TH_LONG freq;
    TH_LONG start;
    int st;
} thTimer;
#else
typedef struct {
    struct timespec start;
    int st;
} thTimer;
#endif

void startTimer_th(thTimer *th, TH_LONG start_time);
TH_LONG getTime_th(thTimer *th); // milliseconds
void h_sleep(int usec);

#endif
