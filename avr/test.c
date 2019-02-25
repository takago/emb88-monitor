#include <avr/io.h>	// レジスタ名や，レジスタのビット名の定義
#include <avr/wdt.h>	// ウォッチドックタイマ
#include <avr/interrupt.h>	// 割り込み

volatile unsigned char move_left = 1;	// 1:左循環シフト, 0:右循環シフト

ISR(TIMER1_COMPA_vect)	// 50msごとにタイマ割込み
{
	unsigned char sw;

	//スイッチの状態に応じて，循環シフトの方向を切り替える
	sw = (~PINC >> 4) & 3;
	if (sw == 1) {
		move_left = 1;
	}
	if (sw == 2) {
		move_left = 0;
	}


	// マトリクスLEDの表示更新，音程の変更
	if (move_left) {
		PORTB = (PORTB << 1) | ((PORTB >> 7) & 1);
		OCR2A++;
	}
	else {
		PORTB = (PORTB >> 1) | ((PORTB & 1) << 7);
		OCR2A--;
	}
    OCR2A|=0x80;        
}

int main()
{
	// ポートB,C,Dの入出力方向を設定する
	DDRB = 0xFF;
	DDRC = 0x0F;
	DDRD = 0xFE;

	// ポートB,C,Dごとの出力値やプルアップの設定
	PORTB = 0x07;
	PORTC = 0x30;
	PORTD = 0x00;

	// タイマ2の設定（音程）
	TCNT2 = 0;
	OCR2A = 150;
	TCCR2A = 0x12;
	TCCR2B = 0x04;

	// タイマ1の設定
	TCNT1 = 0;
	OCR1A = 390;
	TCCR1A = 0x00;
	TCCR1B = 0x0D;
	TIMSK1 = _BV(OCIE1A);	// タイマ割り込み有効化

	sei();	// システム全体の割り込み許可

	for (;;) {	// イベントループ
		wdt_reset();	// ウォッチドッグタイマのクリア
	}
	return 0;
}
