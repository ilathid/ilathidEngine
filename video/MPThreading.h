#ifndef MPTHREADING_H
#define MPTHREADING_H

#ifdef _WIN32
#include <windows.h>
#define MPTmut     HANDLE
#else
#include <pthread.h>
#include <unistd.h>
#define MPTmut     pthread_mutex_t
#endif

static void MptMutCreate(MPTmut mut)
{
#ifdef _WIN32
    mut = CreateMutex(NULL, 0, NULL);
#else
    pthread_mutex_init(&mut, NULL);
#endif
}

static void MptMutDestroy(MPTmut mut)
{
#ifdef _WIN32
    CloseHandle(mut);
#else
    pthread_mutex_destroy(&mut);
#endif
}

static void MptMutLock(MPTmut mut)
{
#ifdef _WIN32
    WaitForSingleObject(mut, INFINITE);
#else
    pthread_mutex_lock(&mut);
#endif
}

static void MptMutUnLock(MPTmut mut)
{
#ifdef _WIN32
    ReleaseMutex(mut);
#else
    pthread_mutex_unlock(&mut);
#endif
}

#endif
