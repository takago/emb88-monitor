#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

volatile unsigned char led[8] =
  { 0x00, 0x57, 0x55, 0x77, 0x11, 0x17, 0x00, 0xFF };
volatile unsigned char mv_flag;

void update_led();

ISR(TIMER0_COMPA_vect)	// 定期的な処理を記述
{
	static int cnt;
	cnt++;
	if (cnt == 100) {
		cnt = 0;
		mv_flag = 1;	// 200msごとにセット
	}
	update_led();	// ダイナミック点灯    
}

void update_led()
{
	static unsigned char sc = 0xFE;
	static unsigned char scan = 0;

	PORTB = 0;	// 残像対策
	sc = (sc << 1) | (sc >> 7);
	PORTD = (PORTD & 0x0F) | (sc & 0xF0);	// 上位4ビット書き換え           
	PORTC = (PORTC & 0xF0) | (sc & 0x0F);	// 下位4ビット書き換え           
	scan = (scan + 1) & 7;
	PORTB = led[scan];
}

int main()
{
	unsigned char n;

	DDRB = 0xFF;
	DDRC = 0x0F;
	DDRD = 0xFE;

	PORTB = 0x00;
	PORTC = 0x30;
	PORTD = 0x00;

	// タイマ設定
	TCNT0 = 0;
	OCR0A = 249;
	TCCR0A = 2;
	TCCR0B = 3;
	TIMSK0 |= _BV(OCIE0A);	// コンペアマッチA割り込み(2ms)

	sei();
	for (;;) {
		wdt_reset();
		if (mv_flag == 1) {
			mv_flag = 0;
			for (n = 0; n <= 7; n++) {
				led[n] = (led[n] << 1) | (led[n] >> 7);
			}
		}
	}
	return 0;
}
