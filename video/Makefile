CC=cc
CFLAGS=-fno-strict-aliasing -O3 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -g2 -Wformat
DEPS = MediaPlayer.h alibrary.h timehelper.h packetbuffer.h

.PHONY: all
all:  libMPPool.so.1 totest

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
	cc -L/usr/local/lib -shared -Wl,-soname,libMPPool.so.1 -lpthread -lGL -lGLEW -lvorbis -logg -ltheora -lSDL -o libMPPool.so.1.0 Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o -lc

totest.o: totest.c
	cc $(CFLAGS) -I/usr/local/include/SDL -c totest.c -o totest.o

totest: totest.o Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o
	cc -L/usr/local/lib -lpthread -lGL -lGLEW -lvorbis -logg -ltheora -lSDL -o totest Mixer.o VideoBuffer.o MediaDecoder.o MediaPlayer.o MPPool.o mpGLUpdate.o totest.o
