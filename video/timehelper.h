#ifndef TIMEHELPER_H
#define TIMEHELPER_H

#include <time.h>

extern time_t base_sec;

typedef struct {
    struct timespec st;
} thTimer;

void startTimer_th(thTimer *th, unsigned int start_time);
unsigned int getTime_th(thTimer *th);

void h_setBaseTime(void);

unsigned int h_time(void);
void h_sleep(unsigned int usec);

#endif
