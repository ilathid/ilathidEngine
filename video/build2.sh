#!/bin/bash
#setenv CFLAGS "-I/usr/local/include"
#setenv LDFLAGS "-L/usr/local/lib -L./"
# python setup.py build_ext --inplace


cc -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -c MediaPlayer.c -o build/temp.freebsd-9.0-RELEASE-i386-2.7/MediaPlayer.o -g

cc -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -c timehelper.c -o build/temp.freebsd-9.0-RELEASE-i386-2.7/timehelper.o -g

cc -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -c alibrary.c -o build/temp.freebsd-9.0-RELEASE-i386-2.7/alibrary.o -g

cc -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -c packetbuffer.c -o build/temp.freebsd-9.0-RELEASE-i386-2.7/packetbuffer.o -g

cc -fno-strict-aliasing -O2 -pipe -fno-strict-aliasing -DNDEBUG -O2 -pipe -fno-strict-aliasing -fPIC -I. -I/usr/local/include -I/usr/local/include/python2.7 -c test.c -o build/temp.freebsd-9.0-RELEASE-i386-2.7/test.o -g

cc -o a.out build/temp.freebsd-9.0-RELEASE-i386-2.7/test.o build/temp.freebsd-9.0-RELEASE-i386-2.7/packetbuffer.o build/temp.freebsd-9.0-RELEASE-i386-2.7/alibrary.o build/temp.freebsd-9.0-RELEASE-i386-2.7/timehelper.o build/temp.freebsd-9.0-RELEASE-i386-2.7/MediaPlayer.o -L. -L/usr/local/lib -lavformat -lavcodec -lswscale -lao -lpthread
