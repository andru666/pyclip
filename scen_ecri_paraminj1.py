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
from kivy.core.window import Window
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
        if 'halign' not in kwargs:
            self.halign = 'center'
        if 'valign' not in kwargs:
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
        self.CLIP = self.get_message('Clip')
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
        
        id_bt = 1
        self.Buttons = OrderedDict()
        for bt in self.correctEcu.buttons.keys():
            if bt == 'InjectorsButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[1] = self.get_message('Injectors')
                    layout1.add_widget(Button(text=self.Buttons[1], on_press=lambda *args: self.button_screen('SCR_INJ'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt == 'EGRValveButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[2] = self.get_message('EGR_VALVE')
                    layout1.add_widget(Button(text=self.Buttons[2], id=str(id_bt), on_press=self.resetValues, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt == 'InletFlapButton':
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[3] = self.get_message('INLET_FLAP')
                    layout1.add_widget(Button(text=self.Buttons[3], id=str(id_bt), on_press=self.resetValues, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            if bt.startswith("Button"):
                if str(self.correctEcu.buttons[bt]) == 'true':
                    self.Buttons[int(bt.strip('Button'))] = self.get_message(bt[:-6] + "Text")
                    layout1.add_widget(Button(text=self.Buttons[int(bt.strip('Button'))],id=str(id_bt), on_press=self.resetValues, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
            id_bt += 1
        scr1.add_widget(layout1)
        scr2 = ScrMsg(name='SCR_INJ')
        layout2 = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1))
        layout2.add_widget(self.info('Informations', 'Message21'))
        
        for inj in self.functions[1][1].keys(): 
            layout2.add_widget(Button(text=inj, id=inj, on_press=self.resetInjetorsData, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
        
        layout2.add_widget(Button(text=self.get_message('6218'), on_press=lambda *args: self.button_screen('SCR1'), size_hint=(1, 1), background_color=(0, 1, 0, 1)))
        scr2.add_widget(layout2)
        self.sm.add_widget(scr2)
        
        self.scr3 = ScrMsg(name='SCR_I')
        self.sm.add_widget(self.scr3)
        layout.add_widget(self.sm)
        root.add_widget(layout)
        root.add_widget(Button(text=self.get_message('1053'), on_press=self.stop, size_hint=(1, None)))
        rot = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        rot.add_widget(root)
        return rot

    def takesParams(request):
        for cmd in self.commands.values():
            if cmd['startReq'] == request:
                commandToRun = cmd['command']
                return commandToRun

    def makeDump(self, cmd, idents):
        fileRoot = et.Element("ScmRoot")
        fileRoot.text = "\n        "

        cmdElement = et.Element("ScmParam", name="Command", value=cmd)
        cmdElement.tail = "\n        "
        fileRoot.insert(1,cmdElement)
        
        for k in idents:
            el = et.Element("ScmParam", name='D'+ '{:0>2}'.format(k[1:]), value=str(idents[k]))
            el.tail = "\n        "
            fileRoot.insert(1,el)

        tree = et.ElementTree(fileRoot)
        tree.write(mod_globals.dumps_dir + self.ScmParam['FileName'])

    def getValuesFromEcu(self, params):
        paramToSend = ""
        commandToRun = ""
        requestToFindInCommandsRequests = ""
        backupDict = {}
        #layout1.add_widget(MyLabel(text=str(self.identsRangeKeys)))
        try:
            idKeyToFindInRange = int((params.keys()[0]).replace("D",""))
        except:
            return commandToRun, paramToSend
        else:
            layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
            lbltxt = Label(text='')
            for rangeK in self.identsRangeKeys.keys():
                if self.identsRangeKeys[rangeK]['begin'] <= idKeyToFindInRange <= self.identsRangeKeys[rangeK]['end']:
                    requestToFindInCommandsRequests = "3B" + self.identsRangeKeys[rangeK]['frame'][-2:]
                    isTakingParams = self.takesParams(requestToFindInCommandsRequests)
                    if isTakingParams:
                        for k,v in params.iteritems():
                            backupDict[k] = self.ecu.get_id(self.identsList[k], 5)
                            if v in self.identsList.keys():
                                self.identsList[k] = self.ecu.get_id(self.identsList[v], 5)
                            else:
                                self.identsList[k] = v
                        layout.add_widget(MyLabel(text=str(self.identsList)))
                        for idKey in range(self.identsRangeKeys[rangeK]['begin'], self.identsRangeKeys[rangeK]['end'] + 1):
                            if str(self.identsList["D" + str(idKey)]).startswith("ID"):
                                self.identsList["D" + str(idKey)] = self.ecu.get_id(self.identsList["D" + str(idKey)], 5)
                                backupDict["D" + str(idKey)] = self.identsList["D" + str(idKey)]
                            paramToSend += str(self.identsList["D" + str(idKey)])
                        layout.add_widget(MyLabel(text=str(self.identsList)))
                        commandToRun = isTakingParams
                        break
            self.makeDump(commandToRun, backupDict)
            return commandToRun, paramToSend

    def info(self, info, message):
        layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 2))
        layout.add_widget(MyLabel(text=self.get_message(info), size_hint=(1, 0.3), bgcolor=(0.3, 0.3, 0, 0.3)))
        layout.add_widget(MyLabel(text=self.get_message(message), size_hint=(1, 0.7), bgcolor=(1, 0, 0, 0.3)))
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
 
    def afterEcu_Change(self, instance):
        self.popup_afterEcuChange.dismiss()
        title = self.functions[6][0]
        params = self.getValuesToChange(title)
        mileage = int(self.mileage.text)
        
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        lbltxt = MyLabel(text=self.get_message('CommandInProgressMessage'))
        for paramkey in params.keys():
            if params[paramkey] == "Mileage":
                mnemonics = self.ecu.get_ref_id(self.identsList[paramkey]).mnemolist[0]
                identValue = self.ecu.get_id(self.identsList[paramkey], 5)
                if identValue == 'ERROR':
                    identValue = '00000000'
                hexval = "{0:0{1}X}".format(mileage,len(identValue))
                if self.ecu.Mnemonics[mnemonics].littleEndian == '1':
                    a = hexval
                    b = ''
                    if not len(a) % 2:
                        for i in range(0,len(a),2):
                            b = a[i:i+2]+b
                        hexval = b
                params[paramkey] = hexval
        command, paramToSend = self.getValuesFromEcu(params)
        response = self.ecu.run_cmd(command,paramToSend)
        lbltxt.text = self.get_message('CommandFinishedMessage')
        lbltxt.text += ':\n'
        
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            popup = Popup(title=self.CLIP, auto_dismiss=True, content=lbltxt, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
            popup.open()
            return
        
        if "NR" in response:
            lbltxt.text += self.get_message('MessageNACK')
        else:
            lbltxt.text += self.get_message('Message31')
        layout.add_widget(lbltxt)
        popup = Popup(title=self.CLIP, auto_dismiss=True, content=layout, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
        popup.open()

    def afterEcuChange(self, instance):
        self.popup_resetValues.dismiss()
        button = self.functions[6][1]
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        if instance.id == '0':
            milea = self.mileage.text
        else:
            milea = ''
        self.mileage = TextInput(text=milea, multiline=False, size_hint=(1, None))
        if instance.id == '0':
            if not self.mileage.text.isdigit() and self.mileage.text:
                layout.add_widget(MyLabel(text=self.get_message('MessageBox2')))
                self.mileage = TextInput(text=milea, multiline=False, size_hint=(1, None))
                layout.add_widget(self.mileage)
                self.AECbutton = Button(text=self.get_message('1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None), height=fs*4)
                self.popup_afterEcuChange.dismiss()
            elif not (2 <= len(self.mileage.text) <= 6 and int(self.mileage.text) >= 10):
                layout.add_widget(MyLabel(text=self.get_message('MessageBox1')))
                self.mileage = TextInput(text=milea, multiline=False, size_hint=(1, None))
                layout.add_widget(self.mileage)
                self.AECbutton = Button(text=self.get_message('1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None), height=fs*4)
                self.popup_afterEcuChange.dismiss()
            else:
                layout.add_widget(MyLabel(text=self.mileage.text + ' ' + self.get_message('Unit1')))
                self.AECbutton = Button(text=self.get_message('1926'), id='0', on_press=self.afterEcu_Change, size_hint=(1, None), height=fs*4)
                self.popup_afterEcuChange.dismiss()
        else:
            layout.add_widget(self.mileage)
            self.AECbutton = Button(text=self.get_message('1926'), id='0', on_press=self.afterEcuChange, size_hint=(1, None), height=fs*4)
        layout.add_widget(self.AECbutton)
        self.popup_afterEcuChange = Popup(title=(self.Buttons[button]), auto_dismiss=True, content=layout, size=(Window.size[0]*0.9, Window.size[1]*0.9), size_hint=(None, None))
        self.popup_afterEcuChange.open()
        
    def set_GlowPlugsType(self, instance):
        self.popup_setGlowPlugsType.dismiss()
        params = self.getValuesToChange(self.functions[8][0])
        params[params["IdentToBeDisplayed"].replace("Ident", "D")] = self.get_message(instance.id)
        params.pop("IdentToBeDisplayed")
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        lbltxt = MyLabel(text=self.get_message('CommandInProgressMessage'))
        command, paramToSend = self.getValuesFromEcu(params)
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            popup = Popup(title=self.CLIP, auto_dismiss=True, content=lbltxt, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
            popup.open()
            return
        
        response = self.ecu.run_cmd(command,paramToSend)
        lbltxt.text = self.get_message('CommandFinishedMessage')
        lbltxt.text += ':\n'
        if "NR" in response:
            lbltxt.text += self.get_message('MessageNACK')
        else:
            lbltxt.text += self.get_message('Message31')
        layout.add_widget(lbltxt)
        popup = Popup(title=self.CLIP, auto_dismiss=True, content=layout, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
        popup.open()
        

    def setGlowPlugsType(self, instance):
        self.popup_resetValues.dismiss()
        params = self.getValuesToChange(self.functions[8][0])
        currentType = self.ecu.get_id(self.identsList[params["IdentToBeDisplayed"].replace("Ident", "D")], 5)
        slowTypeValue = self.get_message('ValueSlowParam')
        fastTypeValue = self.get_message('ValueFastParam')
        currentMessage = self.get_message_by_id('52676')
        slowMessage = self.get_message('Slow')
        fastMessage = self.get_message('Fast')
        notDefinedMessage = self.get_message('NotDefined')
        
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        if currentType == slowTypeValue:
            currentTy = currentMessage + ': ' + slowMessage
        elif currentType == fastTypeValue:
            currentTy = currentMessage + ': ' + fastMessage
        else:
            currentTy = currentMessage + ': ' + notDefinedMessage
        layout.add_widget(MyLabel(text=currentTy))
        layout.add_widget(Button(text=slowMessage, id='ValueSlowParam', on_press=self.set_GlowPlugsType, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
        layout.add_widget(Button(text=fastMessage, id='ValueFastParam', on_press=self.set_GlowPlugsType, size_hint=(1, 1), background_color=(0, 1, 0, 1)))
        layout_box = BoxLayout(orientation='horizontal', spacing=5, size_hint=(1, 1))
        layout_box.add_widget(Button(text=self.get_message('1053'), on_press=self.stop, size_hint=(1, None), height=fs*4))
        layout.add_widget(layout_box)
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        root.add_widget(layout)
        self.popup_setGlowPlugsType = Popup(title=(self.Buttons[self.functions[8][1]]), auto_dismiss=True, content=root, size=Window.size, size_hint=(None, None))
        self.popup_setGlowPlugsType.open()    

    def reset_Values(self, instance):
        self.popup_resetValues.dismiss()
        key = int(instance.id)
        defaultCommand = self.functions[key][2]
        title = self.functions[key][0]
        params = self.getValuesToChange(title)
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        lbltxt = MyLabel(text=self.get_message('CommandInProgressMessage'))
        command, paramToSend = self.getValuesFromEcu(params)
        if "ERROR" in paramToSend:
            lbltxt.text = "Data downloading went wrong. Aborting."
            popup = Popup(title=self.CLIP, auto_dismiss=True, content=lbltxt, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
            popup.open()
            return
        lbltxt.text = self.get_message('CommandFinishedMessage')
        lbltxt.text += ':\n'
        if command:
            response = self.ecu.run_cmd(command,paramToSend)
        else:
            response = self.ecu.run_cmd(defaultCommand)
        if "NR" in response:
            lbltxt.text += self.get_message('MessageNACK')
        else:
            lbltxt.text += self.get_message('Message31')
        layout.add_widget(lbltxt)
        popup = Popup(title=self.CLIP, auto_dismiss=True, content=layout, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
        popup.open()

    def resetValues(self, instance):
        key = int(instance.id)
        paramToSend = ""
        commandTakesParams = True
        button = self.functions[key][1]
        
        layout = GridLayout(cols=1, spacing=fs * 0.5, size_hint=(1, 1))
        lbltxt = MyLabel(text='', size_hint=(1, 1))
        if key == 2 or key == 7 or key == 3:
            lbltxt.text += self.get_message('Message23')
        if key == 4:
            layout.add_widget(self.info('Informations', 'MessageBox4'))
            lbltxt.text += self.get_message('Message24')
        if key == 5:
            lbltxt.text += self.get_message('Message25')
        if key == 8:
            layout.add_widget(self.info('Informations', 'Message282'))
            #lbltxt.text += self.get_message('MessageBox2')
        if key == 7:
            layout.add_widget(self.info('Informations', 'Message27'))
        if key == 6:
            layout.add_widget(self.info('Informations', 'Message262'))
            lbltxt.text += self.get_message('Message281')
        if lbltxt.text != '': layout.add_widget(lbltxt)
        layout_box = BoxLayout(orientation='horizontal', spacing=5, size_hint=(1, 1))
        res_button = Button(text=self.get_message('Yes'), id=str(key), size_hint=(1, 1), height=fs*2)
        layout_box.add_widget(res_button)
        if key == 6:
            res_button.bind(on_press=self.afterEcuChange)
        elif key == 8:
            res_button.bind(on_press=self.setGlowPlugsType)
        else:
            res_button.bind(on_press=self.reset_Values)
        layout_box.add_widget(Button(text=self.get_message('No'), on_press=self.stop, size_hint=(1, 1), height=fs*2))
        layout.add_widget(layout_box)
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        root.add_widget(layout)
        self.popup_resetValues = Popup(title=(self.Buttons[button]), auto_dismiss=True, content=root, size=Window.size, size_hint=(None, None))
        self.popup_resetValues.open()

    def resetInjetorsData(self, instance):
        response = ''
        lbltxt = Label(text=self.get_message('CommandInProgressMessage'))
        popup = Popup(title=self.CLIP, auto_dismiss=True, content=lbltxt, size=(Window.size[0]*0.7, Window.size[1]*0.5), size_hint=(None, None))
        popup.open()
        EventLoop.idle()
        response = self.ecu.run_cmd(self.functions[1][1][instance.id])
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