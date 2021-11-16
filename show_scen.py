#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
import mod_utils
import mod_ecu
import mod_zip
from kivy.uix.widget import Widget
from mod_utils import pyren_encode
from mod_utils import clearScreen
from mod_utils import ASCIITOHEX
from kivy import base
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

fs =  mod_globals.fontSize

class MyLabel(Label):

    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
            self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'height' not in kwargs:
            fmn = 1.05
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 5
            if lines > 20: lines = 13
            if 1 > simb: lines = 2
            if fs > 20: 
                lines = lines * 1.05
                fmn = 1.5
            self.height = fmn * lines * fs
        
        if 'font_size' not in kwargs:
            self.font_size = fs
    
    def on_size(self, *args):
        if not self.canvas:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(self.bgcolor[0], self.bgcolor[1], self.bgcolor[2], self.bgcolor[3])
            Rectangle(pos=self.pos, size=self.size)

class Show_scen():

    def build(self, instance):
        layout_popup = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout_popup.bind(minimum_height=layout_popup.setter('height'))

        for i in range(0, 15):
            btn1 = Button(text=str(i), id=str(i))
            layout_popup.add_widget(btn1)

        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        layout_popup.add_widget(Button(text='CANCEL', on_press=self.stop(), size_hint=(1, None), height=80))
        root.add_widget(layout_popup)
        popup = Popup(title='Numbers', content=root, size_hint=(1, 1))
        return popup
    

class Scenarii(App):
    
    def __init__(self, **kwargs):
        self.data = kwargs['data']
        self.DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        self.ScmRoom = self.DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}

        super(Scenarii, self).__init__(**kwargs)


    def build(self):
        fs = mod_globals.fontSize
        self.header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=self.header))
        root.add_widget(MyLabel(text=self.command.scenario))
        root.add_widget(Button(text='SHOW SCEN', on_press=self.show_scen, size_hint=(1, None), height=80))
        root.add_widget(Button(text='CANCEL', on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        rot.add_widget(root)
        return rot
    
    def show_scen(self, msg):
        layout_popup = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout_popup.bind(minimum_width=layout_popup.setter('width'), minimum_height=layout_popup.setter('height'))
        layout_popup.add_widget(MyLabel(text=self.command.scenario.split('#')[1], bgcolor=(1, 0, 0, 0.3)))
        for line in self.DOMTree.toprettyxml().splitlines():
            if 'value' in line:
                layout_popup.add_widget(MyLabel(text='', height=5, bgcolor=(1, 1, 0, 0.3)))
                pa = re.compile(r'name=\"(\w+)\"\s+value=\"(\w+)\"')
                ma = pa.search( line.strip() )
                if ma:
                    p_name = ma.group(1)
                    p_value = ma.group(2)
                    if p_value.isdigit() and p_value in mod_globals.language_dict.keys():
                        p_value = mod_globals.language_dict[p_value]
                    layout_popup.add_widget(MyLabel(text=str(pyren_encode( "    %-20s : %s" % (p_name, p_value) )), font_size=fs, halign= 'left'))
                else:
                    layout_popup.add_widget(MyLabel(text=str(pyren_encode( line.strip().encode('utf-8', 'ignore').decode('utf-8'))), font_size=fs,  halign= 'left'))
        if self.command.scenario.startswith('scen'):
            name_scen_text = (self.command.scenario.split('#')[1].replace('&', '=').split('=')[1] +'_text.xml').lower()
            layout_popup.add_widget(MyLabel(text=name_scen_text, bgcolor=(1, 0, 0, 0.3)))
            for line in mod_zip.get_xml_scenario('scendata/'+ name_scen_text).toprettyxml().splitlines():
                
                if 'value' in line:
                    layout_popup.add_widget(MyLabel(text='', height=5, bgcolor=(1, 1, 0, 0.3)))
                    pa = re.compile(r'value=\"(\w+)\"\s+name=\"(.+)\"')
                    ma = pa.search( line.strip() )
                    pa2 = re.compile(r'name=\"(.+)\"\s+value=\"(\w+)\"')
                    ma2 = pa2.search( line.strip() )
                    if ma:
                        p_name = ma.group(2)
                        p_value = ma.group(1)
                        if p_value.isdigit() and p_value in mod_globals.language_dict.keys():
                            p_value = mod_globals.language_dict[p_value]
                        layout_popup.add_widget(MyLabel(text=str(pyren_encode( "    %-20s : %s" % (p_name, p_value) )), font_size=fs, halign= 'left'))
                    elif ma2:
                        p_name = ma2.group(1)
                        p_value = ma2.group(2)
                        if p_value.isdigit() and p_value in mod_globals.language_dict.keys():
                            p_value = mod_globals.language_dict[p_value]
                        layout_popup.add_widget(MyLabel(text=str(pyren_encode( "    %-20s : %s" % (p_name, p_value) )), font_size=fs, halign= 'left'))
                    else:
                        layout_popup.add_widget(MyLabel(text=str(pyren_encode( line.strip().encode('utf-8', 'ignore').decode('utf-8'))), font_size=fs,  halign= 'left'))
        layout_popup.add_widget(Button(text='CANCEL', on_press=self.stop, size_hint=(1, None), height=60))
        root = ScrollView(size_hint=(1, 1), size=(Window.width*0.9, Window.height*0.9))
        root.add_widget(layout_popup)
        popup = Popup(title=self.header, content=root, size_hint=(1, 1))
        popup.open()

    
    def get_message(self, msg):
        if msg in self.ScmParam.keys():
            value = self.ScmParam[msg]
        else:
            value = msg
        if value.isdigit() and value in mod_globals.language_dict.keys():
            value = pyren_encode(mod_globals.language_dict[value])
        return value

    def get_message_by_id(self, id):
        if id.isdigit() and id in mod_globals.language_dict.keys():
            value = pyren_encode(mod_globals.language_dict[id])
        return value

def run(elm, ecu, command, data):
    app = Scenarii(elm=elm, ecu=ecu, command=command, data=data)
    app.run()
