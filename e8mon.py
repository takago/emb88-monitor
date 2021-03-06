#! /usr/bin/python3

# EMB88 Monitor
# Author: Daisuke Takago, Yuta Kobayashi (Takago Lab.2019)

# メモ：
# 16bitレジスタの書き込みは，上位1，下位0の順
# 16bitレジスタの読み出しは，下位0・上位1の順に読み出すことが決まっている

# Entryの背景色が塗られない場合はデスクトップのテーマを変えればOK

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Pango, GObject

import serial
import time
import signal

serial_dev='/dev/emb88'
serial_baud=38400

fnt='Inconsolata 12'

def reset_emb88(restart):
    # DTR reset
    sdev.dtr=False # Low
    time.sleep(0.1)
    sdev.dtr=True  # High
    while restart:
        time.sleep(0.1)
        if sdev.read(1)==b'=':
            sdev.write(b'/') # Send START Signal
            sdev.flush()
            time.sleep(0.1)
            break
    clear_sdev_buff()

def clear_sdev_buff():
    # print(sdev.in_waiting, sdev.out_waiting) # バッファの使用状況
    while sdev.in_waiting != 0:
        sdev.reset_input_buffer()
        time.sleep(0.1)

    while sdev.out_waiting != 0:
        # print(sdev.out_waiting)
        sdev.reset_output_buffer() #### FIX ME: マイコンのリセットボタンを押すと何故か4秒ほどかかる(VMでは問題なし)
        time.sleep(0.1)

def setup_serial():
    global sdev
    sdev = serial.Serial( serial_dev, serial_baud, timeout=0.1, write_timeout=0.1 )
    reset_emb88(True)

class MonitorWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title='EMB88 Monitor')
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        reg_names=[
            [{'name':'\n(1) GPIO'}],
            [{'name':'DDRD','adr':[0x2a],'wr':True},
            {'name':'DDRC','adr':[0x27],'wr':True},
            {'name':'DDRB','adr':[0x24],'wr':True},
            ],
            [{'name':'PORTD','adr':[0x2b],'wr':True},
             {'name':'PORTC','adr':[0x28],'wr':True},
             {'name':'PORTB','adr':[0x25],'wr':True},
            ],
            [{'name':'PIND','adr':[0x29],'wr':False},
             {'name':'PINC','adr':[0x26],'wr':False},
             {'name':'PINB','adr':[0x23],'wr':False},
            ],
            [{'name':'\n(2) Pin change interrupt'}],
            [{'name':'PCMSK2','adr':[0x6d],'wr':True},
             {'name':'PCMSK1','adr':[0x6c],'wr':True},
             {'name':'PCMSK0','adr':[0x6b],'wr':True},
             {'name':'PCICR','adr':[0x68],'wr':True},
             {'name':'PCIFR','adr':[0x3b],'wr':True},
            ],
            [{'name':'\n(3) 8bit timers'}],
            [{'name':'TCNT0','adr':[0x46],'wr':True},
             {'name':'OCR0A','adr':[0x47],'wr':True},
             {'name':'OCR0B','adr':[0x48],'wr':True},
             {'name':'TCCR0A','adr':[0x44],'wr':True},
             {'name':'TCCR0B','adr':[0x45],'wr':True},
             {'name':'TIMSK0','adr':[0x6e],'wr':True},
             {'name':'TIFR0','adr':[0x35],'wr':True},
            ],
            [{'name':'TCNT2','adr':[0xb2],'wr':True},
             {'name':'OCR2A','adr':[0xb3],'wr':True},
             {'name':'OCR2B','adr':[0xb4],'wr':True},
             {'name':'TCCR2A','adr':[0xb0],'wr':True},
             {'name':'TCCR2B','adr':[0xb1],'wr':True},
             {'name':'TIMSK2','adr':[0x70],'wr':True},
             {'name':'TIFR2','adr':[0x37],'wr':True},
            ],
            [{'name':'\n(4) 16bit timer'}],
            [{'name':'TCNT1','adr':[0x84,0x85],'wr':True}, # TCNT1H:0x85, TCNT1L:0x84
             {'name':'OCR1A','adr':[0x88,0x89],'wr':True}, # OCR1AH:0x89, OCR1AL:0x88
             {'name':'OCR1B','adr':[0x8a,0x8b],'wr':True}, # OCR1BH:0x8B, OCR1BL:0x8A
             {'name':'TCCR1A','adr':[0x80],'wr':True},
             {'name':'TCCR1B','adr':[0x81],'wr':True},
             #{'name':'TCCR1C','adr':[0x82],'wr':True},
             {'name':'TIMSK1','adr':[0x6f],'wr':True},
             {'name':'TIFR1','adr':[0x36],'wr':True},
            ],
            [{'name':'\n(5) ADC'}],
            [{'name':'ADC','adr':[0x78,0x79],'wr':False}, # ADCH:0x79, ADCL:0x78
             {'name':'DIDR0','adr':[0x7e],'wr':True},
             {'name':'ADMUX','adr':[0x7c],'wr':True},
             {'name':'ADCSRA','adr':[0x7c],'wr':True},
             {'name':'ADCSRB','adr':[0x7b],'wr':True},
            ],
            ]

        self.entry={}
        for xx in reg_names:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            vbox.pack_start(hbox, True, True, 0)

            for x in xx:
                reg_name=x['name']
                lbl = Gtk.Label(reg_name)
                lbl.modify_font(Pango.FontDescription(fnt))
                lbl.set_width_chars(7)
                lbl.set_xalign(0.9) # 右寄りでラベル表示
                hbox.pack_start(lbl, False, False, 0)
                if len(x)==1:
                    continue
                reg_adr=x['adr']
                wr=x['wr']
                N=len(reg_adr)
                self.entry[reg_name]=Gtk.Entry()
                self.entry[reg_name].name=reg_name # オブジェクトに値を持たせる
                self.entry[reg_name].adr=reg_adr[0] # オブジェクトに値を持たせる
                self.entry[reg_name].N=N # オブジェクトに値を持たせる
                self.entry[reg_name].set_editable(wr)
                self.entry[reg_name].auto_update=True
                self.entry[reg_name].radix=16 # 基数:2,8,16
                self.entry[reg_name].set_text('UU'*N)
                self.entry[reg_name].set_max_length(2*N)
                self.entry[reg_name].set_width_chars(2*N)
                self.entry[reg_name].modify_font(Pango.FontDescription(fnt))
                self.entry[reg_name].connect("key-press-event", self.on_key_press) # キーボードイベント
                self.entry[reg_name].connect("button-press-event", self.on_button_press) # マウスボタンイベント
                hbox.pack_start(self.entry[reg_name], False, False, 0)

        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(hseparator, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        vbox.pack_start(hbox, True, True, 0)

        btn = Gtk.Button.new_with_label("RESET EMB-88")
        btn.modify_font(Pango.FontDescription(fnt))
        btn.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#DDD'))
        btn.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#000'))
        # btn.modify_bg(Gtk.StateFlags.ACTIVE, Gdk.color_parse('#C35'))
        # btn.modify_fg(Gtk.StateFlags.ACTIVE, Gdk.color_parse('#FFF'))
        btn.modify_bg(Gtk.StateFlags.PRELIGHT, Gdk.color_parse('#C35'))
        btn.modify_fg(Gtk.StateFlags.PRELIGHT, Gdk.color_parse('#FFF'))
        btn.name='rst'
        btn.connect("clicked", self.on_push)
        vbox.pack_start(btn, False, False, 0)

        self.lbl = Gtk.Label('')
        self.lbl.modify_font(Pango.FontDescription(fnt))
        self.lbl.set_xalign(1) # 右寄りでラベル表示
        vbox.pack_start(self.lbl, False, False, 0)

        setup_serial()

        # タイマースタート
        GObject.timeout_add(100, self.mytimer)
        self.t0=time.time()

    def mytimer(self):
        t1=time.time()
        t_diff=t1-self.t0
        self.t0=t1
        lbl_txt = 'UPDATE[ms]:%-4d' % (t_diff*1000)
        self.lbl.set_text(lbl_txt+' DEV:'+serial_dev+' BAUD:'+str(serial_baud)+' [Takago Lab.2019]')

        for k,widget in self.entry.items():
            if widget.auto_update==False:
                widget.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#FFF'))
                widget.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#00F'))
                continue
            val=self.read_reg( widget.adr, widget.N)
            if widget.radix==16:
                if widget.N==2:
                    dat='%04X' % val
                else:
                    dat='%02X' % val
            elif widget.radix==2:
                if widget.N==2:
                    dat=format(val,'016b')
                else:
                    dat=format(val,'08b')
            else:
                if widget.N==2:
                    dat='%5d' % val
                else:
                    dat='%3d' % val

            widget.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#000'))
            if widget.get_editable()==False:
                if dat!=widget.get_text():
                    widget.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#F68'))
                else:
                    widget.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#999'))
            else:
                if dat!=widget.get_text():
                    widget.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#9CD'))
                else:
                    widget.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#DDD'))
            widget.set_text(dat)
        self.timer_id = GObject.timeout_add(10, self.mytimer) # 10ms後に呼び出す

    def on_key_press(self, widget, ev, data=None):
        #print(ev.keyval)
        #print(widget.name)
        #print(widget.adr)
        #print(widget.get_text())

        if widget.get_editable()==False:
            return

        # [ESC]で入力モードを抜ける
        if ev.keyval == Gdk.KEY_Escape:
            widget.auto_update=True

        # [ENTER]で書き込みモードのON/OFF
        if ev.keyval == Gdk.KEY_Return:
            if widget.auto_update==False:
                widget.auto_update=True
                if widget.radix==16:
                    val = int( widget.get_text(), 16)
                elif widget.radix==2:
                    val = int( widget.get_text(), 2)
                else:
                    val = int( widget.get_text(), 10)
                self.write_reg( widget.adr, val, widget.N )
            else:
                widget.auto_update=False

        # [DEL]や[BS]で消去
        if ev.keyval == Gdk.KEY_Delete or ev.keyval == Gdk.KEY_BackSpace:
            if widget.auto_update==True:
                widget.auto_update=False
                widget.set_text('')

    def on_push(self, widget):
        if widget.name == 'rst':
            GObject.source_remove(self.timer_id) # タイマ停止（レジスタアクセスが止まる）
            reset_emb88(True)
            self.timer_id = GObject.timeout_add(10, self.mytimer) # タイマ再開(レジスタアクセスが始まる)

    def on_button_press(self, widget, ev, data=None):
            # print(ev.button)
            if ev.button==1:
                widget.auto_update = not widget.auto_update
                return
            if ev.button==2:
                if widget.radix==2:
                    widget.radix=16
                    widget.set_max_length(widget.N*2)
                    widget.set_width_chars(widget.N*2)
                elif widget.radix==16:
                    widget.radix=10
                    widget.set_max_length(widget.N*2+1)
                    widget.set_width_chars(widget.N*2+1)
                else:
                    widget.radix=2
                    widget.set_max_length(widget.N*8)
                    widget.set_width_chars(widget.N*8)
                return
            if widget.get_editable()==False:
                return

    def read_reg(self, adr, N):
        try:
            sdev.write(b'\x00')
            sdev.write(adr.to_bytes(1,'big'))
            sdev.flush()
            return int.from_bytes( sdev.read(N), 'little')
        except:# タイムアウトなどが起きたときは
            clear_sdev_buff()
            return 0


    def write_reg(self, adr, val, N):
        try:
            sdev.write(b'\x01')
            sdev.write(adr.to_bytes(1,'big'))
            sdev.write(val.to_bytes(N,'big'))
            sdev.flush()
        except: # タイムアウトなどが起きたときは
            clear_sdev_buff()

win = MonitorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) # 端末からのC-cで終了出来るようにする
Gtk.main()
