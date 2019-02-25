# ここにビルドに必要なCソースファイル名を並べる
# （例： SRCS = src1.c src2. src3.c と書く）

SRCS = list2_22.c

# モニタプログラムを使うときは1にする（ユーザプログラムでシリアル通信を行うときは0にすること）
MONITOR = 1

#--------------------------------------------
# ここから下は理由がない限り書き換えない

ifeq (${MONITOR},1)
	SRCS += onchip_mon.c
endif

# プロジェクト名にはカレントディレクトリ名を割当
PROJECT =   $(notdir $(CURDIR))

SDEV = /dev/emb88
BAUD = 38400

OBJECTS = $(SRCS:.c=.o)
MPU = atmega88pa
F_CPU = 8000000UL

MAPFILE = ${PROJECT}.map
LSSFILE = ${PROJECT}.lss
ELFFILE = ${PROJECT}.elf
HEXFILE = ${PROJECT}.hex
EEPFILE = ${PROJECT}.eep

CC = avr-gcc
CFLAGS = -mmcu=${MPU} -W -Wall -Werror-implicit-function-declaration -DF_CPU=${F_CPU} -Os -g2
#CFLAGS += -save-temps
CFLAGS += -funsigned-char -funsigned-bitfields -fpack-struct -fshort-enums
CFLAGS += -fdiagnostics-color 
#CFLAGS += -fno-tree-vrp 
LDFLAGS = -mmcu=${MPU} -Wl,-Map=${MAPFILE}

.PHONY: all clean distclean

all: clean ${HEXFILE}

${HEXFILE}: ${OBJECTS}
	avr-gcc ${LDFLAGS} ${OBJECTS} -o ${ELFFILE}
	avr-objcopy -j.text -j.data -O ihex ${ELFFILE} ${HEXFILE}
	avr-objcopy -j.eeprom --set-section-flags=.eeprom="alloc,load" --change-section-lma .eeprom=0 --no-change-warnings -O ihex ${ELFFILE} ${EEPFILE}
	avr-objdump -h -S ${ELFFILE} > ${LSSFILE}
	@echo
	@avr-size -C --mcu=${MPU} ${ELFFILE}

distclean: clean
	rm -f ${HEXFILE}

clean:
	rm -f ${OBJECTS} ${MAPFILE} ${LSSFILE} ${ELFFILE} ${EEPFILE} ${PROJECT}.[iso]

dl: all
	con2com ${SDEV} ${BAUD} ${HEXFILE} /

%.o:	%.c Makefile
	${CC}  -c  $< -o $@ ${CFLAGS}
