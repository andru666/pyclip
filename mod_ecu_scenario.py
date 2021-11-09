#Embedded file name: /build/PyCLIP/android/app/mod_ecu_scenario.py
import re, os
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
    try:
        scen = __import__(scenarioName)
        scen.run(elm, ecu, command, scenarioData)
        return True
    except:
        return False