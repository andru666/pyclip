#Embedded file name: /build/PyCLIP/android/app/mod_ecu_scenario.py
import re, os, mod_globals

if mod_globals.os == 'android':
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
    import sys
    scen_dir = Environment.getExternalStorageDirectory().getAbsolutePath() + '/pyren/scen/'
    if not os.path.exists(scen_dir):
        os.makedirs(scen_dir)
    sys.path.append(scen_dir)

def playScenario(command, ecu, elm):

    services = ecu.Services
    scenarioName, scenarioData = command.scenario.split('#')
    
    if scenarioName.lower().startswith('scm'):
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        scenarioName = scenarioData[:scenarioData.find(ecuNumberIndex.group(0)) - 1].lower()
    else:
        scenarioData = scenarioData[5:].replace('=', '_').replace('.xml', '').replace('&ecu', '_Ecu')+'.xml'
        scenarioName = scenarioName.split(':')[1]
        ecuNumberPattern = re.compile(r'\d{5}')
        ecuNumberIndex = ecuNumberPattern.search(scenarioData)
        scenarioD = scenarioData.replace('_Ecu_', '').replace('_ECU_', '').replace('_Const_', '').replace('_CONST_', '')
        scenarioName = scenarioD[:scenarioD.find(ecuNumberIndex.group(0))].lower()
        scenarioData = 'Ecudata/'+scenarioData
    try:
        scen = __import__(scenarioName)
        scen.run(elm, ecu, command, scenarioData)
        return True
    except:
        scen = __import__('show_scen')
        scen.run(elm, ecu, command, scenarioData)
        return True