CC=cc
CFLAGS=-fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -g2 -Wformat
DEPS = MediaPlayer.h alibrary.h timehelper.h packetbuffer.h

test: test.o packetbuffer.o alibrary.o timehelper.o MediaPlayer.o
	$(CC) $(CFLAGS) test.o packetbuffer.o alibrary.o timehelper.o MediaPlayer.o -L. -L/usr/local/lib -lm -lavutil -lavformat -lavcodec -lswscale -lao -lpthread -lrt -o test

MediaPlayer.o: MediaPlayer.c
	$(CC) $(CFLAGS) -c MediaPlayer.c -o MediaPlayer.o

timehelper.o: timehelper.c
	$(CC) $(CFLAGS) -c timehelper.c -o timehelper.o
	
alibrary.o: alibrary.c
	$(CC) $(CFLAGS) -c alibrary.c -o alibrary.o
	
packetbuffer.o: packetbuffer.c
	$(CC) $(CFLAGS) -c packetbuffer.c -o packetbuffer.o
	
test.o: test.c
	$(CC) $(CFLAGS) -c test.c -o test.o

clean:
	rm -f test test.o packetbuffer.o alibrary.o timehelper.o MediaPlayer.o
