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
from kivy.base import EventLoop
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from collections import OrderedDict
import xml.dom.minidom
import xml.etree.cElementTree as et
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock

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
            fmn = 1.2
            lines = len(self.text.split('\n'))
            simb = len(self.text) / 60
            if lines < simb: lines = simb
            if lines < 7: lines = 7
            if lines > 20: lines = 20
            if fs > 20: 
                lines = lines * 1.1
                fmn = 1.7
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

class ScrMsg(Screen):
    pass

class ecus:
    
    vdiag = ""
    buttons = {}
    ncalib = ""

    def __init__(self, vd, nc, bt):
        self.vdiag = vd
        self.ncalib = nc
        self.buttons = bt

class Scenario(App):

    def __init__(self, **kwargs):
        self.data = kwargs['data']
        DOMTree = mod_zip.get_xml_scenario(self.data)
        self.ScmRoom = DOMTree.documentElement
        ScmParams = self.ScmRoom.getElementsByTagName('ScmParam')
        ScmSets = self.ScmRoom.getElementsByTagName('ScmSet')
        self.elm = kwargs['elm']
        self.command = kwargs['command']
        self.ecu = kwargs['ecu']
        self.ScmParam = OrderedDict()
        self.vdiagExists = False
        self.ncalibExists = False
        self.ScmSet = {}
        self.Buttons = {}
        self.commands = {}
        self.ecusList = []
        self.correctEcu = ''
        self.droot = et.fromstring(mod_zip.get_xml_scenario_et(self.data))
        
        for Param in ScmParams:
            name = pyren_encode(Param.getAttribute('name'))
            value = pyren_encode(Param.getAttribute('value'))
            self.ScmParam[name] = value
        
        for Set in ScmSets:
            if len(Set.attributes) != 1:
                setname = pyren_encode(mod_globals.language_dict[Set.getAttribute('name')])
                ScmParams = Set.getElementsByTagName('ScmParam')
                for Param in ScmParams:
                    name = pyren_encode(Param.getAttribute('name'))
                    value = pyren_encode(Param.getAttribute('value'))
                    self.ScmSet[setname] = value
                    self.ScmParam[name] = value
        
        if "VDiag" in self.ScmParam.keys():
            self.vdiagExists = True
            if "Ncalib" in self.ScmParam.keys():
                self.ncalibExists = True
        
        for vDiag in self.droot:
            if vDiag.attrib["name"] == "VDiag":
                if len(vDiag.keys()) == 1:
                    for vDiagName in vDiag:
                        if vDiagName:
                            for vDiagButtons in vDiagName:
                                buttons = OrderedDict()
                                if vDiagButtons.attrib["name"] == "Ncalib":
                                    for ncalibName in vDiagButtons:
                                        for ncalibButtons in ncalibName:
                                            if ncalibButtons.attrib["name"] == "Buttons":
                                                for ncalibButton in ncalibButtons:
                                                    buttons[ncalibButton.attrib["name"]] = ncalibButton.attrib["value"]
                                                self.ecusList.append(ecus(vDiagName.attrib["name"],ncalibName.attrib["name"], buttons))
                                                buttons = OrderedDict()
                                else:
                                    if vDiagButtons.attrib["name"] == "Buttons":
                                        for vDiagButton in vDiagButtons:
                                            buttons[vDiagButton.attrib["name"]] = vDiagButton.attrib["value"]
                                    self.ecusList.append(ecus(vDiagName.attrib["name"], '', buttons))
            if vDiag.attrib["name"] == "Commands":
                if len(vDiag.keys()) == 1:
                    for param in vDiag:
                        serviceIDs = self.ecu.get_ref_cmd(param.attrib["value"]).serviceID
                        startReq = ""
                        for sid in serviceIDs:
                            if self.ecu.Services[sid].params:
                                startReq = self.ecu.Services[sid].startReq
                                break
                        self.commands[param.attrib["name"]] = {"command": param.attrib["value"], "startReq": startReq}
            
        if self.vdiagExists:
            if not self.ncalibExists:
                vdiag = ''
                buttons = OrderedDict()
                for name in self.ScmParam.keys():
                    if name.startswith("InjectorsButton"):
                        if buttons:
                            self.ecusList.append(ecus(vdiag, '', buttons))
                        buttons = OrderedDict()
                        vdiag = name[-2:]
                        buttons[name[:-2]] = self.ScmParam[name]
                    if vdiag:
                        if name.endswith("Button" + vdiag):
                            buttons[name[:-2]] = self.ScmParam[name]
                self.ecusList.append(ecus(vdiag, '', buttons))
        else:
            buttons = OrderedDict()
            found = False
            for name in self.ScmParam.keys():
                    if name == "InjectorsButton":
                        buttons[name] = self.ScmParam[name]
                        found = True
                    if found:
                        if name.endswith("Button"):
                            buttons[name] = self.ScmParam[name]
                        else:
                            found = False
                            break
            self.ecusList.append(ecus('', '', buttons))
        
        if self.vdiagExists:
            value1, datastr1 = self.ecu.get_id(self.ScmParam['VDiag'])
            for ecuSet in self.ecusList:
                if ecuSet.vdiag == value1.upper():
                    if self.ncalibExists:
                        if ecuSet.ncalib:
                            value2, datastr2 = ecu.get_id(ScmParam['Ncalib'])
                            if ecuSet.ncalib == value2.upper():
                                self.correctEcu = ecuSet
                                break
                            elif ecuSet.ncalib == "Other":
                                self.correctEcu = ecuSet
                                break
                        else:
                            self.correctEcu = ecuSet
                            break
                    else:
                        self.correctEcu = ecuSet
                        break 
        else:
            self.correctEcu = self.ecusList[0]

        if not self.correctEcu and mod_globals.opt_demo:
            self.correctEcu = self.ecusList[0]
        
        if self.vdiagExists:
            if not self.correctEcu:
                print '*'*80
                ch = raw_input('Unknown diagnostic version. Press ENTER to exit')
                return
        
        self.identsList = OrderedDict()
        self.identsRangeKeys = OrderedDict()

        for param in self.ScmParam.keys():
            if param.startswith('Idents') and param.endswith('Begin'):
                key = param[6:-5]
                begin = int(self.ScmParam['Idents'+key+'Begin'])
                end = int(self.ScmParam['Idents'+key+'End'])
                try:
                    self.ecu.get_ref_id(self.ScmParam['Ident' + str(begin)]).mnemolist[0]
                except:
                    continue
                else:
                    for idnum in range(begin ,end + 1):
                        self.identsList['D'+str(idnum)] = self.ScmParam['Ident'+str(idnum)]
                        if len(self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist) > 1:
                            mnemonicsLen = map(lambda bitsLen: int(self.ecu.Mnemonics[bitsLen].bitsLength), self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist)
                            self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist = [self.ecu.get_ref_id(self.ScmParam['Ident' + str(idnum)]).mnemolist[mnemonicsLen.index(max(mnemonicsLen))]]
                    frame = self.ecu.Mnemonics[self.ecu.get_ref_id(self.identsList['D'+str(begin)]).mnemolist[0]].request
                    self.identsRangeKeys[key] = {"begin": begin, "end": end, "frame": frame}
        
        self.functions = OrderedDict()
        for cmdKey in self.commands.keys():
            if cmdKey == 'Cmd1':
                self.injectorsDict = OrderedDict()
                self.injectorsDict[self.get_message('Cylinder1')] = self.commands['Cmd1']['command']
                self.injectorsDict[self.get_message('Cylinder2')] = self.commands['Cmd2']['command']
                self.injectorsDict[self.get_message('Cylinder3')] = self.commands['Cmd3']['command']
                self.injectorsDict[self.get_message('Cylinder4')] = self.commands['Cmd4']['command']
                self.functions[1] = [1, self.injectorsDict]
            if cmdKey == 'Cmd5':
                self.functions[2] = ["EGR_VALVE", 2, self.commands['Cmd5']['command']]
            if cmdKey == 'Cmd6':
                self.functions[3] = ["INLET_FLAP", 3, self.commands['Cmd6']['command']]
            if cmdKey == 'Cmd7':
                self.functions[4] = ["PARTICLE_FILTER", 4, self.commands['Cmd7']['command']]
                self.functions[5] = ["Button5ChangeData", 5, self.commands['Cmd7']['command']]
                self.functions[6] = ["Button6ChangeData", 6, self.commands['Cmd7']['command']]
            if cmdKey == 'Cmd9':
                self.functions[8] = ["Button8DisplayData", 8]
        
        super(Scenario, self).__init__(**kwargs)

    def build(self):
        self.mainText =self.get_message('Title')
        header = '[' + self.command.codeMR + '] ' + self.command.label
        root = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        root.add_widget(MyLabel(text=header, height=fs*3))
        root.add_widget(MyLabel(text=self.mainText, bgcolor=(1, 1, 0, 0.3), height=fs*3))
        layout = BoxLayout(orientation='vertical', spacing=15, size_hint=(1, 1))
        self.sm = ScreenManager(size_hint=(1, 1))
        scr1 = ScrMsg(name='SCR1')
        self.sm.add_widget(scr1)
        layout1 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout1.add_widget(self.info('Informations', 'Message1'))
        for bt in self.correctEcu.buttons.keys():
            if bt == 'InjectorsButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    layout1.add_widget(Button(text=self.get_message('Injectors'), on_press=lambda *args: self.button_screen('SCR_INJ'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt == 'EGRValveButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    layout1.add_widget(Button(text=self.get_message('EGR_VALVE'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt == 'InletFlapButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    layout1.add_widget(Button(text=self.get_message('INLET_FLAP'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt.startswith("Button"):
                if str(self.correctEcu.buttons[bt]) == 'true':
                    layout1.add_widget(Button(text=self.get_message(bt[:-6] + "Text"),id=bt,  on_press=self.resetValues, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
                    
        scr1.add_widget(layout1)
        scr2 = ScrMsg(name='SCR_INJ')
        layout2 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout2.add_widget(self.info('Informations', 'Message21'))
        inj = self.functions[1][1].keys()
        self.inj_button = Button(text=inj[0], on_press=lambda *args: self.resetInjetorsData(inj[0]), size_hint=(1, 1), background_color=(0, 1, 0, 1))
        layout2.add_widget(self.inj_button)
        self.inj_button = Button(text=inj[1], on_press=lambda *args: self.resetInjetorsData(inj[1]), size_hint=(1, 1), background_color=(0, 1, 0, 1))
        layout2.add_widget(self.inj_button)
        self.inj_button = Button(text=inj[2], on_press=lambda *args: self.resetInjetorsData(inj[2]), size_hint=(1, 1), background_color=(0, 1, 0, 1))
        layout2.add_widget(self.inj_button)
        self.inj_button = Button(text=inj[3], on_press=lambda *args: self.resetInjetorsData(inj[3]), size_hint=(1, 1), background_color=(0, 1, 0, 1))
        layout2.add_widget(self.inj_button)
        layout2.add_widget(Button(text=self.get_message('6218'), on_press=lambda *args: self.button_screen('SCR1'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
        scr2.add_widget(layout2)
        self.sm.add_widget(scr2)
        layout.add_widget(self.sm)
        root.add_widget(layout)
        root.add_widget(Button(text=self.get_message('1053'), on_press=self.stop, size_hint=(1, None)))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        rot.add_widget(root)
        return rot
    
    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 2))
        layout.add_widget(MyLabel(text=self.get_message(info), size_hint=(1, 1), bgcolor=(0.3, 0.3, 0, 0.3)))
        layout.add_widget(MyLabel(text=self.get_message(message), size_hint=(1, 1), bgcolor=(1, 0, 0, 0.3)))
        return layout

    def takesParams(self, request):
        for cmd in self.commands.values():
            if cmd['startReq'] == request:
                commandToRun = cmd['command']
                return commandToRun

    def getValuesToChange(self, resetItem):
        params = {}
        for child in self.droot:
            if child.attrib["name"] == resetItem:
                if len(child.keys()) == 1:
                    for param in child:
                        params[param.attrib["name"].replace("D0", "D")] = param.attrib["value"]
        return params

    def button_screen(self, dat, start=None):
        self.sm.current = dat
 
    def afterEcuChange(self, key):
        print key
 
    def setGlowPlugsType(self, key):
        print key
 
    def resetValues(self, instance):
        lbltxt = Label(text=str(instance.id))
        popup = Popup(title='title', auto_dismiss=True, content=lbltxt, size=(400, 400), size_hint=(None, None))
        popup.open()
        title = ''
        button = ''
        defaultCommand = ''
        paramToSend = ""
        commandTakesParams = True
        

    def resetInjetorsData(self, key):
        response = ''
        lbltxt = Label(text=self.get_message('CommandInProgressMessage'))
        title = self.get_message('Clip')
        title = key
        popup = Popup(title=title, auto_dismiss=True, content=lbltxt, size=(400, 400), size_hint=(None, None))
        popup.open()
        EventLoop.idle()
        response = self.ecu.run_cmd(self.functions[1][1][key])
        lbltxt.text = self.get_message('CommandFinishedMessage')
        lbltxt.text += ':\n'
        if "NR" in response:
            lbltxt.text += self.get_message('MessageNACK')
        else:
            lbltxt.text += self.get_message('Message31')
        
    
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
    app = Scenario(elm=elm, 
    ecu=ecu, command=command, data=data)
    app.run()
