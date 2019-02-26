# EMB88 Monitor
# Author: Daisuke Takago, Yuta Kobayashi (Takago Lab.2019)

# メモ：
# 16bitレジスタの書き込みは，上位1，下位0の順
# 16bitレジスタの読み出しは，下位0・上位1の順に読み出すことが決まっている

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Pango, GObject

import binascii
import serial
import sys
import time

update_interval_ms=50
col=[Gdk.Color(0, 0x7a*256,0xbb *256), Gdk.Color(60000, 60000, 60000), Gdk.Color(20000, 20000, 20000)]

class EntryWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="EMB88 Monitor (TAKAGO_LAB. 2019)")
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
             {'name':'OCR0B','adr':[0x48],'wr':True},
             {'name':'OCR0A','adr':[0x47],'wr':True},
             {'name':'TCCR0B','adr':[0x45],'wr':True},
             {'name':'TCCR0A','adr':[0x44],'wr':True},
             {'name':'TIFR0','adr':[0x35],'wr':True},
             {'name':'TIMSK0','adr':[0x6e],'wr':True},
            ],
            [{'name':'TCNT2','adr':[0xb2],'wr':True},
             {'name':'OCR2B','adr':[0xb4],'wr':True},
             {'name':'OCR2A','adr':[0xb3],'wr':True},
             {'name':'TCCR2B','adr':[0xb1],'wr':True},
             {'name':'TCCR2A','adr':[0xb0],'wr':True},
             {'name':'TIFR2','adr':[0x37],'wr':True},
             {'name':'TIMSK2','adr':[0x70],'wr':True},
            ],
            [{'name':'\n(4) 16bit timer'}],
            [{'name':'TCNT1','adr':[0x84,0x85],'wr':True}, # TCNT1H:0x85, TCNT1L:0x84
             {'name':'OCR1B','adr':[0x8a,0x8b],'wr':True}, # OCR1BH:0x8B, OCR1BL:0x8A
             {'name':'OCR1A','adr':[0x88,0x89],'wr':True}, # OCR1AH:0x89, OCR1AL:0x88
             {'name':'TCCR1C','adr':[0x82],'wr':True},
             {'name':'TCCR1B','adr':[0x81],'wr':True},
             {'name':'TCCR1A','adr':[0x80],'wr':True},
             {'name':'TIFR1','adr':[0x36],'wr':True},
             {'name':'TIMSK1','adr':[0x6f],'wr':True},
            ],
            [{'name':'\n(5) ADC'}],
            [{'name':'ADC','adr':[0x78,0x79],'wr':False}, # ADCH:0x79, ADCL:0x78
             {'name':'DIDR0','adr':[0x7e],'wr':True},
             {'name':'ADMUX','adr':[0x7c],'wr':True},
             {'name':'ADCSRB','adr':[0x7b],'wr':True},
             {'name':'ADCSRA','adr':[0x7c],'wr':True},
            ],
            [{'name':''}],
            ]

        self.entry={}
        for xx in reg_names:
#            hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
#            vbox.pack_start(hseparator, True, True, 0)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            vbox.pack_start(hbox, True, True, 0)
            for x in xx:
                reg_name=x['name']
                lbl = Gtk.Label(reg_name)
                lbl.modify_font(Pango.FontDescription('Inconsolata 20'))
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
                self.entry[reg_name].set_text('UU'*N)
                self.entry[reg_name].set_max_length(2*N)
                self.entry[reg_name].set_width_chars(2*N)
                self.entry[reg_name].modify_font(Pango.FontDescription('Inconsolata 24'))
                if wr==True:
                    self.entry[reg_name].modify_bg(Gtk.StateType.NORMAL, col[0])
                else:
                    self.entry[reg_name].modify_bg(Gtk.StateType.NORMAL, col[2])
                self.entry[reg_name].modify_fg(Gtk.StateType.NORMAL, col[1])
                self.entry[reg_name].connect("key-release-event", self.on_key_release)
                self.entry[reg_name].connect("button-release-event", self.on_button_release)
                hbox.pack_start(self.entry[reg_name], False, False, 0)
        GObject.timeout_add(1000, self.mytimer)

    def mytimer(self):
        GObject.timeout_add(update_interval_ms, self.mytimer)
        for k,widget in self.entry.items():
            if widget.auto_update==False:
                continue
            val=self.read_reg( widget.adr, widget.N)
            if widget.N==2:
                widget.set_text('%04X' % val)
            else:
                widget.set_text('%02X' % val)

    def on_key_release(self, widget, ev, data=None):
        #print(ev.keyval)
        #print(widget.name)
        #print(widget.adr)
        #print(widget.get_text())

        if widget.get_editable()==False:
            return

        # [ESC]で入力モードを抜ける
        if ev.keyval == Gdk.KEY_Escape:
            widget.auto_update=True
            widget.modify_bg(Gtk.StateType.NORMAL, col[0])
            widget.modify_fg(Gtk.StateType.NORMAL, col[1])

        # [ENTER]で書き込みモードのON/OFF
        if ev.keyval == Gdk.KEY_Return:
            if widget.auto_update==False:
                widget.auto_update=True
                widget.modify_bg(Gtk.StateType.NORMAL, col[0])
                widget.modify_fg(Gtk.StateType.NORMAL, col[1])
                val = int( widget.get_text(), 16)
                self.write_reg( widget.adr, val, widget.N )
            else:
                widget.auto_update=False
                widget.modify_fg(Gtk.StateType.NORMAL, col[0])
                widget.modify_bg(Gtk.StateType.NORMAL, col[1])

        # [DEL]や[BS]で消去
        if ev.keyval == Gdk.KEY_Delete or ev.keyval == Gdk.KEY_BackSpace:
            if widget.auto_update==True:
                widget.auto_update=False
                widget.modify_fg(Gtk.StateType.NORMAL, col[0])
                widget.modify_bg(Gtk.StateType.NORMAL, col[1])
                widget.set_text('')

    def on_button_release(self, widget, ev, data=None):
            if widget.get_editable()==False:
                return
            if widget.auto_update==False:
                widget.auto_update=True
                widget.modify_bg(Gtk.StateType.NORMAL, col[0])
                widget.modify_fg(Gtk.StateType.NORMAL, col[1])
            else:
                widget.auto_update=False
                widget.modify_fg(Gtk.StateType.NORMAL, col[0])
                widget.modify_bg(Gtk.StateType.NORMAL, col[1])

    def read_reg(self, adr, N):
        sdev.write(b'\x00')
        sdev.flush()
        #time.sleep(0.01)
        sdev.write(adr.to_bytes(1,'big'))
        sdev.flush()
        #time.sleep(0.01)
        c = int.from_bytes(sdev.read(N),'little')
        return c

    def write_reg(self, adr, val, N):
        sdev.write(b'\x01')
        sdev.flush()
        #time.sleep(0.01)
        sdev.write(adr.to_bytes(1,'big'))
        sdev.flush()
        #time.sleep(0.01)
        sdev.write(val.to_bytes(N,'big'))
        sdev.flush()
        #time.sleep(0.01)

win = EntryWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()

sdev = serial.Serial('/dev/emb88',38400, timeout=0.05)
time.sleep(0.1)
# buffer flush
sdev.reset_input_buffer()
sdev.reset_output_buffer()
time.sleep(0.1)
Gtk.main()
