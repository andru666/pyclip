#Embedded file name: /build/PyCLIP/android/app/scen_ecri_codevin.py
import time, re
import mod_ecu_mnemonic, mod_globals, mod_zip
from mod_utils import pyren_encode, clearScreen, ASCIITOHEX, hex_VIN_plus_CRC, isHex
from mod_ecu import *
from collections import OrderedDict
from kivy.app import App
from kivy import base
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from functools import partial
import xml.dom.minidom
import xml.etree.cElementTree as et

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
        
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.data = kwargs['data']

        DOMTree = mod_zip.get_xml_scenario(self.data)
        ScmRoom = DOMTree.documentElement
        ScmParams = ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = ScmRoom.getElementsByTagName('ScmSet')
        self.ScmParam = OrderedDict()
        self.ScmSet = OrderedDict()
        
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            setname = pyren_encode(Set.getAttribute('name'))
            ScmParams = Set.getElementsByTagName('ScmParam')
            scmParamsDict = OrderedDict()
            for Param in ScmParams:
                name = pyren_encode(Param.getAttribute('name'))
                value = pyren_encode(Param.getAttribute('value'))
                scmParamsDict[name] = value
            self.ScmSet[setname]= scmParamsDict
        
        super(Scenarii, self).__init__(**kwargs)

    def build(self):
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.bind(minimum_height=root.setter('height'))
        root.add_widget(MyLabel(text=header))
        root.add_widget(MyLabel(text=self.get_message('Title'), bgcolor=(1, 1, 0, 0.3), height=fs*3))
        root.add_widget(MyLabel(text=self.get_message('Subtitle'), bgcolor=(1, 0.3, 0, 0.3), height=fs*3))
        root.add_widget(self.info('Informations', 'InformationsContent'))
        root.add_widget(self.button_yes_no(False, self.resetValues))
        root.add_widget(Button(text=self.get_message('6218'), on_press=self.stop, size_hint=(1, None), height=80))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        rot.add_widget(root)
        return rot
    
    def valueReset(self, name, value):
        
        if isHex(value):
            response = self.ecu.run_cmd(self.ScmSet['Commands'][name],value)
        else:
            result = re.search(r"[^a-zA-Z\d\s:]", value)
            if result:
                parameters = re.findall(r"Ident\d+", value)
                paramByteLength = len(parameters[0])/2
                comp = value
                for param in parameters:
                    paramValue = self.ecu.get_id(self.ScmSet['Identifications'][param], 5)
                    if isHex(paramValue):
                        comp = comp.replace(param, '0x' + self.ecu.get_id(self.ScmSet['Identifications'][param], 5))
                    if comp:
                        calc = Calc()
                        idValue = calc.calculate(comp)
                        hexVal = hex(idValue)[2:]
                        if len(hexVal)%2:
                            hexVal = '0' + hexVal
                        if (len(hexVal)/2) % paramByteLength:
                            hexVal = '00' * (paramByteLength - len(hexVal)/2) + hexVal
                        response = self.ecu.run_cmd(self.ScmSet['Commands'][name],hexVal)
            else:
                idValue = self.ecu.get_id(self.ScmSet['Identifications'][value], 5)
                if isHex(idValue):
                    response = self.ecu.run_cmd(self.ScmSet['Commands'][name],idValue)
        return response

    def reset_Values(self,instance):
        self.popup.dismiss()
        
        self.lbltxt = Label(text=self.get_message('CommandInProgress'))
        response = ''
        popup = Popup(title='STATUS', auto_dismiss=True, content=self.lbltxt, size=(Window.size[0]*0.7, Window.size[1]*0.7), size_hint=(None, None))
        popup.open()
        time.sleep(5)
        base.EventLoop.idle
        for name, value in self.ScmSet['CommandParameters'].iteritems():
            response += self.valueReset(name, value)
        base.EventLoop.idle()
        self.lbltxt.text = self.get_message('CommandFinished')
        self.lbltxt.text += ':\n'
        
        if "NR" in response:
            self.lbltxt.text += self.get_message('EndScreenMessage4')
        else:
            self.lbltxt.text += self.get_message('EndScreenMessage3')   



    def resetValues(self, instance):
        if not mod_globals.opt_demo:
            makeDump()
            
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        self.lbltxt = MyLabel(text=self.get_message('CommandInProgress'))
        layout.add_widget(self.lbltxt)
        layout.add_widget(Button(text=self.get_message('1926'), on_press=self.reset_Values, size_hint=(1, 1), height=fs*2))
        self.popup = Popup(title='STATUS', auto_dismiss=True, content=layout, size=(Window.size[0]*0.7, Window.size[1]*0.7), size_hint=(None, None))
        self.popup.open()
         
        
    def button_yes_no(self, no=True, yes=None):
        layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 1))
        if yes: layout.add_widget(Button(text=self.get_message('Yes'), on_press=yes, size_hint=(1, 1), height=fs*2))
        if no: layout.add_widget(Button(text=self.get_message('No'), on_press=self.stop, size_hint=(1, 1), height=fs*2))
        return layout

    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 2))
        layout.add_widget(MyLabel(text=self.get_message(info), size_hint=(1, 1), bgcolor=(0.3, 0.3, 0, 0.3)))
        layout.add_widget(MyLabel(text=self.get_message(message), size_hint=(1, 1), bgcolor=(1, 0, 0, 0.3)))
        return layout
    
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
