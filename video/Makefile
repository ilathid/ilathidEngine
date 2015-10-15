CC=cc
CFLAGS=-fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -g2 -Wformat
DEPS = MediaPlayer.h alibrary.h timehelper.h packetbuffer.h

.PHONY: all
all:  libMPPool.so.1

Mixer.o: Mixer.c
	cc $(CFLAGS) -I/usr/local/include/SDL -c Mixer.c -o Mixer.o

VideoBuffer.o: VideoBuffer.c
	cc $(CFLAGS) -c VideoBuffer.c -o VideoBuffer.o

MediaDecoder.o: MediaDecoder.c
	cc $(CFLAGS) -I/usr/local/include/SDL -c MediaDecoder.c -o MediaDecoder.o
	
MediaPlayer.o: MediaPlayer.c
	cc $(CFLAGS) -I/usr/local/include/SDL -c MediaPlayer.c -o MediaPlayer.o

mpGLUpdate.o: mpGLUpdate.c
	cc $(CFLAGS) -I/usr/local/include/GL -c mpGLUpdate.c -o mpGLUpdate.o

MPPool.o: MPPool.c
	cc $(CFLAGS) -I/usr/local/include/SDL -c MPPool.c -o MPPool.o

libMPPool.so.1: Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o
	cc -shared -Wl,-soname,libMPPool.so.1 -o libMPPool.so.1.0 Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o -lc
