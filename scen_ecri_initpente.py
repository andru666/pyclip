#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import os
import sys
import re
import time
import mod_globals
import mod_utils
import mod_ecu
import mod_zip
import mod_ecu_mnemonic
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
            fmn = 1.1
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 5
            if lines > 20: lines = 15
            if 1 > simb: lines = 1.5
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
            try:
                setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
            except:
                pass
            ScmParams = Set.getElementsByTagName('ScmParam')
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                try:
                    self.ScmSet[setname] = value
                except:
                    pass
                self.ScmParam[name] = value
        
        super(Scenarii, self).__init__(**kwargs)

    def build(self):
        fs = mod_globals.fontSize
        
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1.0, None))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=self.get_message('TexteTitre'), bgcolor=(1, 1, 0, 0.3)))
        root.add_widget(MyLabel(text=self.get_message('TexteConsigne'), bgcolor=(1, 0, 0, 0.3)))
        root.add_widget(Button(text=self.command.label, on_press=self.pupp, size_hint=(1, None), height=80))
        
        root.add_widget(Button(text=self.get_message('6218'), on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5,
         'center_y': 0.5})
        rot.add_widget(root)
        return rot

    def pupp(self, instance):
        cmd = self.ecu.get_ref_cmd(self.ScmParam['Commande1'])
        resVal = self.ScmParam['ParametreCommande1']
        responce = self.ecu.run_cmd(self.ScmParam['Commande1'], resVal)
        codemr, label, value, unit = self.ecu.get_pr(self.ScmParam['ParametreInclinaison'], True)
        key = '%s - %s' % (codemr, label)
        value = '%s %s' % (value, unit)
        layout = GridLayout(cols=1, spacing=5, padding=fs*0.5, size_hint=(1, None))
        layout_current = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        layout_current.add_widget(MyLabel(text=key, size_hint=(0.6, 1), bgcolor=(0, 0, 1, 0.3)))
        layout_current.add_widget(MyLabel(text=value, size_hint=(0.4, 1), bgcolor=(0, 1, 0, 0.3)))
        layout.add_widget(layout_current)
        layout.add_widget(Button(text=self.get_message('6218'), fonte_size=fs, on_press=self.stop, size_hint=(1, None), height=fs*4))
        rootP = ScrollView(size_hint=(1, 1))
        rootP.add_widget(layout)
        if 'NR' not in responce:
            ch = self.get_message('TexteProcedureInterompue')
        else:
            ch = self.get_message('TexteInitialisationEffectuee')
        
        popup = Popup(title='STATUS', content=rootP, auto_dismiss=True, size=(500, 500), size_hint=(None, None))
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
    app = Scenarii(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
