#CC=gcc48
#CPP=g++48
CC=cc
CPP=c++
CFLAGS=-fno-strict-aliasing -O3 -pipe -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -g2 -Wformat
DEPS = MediaPlayer.h alibrary.h timehelper.h packetbuffer.h
#DEBUG = -pg
DEBUG = -DNDEBUG

.PHONY: all
all:  libMPPool.so.1 totest

Mixer.o: Mixer.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/SDL -c Mixer.c -o Mixer.o

VideoBuffer.o: VideoBuffer.c
	$(CC) $(CFLAGS) $(DEBUG) -c VideoBuffer.c -o VideoBuffer.o

MediaDecoder.o: MediaDecoder.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/SDL -c MediaDecoder.c -o MediaDecoder.o
	
MediaPlayer.o: MediaPlayer.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/SDL -c MediaPlayer.c -o MediaPlayer.o

mpGLUpdate.o: mpGLUpdate.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/GL -c mpGLUpdate.c -o mpGLUpdate.o

MPPool.o: MPPool.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/SDL -c MPPool.c -o MPPool.o

# fast_memcpy.o: fast_memcpy.cpp
# 	$(CC) fast_memcpy.cpp -o fast_memcpy.o

libMPPool.so.1: Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o
	$(CC) $(DEBUG) -L/usr/local/lib -shared -Wl,-soname,libMPPool.so.1 -lpthread -lGL -lGLEW -lvorbis -logg -ltheora -lSDL -o libMPPool.so.1.0 Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o -lc

totest.o: totest.c
	$(CC) $(CFLAGS) $(DEBUG) -I/usr/local/include/SDL -c totest.c -o totest.o

totest: totest.o Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o
	$(CC) $(DEBUG) -L/usr/local/lib -lpthread -lGL -lGLEW -lvorbis -logg -ltheora -lSDL -o totest Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o totest.o
