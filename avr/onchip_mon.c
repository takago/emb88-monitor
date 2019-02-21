#include<avr/io.h>
#include <avr/interrupt.h>

unsigned int n = 0;
unsigned int c[4];
unsigned int *p;
int flag = 0;
/* 割り込み処理未定義時にハングアップするのを防止 */
__attribute__((weak)) ISR(INT0_vect){}
__attribute__((weak)) ISR(INT1_vect){}
__attribute__((weak)) ISR(PCINT0_vect){}
__attribute__((weak)) ISR(PCINT1_vect){}
__attribute__((weak)) ISR(PCINT2_vect){}
__attribute__((weak)) ISR(WDT_vect){}
__attribute__((weak)) ISR(TIMER0_COMPA_vect){}
__attribute__((weak)) ISR(TIMER0_COMPB_vect){}
__attribute__((weak)) ISR(TIMER0_OVF_vect){}
__attribute__((weak)) ISR(TIMER1_CAPT_vect){}
__attribute__((weak)) ISR(TIMER1_COMPA_vect){}
__attribute__((weak)) ISR(TIMER1_COMPB_vect){}
__attribute__((weak)) ISR(TIMER1_OVF_vect){}
__attribute__((weak)) ISR(TIMER2_COMPA_vect){}
__attribute__((weak)) ISR(TIMER2_COMPB_vect){}
__attribute__((weak)) ISR(TIMER2_OVF_vect){}
__attribute__((weak)) ISR(SPI_STC_vect){}
__attribute__((weak)) ISR(USART_UDRE_vect){}
__attribute__((weak)) ISR(USART_TX_vect){}
__attribute__((weak)) ISR(ADC_vect){}
__attribute__((weak)) ISR(EE_READY_vect){}
__attribute__((weak)) ISR(ANALOG_COMP_vect){}
__attribute__((weak)) ISR(TWI_vect){}
__attribute__((weak)) ISR(SPM_Ready_vect){}

ISR(USART_RX_vect) //__attribute__((weak))を付けると動かない
{
    static unsigned int stat = 0;
    static unsigned int rw;
    static unsigned int *p; // IOレジスタのアドレス
    
    switch(stat){
    case 0: // 初期状態
        rw = UDR0; // 0:読み出し命令，1:書き込み命令
        stat=1;
        return;
    case 1: // IOレジスタ情報の受信待ち
        p = UDR0;        // レジスタアドレス取得  
        if(rw == 0){  // 読み出し処理のときは　
            UDR0 = *p;  // IOレジスタの値を取り出して送信
            stat=0;
            return;   
        }
        stat=2;
        return;
    case 2:  // 書き込みデータの到着待ちの状態
        *p = UDR0;  // IOレジスタに書き込み
        stat=0;
        return;
    }
}

/* main()の前に自動的に実行する */
__attribute__((constructor)) void moni()
{
    /* USART設定 */
    UCSR0C = 3 << UCSZ00;
    UBRR0 = 12;             // 38400bps
    UCSR0B |= 1 << RXCIE0;	// 受信割り込み有効
    UCSR0B |= 1 << TXEN0;	// 送信器使用
    UCSR0B |= 1 << RXEN0;	// 受信器使用

    sei();	// 割り込み受付開始
}
