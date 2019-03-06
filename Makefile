MPU = atmega88pa
F_CPU = 8000000UL
CC = avr-gcc
CFLAGS = -mmcu=${MPU} -W -Wall -Werror-implicit-function-declaration -DF_CPU=${F_CPU} -Os -g2
CFLAGS += -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums
CFLAGS += -fdiagnostics-color 
LDFLAGS = -mmcu=${MPU}

OBJ = onchip_mon.o
MONI_PATH0 = /usr/local/bin
MONI_PATH1 = /usr/local/lib/avr/lib

all: ${OBJ}

install: ${OBJ}
	mkdir -p ${MONI_PATH1}
	cp $< ${MONI_PATH1}
	cp e8mon.py ${MONI_PATH0}/e8mon
	chmod +x  ${MONI_PATH0}/e8mon
	cp e8mon.desktop /usr/local/share/applications/

clean: ${OBJ}
	rm -f $<

uninstall:
	rm -f ${MONI_PATH1}/onchip_mon.o
	rm -f ${MONI_PATH0}/e8mon
	rm -f /usr/local/share/applications/e8mon.desktop

%.o:    %.c Makefile
	${CC}  -c  $< -o $@ ${CFLAGS}
