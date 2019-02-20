import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, Pango

import binascii

class EntryWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="EMB88 Monitor -- Takago Lab. --")
        self.timeout_id = None

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        reg_names=[
            [{'name':'DDRB','adr':0x24},
             {'name':'DDRC','adr':0x27},
             {'name':'DDRD','adr':0x2a},
            ],
            [{'name':'PORTB','adr':0x25},
             {'name':'PORTC','adr':0x28},
             {'name':'PORTD','adr':0x2b}
            ],
            [{'name':'PINB','adr':0x23},
             {'name':'PINC','adr':0x26},
             {'name':'PIND','adr':0x29}
            ],
            [{'name':'PCMSK2','adr':0x6d},
             {'name':'PCMSK1','adr':0x6c},
             {'name':'PCMSK0','adr':0x6b},
             {'name':'PCICR','adr':0x68},
             {'name':'PCIFR','adr':0x3b},
            ],
            [{'name':'TCNT2','adr':0xb2},
             {'name':'OCR2B','adr':0xb4},
             {'name':'OCR2A','adr':0xb3},
             {'name':'TCCR2B','adr':0xb1},
             {'name':'TCCR2A','adr':0xb0},
             {'name':'TIFR2','adr':0x37},
             {'name':'TIMSK2','adr':0x70},
            ],
            [{'name':'TCNT1H','adr':0x85},
             {'name':'OCR1BH','adr':0x8b},
             {'name':'OCR1AH','adr':0x89},
             {'name':'TCCR1C','adr':0x82},
            ],
            [{'name':'TCNT1L','adr':0x84},
             {'name':'OCR1BL','adr':0x8a},
             {'name':'OCR1AL','adr':0x88},
             {'name':'TCCR1B','adr':0x81},
             {'name':'TCCR1A','adr':0x80},
             {'name':'TIFR1','adr':0x36},
             {'name':'TIMSK1','adr':0x6f},
            ],
            [{'name':'TCNT0','adr':0x46},
             {'name':'OCR0B','adr':0x48},
             {'name':'OCR0A','adr':0x47},
             {'name':'TCCR0B','adr':0x45},
             {'name':'TCCR0A','adr':0x44},
             {'name':'TIFR0','adr':0x35},
             {'name':'TIMSK0','adr':0x6e},
            ],
            ]

        self.entry={}
        for xx in reg_names:
            hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            vbox.pack_start(hseparator, True, True, 0)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            vbox.pack_start(hbox, True, True, 0)
            for x in xx:
                reg_name=x['name']
                reg_adr=x['adr']
                lbl = Gtk.Label(reg_name)
                lbl.modify_font(Pango.FontDescription('Dejavu Sans Mono 16'))
                lbl.set_width_chars(7)
                hbox.pack_start(lbl, False, False, 0)
                self.entry[reg_name]=Gtk.Entry()
                self.entry[reg_name].adr=reg_adr # オブジェクトに値を持たせる
                self.entry[reg_name].name=reg_name # オブジェクトに値を持たせる
                self.entry[reg_name].set_text('UU')
                self.entry[reg_name].set_max_length(2)
                self.entry[reg_name].set_width_chars(2)
                self.entry[reg_name].modify_font(Pango.FontDescription('Dejavu Sans Mono 20'))
                self.entry[reg_name].connect("key-release-event", self.on_key_release)
                self.entry[reg_name].connect("button-release-event", self.on_button_release)
                hbox.pack_start(self.entry[reg_name], False, False, 0)

    def on_key_release(self, widget, ev, data=None):
        if ev.keyval == Gdk.KEY_Return:
            #print(widget.name)
            #print(widget.adr)
            #print(widget.get_text())
            tmp1 = widget.adr
            tmp2 = int( widget.get_text(), 16)
            msg = tmp1.to_bytes(1,'big')+b'\x01'+tmp2.to_bytes(1,'big')
            print(binascii.hexlify(msg))
            # ここで送信する★★
        if ev.keyval == Gdk.KEY_Tab:
            print('ここで更新')
        if ev.keyval == Gdk.KEY_Up:
            print('ここで更新')
        if ev.keyval == Gdk.KEY_Down:
            print('ここで更新')
        if ev.keyval == 65056: ## Shift TAB
            print('[SHIFT+TAB]')
        print(ev.keyval)

    def on_button_release(self, widget, ev, data=None):
        #print(widget.name)
        #print(widget.adr)
        #print(widget.get_text())
        tmp1 = widget.adr
        msg = tmp1.to_bytes(1,'big')+b'\x00'
        print(binascii.hexlify(msg))
        # ここで受信したバイトデータをGUIに書く★★

win = EntryWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()