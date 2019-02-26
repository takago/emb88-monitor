MPU = atmega88pa
F_CPU = 8000000UL
CC = avr-gcc
CFLAGS = -mmcu=${MPU} -W -Wall -Werror-implicit-function-declaration -DF_CPU=${F_CPU} -Os -g2
CFLAGS += -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums
CFLAGS += -fdiagnostics-color 
LDFLAGS = -mmcu=${MPU}

MONI_PATH0 = /usr/local/bin
MONI_PATH1 = /usr/local/lib/avr/lib

all: onchip-monitor/onchip_mon.o

install: onchip-monitor/onchip_mon.o
	mkdir -p ${MONI_PATH1}
	cp onchip-monitor/onchip_mon.o ${MONI_PATH1}
	cp emb88-monitor.py ${MONI_PATH0}/emb88-monitor
	chmod +x  ${MONI_PATH0}/emb88-monitor

clean:
	rm onchip-monitor/onchip_mon.o

uninstall:
	rm ${MONI_PATH1}/onchip_mon.o
	rm ${MONI_PATH0}/emb88-monitor

%.o:    %.c Makefile
	${CC}  -c  $< -o $@ ${CFLAGS}
