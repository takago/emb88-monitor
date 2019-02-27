#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>

volatile unsigned char buff[16], stat;
#define STEP 5	// �Ɩ����ɂ���Ē�������

ISR(ADC_vect)
{
	TIFR1 = _BV(OCF1B);	// �g���K�p�̃t���O�̃N���A
	PORTB = 0xFF >> (8 - ((1024 - ADC) >> STEP));
}

int main(void)
{
	// LED ����� SW1,2 �̃|�[�g�ݒ�
	DDRD = 0xFE;
	DDRC = 0x0F;
	DDRB = 0xFF;

	PORTD = 0x00;
	PORTC = 0x00;
	PORTB = 0x00;

	OCR1A = 49999;
	OCR1B = 0;
	TCCR1A = 0;
	TCCR1B = 0xA;	// PS=8, CTC, 50ms���Ƃ�CompB�t���O������   

	ADMUX = _BV(REFS0);	// REF�d��(AVCC)
	ADMUX |= 0x05;	// ADC���͂�ADC5�ɐݒ�
	ADCSRB = 5;	// �����g���K(TIMER1_CompB�t���O)
	ADCSRA = _BV(ADEN) | 0x7 | _BV(ADATE) | _BV(ADIE);
	ADCSRA |= _BV(ADSC);	// ADIF�N���A�ƕϊ��J�n

	sei();

	for (;;) {
		wdt_reset();
	}
	return 0;
}
