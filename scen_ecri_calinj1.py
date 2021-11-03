#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
import mod_utils
import mod_ecu
import mod_zip
from mod_utils import pyren_encode
from mod_utils import clearScreen
from mod_utils import ASCIITOHEX
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
fs =  mod_globals.fontSize
class MyLabel(Label):

    def __init__(self, **kwargs):
        if 'bgcolor' in kwargs:
            self.bgcolor = kwargs['bgcolor']
        else:
            self.bgcolor = (0, 0, 0, 0)
        super(MyLabel, self).__init__(**kwargs)
        self.bind(size=self.setter('text_size'))
        self.halign = 'center'
        self.valign = 'middle'
        if 'size_hint' not in kwargs:
            self.size_hint = (1, None)
        if 'height' not in kwargs:
            fmn = 1.7
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 7
            if lines > 20: lines = 15
            if 1 > simb: lines = 1
            if fs > 25: lines = lines * 1.05
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


class Scenarii(App):
    
    def __init__(self, **kwargs):
        DOMTree = mod_zip.get_xml_scenario(kwargs['data'])
        self.ScmRoom = DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = {}
        self.ScmSet = {}
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value

        for Set in ScmSets:
            setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
            ScmParams = Set.getElementsByTagName('ScmParam')
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                self.ScmSet[setname] = value
                self.ScmParam[name] = value

        super(Scenarii, self).__init__(**kwargs)

    def build(self):
        fs = mod_globals.fontSize
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1)
        codemr1, label1, value1 = self.ecu.get_id(self.ScmParam['Injecteur1'], True)
        codemr2, label2, value2 = self.ecu.get_id(self.ScmParam['Injecteur2'], True)
        codemr3, label3, value3 = self.ecu.get_id(self.ScmParam['Injecteur3'], True)
        codemr4, label4, value4 = self.ecu.get_id(self.ScmParam['Injecteur4'], True)
        codemr1 = '%s : %s' % (pyren_encode(codemr1), pyren_encode(label1))
        codemr2 = '%s : %s' % (pyren_encode(codemr2), pyren_encode(label2))
        codemr3 = '%s : %s' % (pyren_encode(codemr3), pyren_encode(label3))
        codemr4 = '%s : %s' % (pyren_encode(codemr4), pyren_encode(label4))

        layout_current1 = BoxLayout(orientation='horizontal', height=fs * 2, size_hint=(1, None))
        layout_current1.add_widget(MyLabel(text=pyren_encode(label1), size_hint=(1, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current1.add_widget(MyLabel(text=value1, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3)))
        layout_current2 = BoxLayout(orientation='horizontal', height=fs * 2, size_hint=(1, None))
        layout_current2.add_widget(MyLabel(text=pyren_encode(label2), size_hint=(1, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current2.add_widget(MyLabel(text=value2,  size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3)))
        layout_current3 = BoxLayout(orientation='horizontal', height=fs * 2, size_hint=(1, None))
        layout_current3.add_widget(MyLabel(text=pyren_encode(label3), size_hint=(1, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current3.add_widget(MyLabel(text=value3, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3)))
        layout_current4 = BoxLayout(orientation='horizontal', height=fs * 2, size_hint=(1, None))
        layout_current4.add_widget(MyLabel(text=pyren_encode(label4), size_hint=(1, None), bgcolor=(0, 0, 1, 0.3)))
        layout_current4.add_widget(MyLabel(text=value4, size_hint=(0.6, None), bgcolor=(0, 1, 0, 0.3)))
        
        root.add_widget(MyLabel(text=header))
        
        root.add_widget(MyLabel(text=self.get_message('TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(layout_current1)
        root.add_widget(layout_current2)
        root.add_widget(layout_current3)
        root.add_widget(layout_current4)
        root.add_widget(MyLabel(text=self.get_message('TextMessage4'), bgcolor=(1, 0, 0, 0.3)))
        
        #root.add_widget(TextInput(text='VF', multiline=False, size_hint=(1, None), height=40))

        root.add_widget(Button(text='Прописать форсунки', on_press=self.write_inj, size_hint=(1, None), height=80))
        root.add_widget(Button(text='CANCEL', on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        rot.add_widget(root)
        return rot
    
    def write_vin(self):
        root = GridLayout(cols=1)
        self.vin_input = TextInput(text='VF', multiline=False, size_hint=(1, None), height=40)
        root.add_widget(self.vin_input)
        return root
    
    def write_vin(self, instance):
        vin = self.vin_input.text.upper()
        if not (len(vin) == 17 and 'I' not in vin and 'O' not in vin):
            popup = Popup(title='Status', content=Label(text='Invalid VIN'), auto_dismiss=True, size=(500, 500), size_hint=(None, None))
            popup.open()
            return None
        vin_crc = hex_VIN_plus_CRC(vin)
        self.ecu.run_cmd(self.ScmParam['ConfigurationName'], vin_crc)
        popup = Popup(title='Status', content=Label(text='VIN CHANGED'), auto_dismiss=True, size=(500, 500), size_hint=(None, None))
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
