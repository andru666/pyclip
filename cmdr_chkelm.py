# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: /build/PyCLIP/android/app/cmdr_chkelm.py
# Compiled at: 2018-11-25 22:57:49
import os, sys, pyren, mod_globals
cmdb = '\n#v1.0 ;AC P; ATZ                   ; Z                  ; reset all\n#v1.0 ;AC P; ATE1                  ; E0, E1             ; Echo off, or on*\n#v1.0 ;AC P; ATL0                  ; L0, L1             ; Linefeeds off, or on\n#v1.0 ;AC  ; ATI                   ; I                  ; print the version ID\n#v1.0 ;AC  ; AT@1                  ; @1                 ; display the device description \n#v1.0 ;AC P; ATAL                  ; AL                 ; Allow Long (>7 byte) messages\n#v1.0 ;AC  ; ATBD                  ; BD                 ; perform a Buffer Dump\n#V1.0 ;ACH ; ATSP4                 ; SP h               ; Set Protocol to h and save it\n#v1.0 ;AC  ; ATBI                  ; BI                 ; Bypass the Initialization sequence\n#v1.0 ;AC P; ATCAF0                ; CAF0, CAF1         ; Automatic Formatting off, or on*\n#v1.0 ;AC  ; ATCF 123              ; CF hhh             ; set the ID Filter to hhh\n#v1.0 ;AC  ; ATCF 12345678         ; CF hhhhhhhh        ; set the ID Filter to hhhhhhhh\n#v1.0 ;AC  ; ATCFC1                ; CFC0, CFC1         ; Flow Controls off, or on*\n#v1.0 ;AC  ; ATCM 123              ; CM hhh             ; set the ID Mask to hhh\n#v1.0 ;AC  ; ATCM 12345678         ; CM hhhhhhhh        ; set the ID Mask to hhhhhhhh\n#v1.0 ;AC  ; ATCP 01               ; CP hh              ; set CAN Priority to hh (29 bit)\n#v1.0 ;AC  ; ATCS                  ; CS                 ; show the CAN Status counts \n#v1.0 ;AC  ; ATCV 1250             ; CV dddd            ; Calibrate the Voltage to dd.dd volts\n#v1.0 ;AC  ; ATD                   ; D                  ; set all to Defaults\n#v1.0 ;AC  ; ATDP                  ; DP                 ; Describe the current Protocol\n#v1.0 ;AC  ; ATDPN                 ; DPN                ; Describe the Protocol by Number\n#v1.0 ;AC P; ATH0                  ; H0, H1             ; Headers off*, or on\n#v1.0 ;AC  ; ATI                   ; I                  ; print the version ID\n#v1.0 ;AC P; ATIB 10               ; IB 10              ; set the ISO Baud rate to 10400*\n#v1.0 ;AC  ; ATIB 96               ; IB 96              ; set the ISO Baud rate to 9600      \n#v1.0 ;AC  ; ATL1                  ; L0, L1             ; Linefeeds off, or on\n#v1.0 ;AC  ; ATM0                  ; M0, M1             ; Memory off, or on\n#v1.0 ; C  ; ATMA                  ; MA                 ; Monitor All\n#v1.0 ; C  ; ATMR 01               ; MR hh              ; Monitor for Receiver = hh\n#v1.0 ; C  ; ATMT 01               ; MT hh              ; Monitor for Transmitter = hh\n#v1.0 ;AC  ; ATNL                  ; NL                 ; Normal Length messages*\n#v1.0 ;AC  ; ATPC                  ; PC                 ; Protocol Close\n#v1.0 ;AC  ; ATR1                  ; R0, R1             ; Responses off, or on*\n#v1.0 ;AC  ; ATRV                  ; RV                 ; Read the input Voltage\n#v1.0 ;ACH ; ATSP7                 ; SP h               ; Set Protocol to h and save it\n#v1.0 ;ACH ; ATSH 00000000         ; SH wwxxyyzz        ; Set Header to wwxxyyzz\n#v1.0 ;AC  ; ATSH 001122           ; SH xxyyzz          ; Set Header to xxyyzz\n#v1.0 ;AC P; ATSH 012              ; SH xyz             ; Set Header to xyz\n#v1.0 ;AC  ; ATSP A6               ; SP Ah              ; Set Protocol to Auto, h and save it\n#v1.0 ;AC  ; ATSP 6                ; SP h               ; Set Protocol to h and save it\n#v1.0 ;AC P; ATST FF               ; ST hh              ; Set Timeout to hh x 4 msec\n#v1.0 ;AC P; ATSW 96               ; SW 00              ; Stop sending Wakeup messages\n#v1.0 ;AC P; ATSW 34               ; SW hh              ; Set Wakeup interval to hh x 20 msec\n#v1.0 ;AC  ; ATTP A6               ; TP Ah              ; Try Protocol h with Auto search\n#v1.0 ;AC  ; ATTP 6                ; TP h               ; Try Protocol h\n#v1.0 ;AC P; ATWM 817AF13E         ; WM [1 - 6 bytes]   ; set the Wakeup Message\n#v1.0 ;AC P; ATWS                  ; WS                 ; Warm Start (quick software reset)\n#v1.1 ;AC P; ATFC SD 300000        ; FC SD [1 - 5 bytes]; FC, Set Data to [...]\n#v1.1 ;AC P; ATFC SH 012           ; FC SH hhh          ; FC, Set the Header to hhh\n#v1.1 ;AC P; ATFC SH 00112233      ; FC SH hhhhhhhh     ; Set the Header to hhhhhhhh \n#v1.1 ;AC P; ATFC SM 1             ; FC SM h            ; Flow Control, Set the Mode to h\n#v1.1 ;AC  ; ATPP FF OFF           ; PP FF OFF          ; all Prog Parameters disabled\n#v1.1 ;AC  ; ATPP FF ON            ; PP FF ON           ; all Prog Parameters enabled\n#v1.1 ;    ;                       ; PP xx OFF          ; disable Prog Parameter xx\n#v1.1 ;    ;                       ; PP xx ON           ; enable Prog Parameter xx \n#v1.1 ;    ;                       ; PP xx SV yy        ; for PP xx, Set the Value to yy\n#v1.1 ;AC  ; ATPPS                 ; PPS                ; print a PP Summary\n#v1.2 ;AC  ; ATAR                  ; AR                 ; Automatically Receive\n#v1.2 ;AC 0; ATAT1                 ; AT0, 1, 2          ; Adaptive Timing off, auto1*, auto2\n#v1.2 ;    ;                       ; BRD hh             ; try Baud Rate Divisor hh\n#v1.2 ;    ;                       ; BRT hh             ; set Baud Rate Timeout\n#v1.2 ;ACH ; ATSPA                 ; SP h               ; Set Protocol to h and save it\n#v1.2 ; C  ; ATDM1                 ; DM1                ; monitor for DM1 messages\n#v1.2 ; C  ; ATIFR H               ; IFR H, S           ; IFR value from Header* or Source\n#v1.2 ; C  ; ATIFR0                ; IFR0, 1, 2         ; IFRs off, auto*, or on\n#v1.2 ;AC  ; ATIIA 01              ; IIA hh             ; set ISO (slow) Init Address to hh\n#v1.2 ;AC  ; ATKW0                 ; KW0, KW1           ; Key Word checking off, or on*\n#v1.2 ; C  ; ATMP 0123             ; MP hhhh            ; Monitor for PGN 0hhhh\n#v1.2 ; C  ; ATMP 0123 4           ; MP hhhh n          ; and get n messages\n#v1.2 ; C  ; ATMP 012345           ; MP hhhhhh          ; Monitor for PGN hhhhhh\n#v1.2 ; C  ; ATMP 012345 6         ; MP hhhhhh n        ; and get n messages\n#v1.2 ;AC  ; ATSR 01               ; SR hh              ; Set the Receive address to hh\n#v1.3 ;    ; AT@2                  ; @2                 ; display the device identifier\n#v1.3 ;AC P; ATCRA 012             ; CRA hhh            ; set CAN Receive Address to hhh\n#v1.3 ;AC  ; ATCRA 01234567        ; CRA hhhhhhhh       ; set the Rx Address to hhhhhhhh\n#v1.3 ;AC  ; ATD0                  ; D0, D1             ; display of the DLC off*, or on\n#v1.3 ;AC  ; ATFE                  ; FE                 ; Forget Events\n#v1.3 ;AC  ; ATJE                  ; JE                 ; use J1939 Elm data format*\n#v1.3 ;AC  ; ATJS                  ; JS                 ; use J1939 SAE data format\n#v1.3 ;AC  ; ATKW                  ; KW                 ; display the Key Words\n#v1.3 ;AC  ; ATRA 01               ; RA hh              ; set the Receive Address to hh\n#v1.3 ;ACH ; ATSP6                 ; SP h               ; Set Protocol to h and save it\n#v1.3 ;ACH ; ATRTR                 ; RTR                ; send an RTR message\n#v1.3 ;AC  ; ATS1                  ; S0, S1             ; printing of aces off, or on* \n#v1.3 ;AC  ; ATSP 00               ; SP 00              ; Erase stored protocol\n#v1.3 ;AC  ; ATV0                  ; V0, V1             ; use of Variable DLC off*, or on\n#v1.4 ;AC  ; ATCEA                 ; CEA                ; turn off CAN Extended Addressing \n#v1.4 ;AC  ; ATCEA 01              ; CEA hh             ; use CAN Extended Address hh\n#v1.4 ;AC  ; ATCV 0000             ; CV 0000            ; restore CV value to factory setting\n#v1.4 ;AC  ; ATIB 48               ; IB 48              ; set the ISO Baud rate to 4800\n#v1.4 ;AC  ; ATIGN                 ; IGN                ; read the IgnMon input level\n#v1.4 ;    ;                       ; LP                 ; go to Low Power mode\n#v1.4 ;AC  ; ATPB 01 23            ; PB xx yy           ; Protocol B options and baud rate\n#v1.4 ;AC  ; ATRD                  ; RD                 ; Read the stored Data\n#v1.4 ;AC  ; ATSD 01               ; SD hh              ; Save Data byte hh\n#v1.4 ;ACH ; ATSP4                 ; SP h               ; Set Protocol to h and save it\n#v1.4 ;AC P; ATSI                  ; SI                 ; perform a Slow (5 baud) Initiation\n#v1.4 ;ACH ; ATZ                   ; Z                  ; reset all\n#v1.4 ;ACH ; ATSP5                 ; SP h               ; Set Protocol to h and save it\n#v1.4 ;AC P; ATFI                  ; FI                 ; perform a Fast Initiation\n#v1.4 ;ACH ; ATZ                   ; Z                  ; reset all\n#v1.4 ;AC  ; ATSS                  ; SS                 ; use Standard Search order (J1978)\n#v1.4 ;AC  ; ATTA 12               ; TA hh              ; set Tester Address to hh\n#v1.4 ;ACH ; ATSPA                 ; SP h               ; Set Protocol to h and save it\n#v1.4 ;AC  ; ATCSM1                ; CSM0, CSM1         ; Silent Monitoring off, or on* \n#v1.4 ;AC  ; ATJHF1                ; JHF0, JHF1         ; Header Formatting off, or on*\n#v1.4 ;AC  ; ATJTM1                ; JTM1               ; set Timer Multiplier to 1*\n#v1.4 ;AC  ; ATJTM5                ; JTM5               ; set Timer Multiplier to 5\n#v1.4b;AC  ; ATCRA                 ; CRA                ; reset the Receive Address filters\n#v2.0 ;AC  ; ATAMC                 ; AMC                ; display Activity Monitor Count\n#v2.0 ;AC  ; ATAMT 20              ; AMT hh             ; set the Activity Mon Timeout to hh\n#v2.1 ;AC  ; ATCTM1                ; CTM1               ; set Timer Multiplier to 1*\n#v2.1 ;AC  ; ATCTM5                ; CTM5               ; set Timer Multiplier to 5\n#v2.1 ;ACH ; ATZ                   ; Z                  ; reset all\n'
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
try:
    import androidhelper as android
    mod_globals.os = 'android'
except:
    try:
        import android
        mod_globals.os = 'android'
    except:
        pass

if mod_globals.os != 'android':
    try:
        import serial
        from serial.tools import list_ports
    except ImportError:
        sys.exit()

from mod_elm import ELM

def main():
    pyren.optParser()
    good = 0
    total = 0
    pycom = 0
    vers = ''
    res = ''
    print 'Opening ELM'
    elm = ELM(mod_globals.opt_port, mod_globals.opt_speed, mod_globals.opt_log)
    elm.portTimeout = 5
    for st in cmdb.split('#'):
        cm = st.split(';')
        if len(cm) > 1:
            if mod_globals.os == 'android' and 'A' not in cm[1].upper():
                continue
            if mod_globals.os != 'android' and 'C' not in cm[1].upper():
                continue
            if len(cm[2].strip()):
                res = elm.send_raw(cm[2])
                if 'H' in cm[1].upper():
                    continue
                total += 1
                if '?' in res:
                    chre = '[FAIL]'
                    if 'P' in cm[1].upper():
                        pycom += 1
                else:
                    chre = '[OK]'
                    good += 1
                    vers = cm[0]
                print '%5s %10s %6s' % (cm[0], cm[2], chre)
                sys.stdout.flush

    if pycom > 0:
        res = '\n\n\nUncompatible adapter on ARM core \n pyren would not work with it \n\n\n'
    res = res + '\n\n\nResult: ' + str(good) + ' from ' + str(total) + '\n Max version:' + vers + '\n\n\n\n\n\n\n'
    elm.lastMessage = res


if __name__ == '__main__':
    main()