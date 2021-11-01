#Embedded file name: /build/PyCLIP/android/app/mod_ecu_scenario.py
import re

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