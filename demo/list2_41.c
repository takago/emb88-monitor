#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>

volatile unsigned char buff[16], stat;
#define STEP 5	// 照明環境によって調整する

ISR(ADC_vect)
{
	TIFR1 = _BV(OCF1B);	// トリガ用のフラグのクリア
	PORTB = 0xFF >> (8 - ((1024 - ADC) >> STEP));
}

int main(void)
{
	// LED および SW1,2 のポート設定
	DDRD = 0xFE;
	DDRC = 0x0F;
	DDRB = 0xFF;

	PORTD = 0x00;
	PORTC = 0x00;
	PORTB = 0x00;

	OCR1A = 49999;
	OCR1B = 0;
	TCCR1A = 0;
	TCCR1B = 0xA;	// PS=8, CTC, 50msごとにCompBフラグが立つ   

	ADMUX = _BV(REFS0);	// REF電圧(AVCC)
	ADMUX |= 0x05;	// ADC入力をADC5に設定
	ADCSRB = 5;	// 自動トリガ(TIMER1_CompBフラグ)
	ADCSRA = _BV(ADEN) | 0x7 | _BV(ADATE) | _BV(ADIE);
	ADCSRA |= _BV(ADSC);	// ADIFクリアと変換開始

	sei();

	for (;;) {
		wdt_reset();
	}
	return 0;
}
