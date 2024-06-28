
# Vineeth Thalakottoor
# vineethfrancis.physics@gmail.com

from usbtmc import *
#from pyvisa import *
import time
import RPi.GPIO as GPIO
GPIO.setmode (GPIO.BOARD)
Iput = 11
Oput = 12
GPIO.setup(Iput, GPIO.IN)
GPIO.setup(Oput, GPIO.OUT)

class AnapicoApsyn420_windows(object):
    def __init__(self, address="TCPIP0::10.10.5.124::inst0::INSTR"):
        try:
            self.address = address
            self.delay = 0.01
            self.rm = ResourceManager()
            self.device = self.rm.open_resource(self.address)
            self.status = "Connected"
            print("Connected to " + self.address)
            print("Input units: Frequency in GHz, Time in seconds")

        except VisaIOError:
            self.status = "Not Connected"
            print("PyVISA is not able to find any devices")

    def ask(self, cmd):
        response = self.device.query(cmd)
        return response.replace('\n', '')

    def write(self, cmd):
        response = self.device.write(cmd)
        time.sleep(self.delay)
        return response

    def reset(self):
        self.write('*RST')

    def power(self, status=None):
        if status is None:
            response = self.ask(':OUTP:STAT?')
            if response == '1':
                return 'Power is ON'
            else:
                return 'Power is OFF'
        else:
            self.write(':OUTP:STAT ' + status.upper())

    def cw(self, value=None):
        if value is None:
            print('Frequency Mode is ' + self.ask(':FREQ:MODE?'))
            print('Trigger Parameter,Type ' + self.ask(':TRIG:SEQ:TYPE?'))
            print('Trigger Parameter,Source ' + self.ask(':TRIG:SEQ:SOUR?'))
            print('Trigger Parameter,Slope ' + self.ask(':TRIG:SEQ:SLOP?'))
            response = self.ask(':FREQ:CW?')
            return 'Current CW Frequency is ' + response + ' Hz'
        else:
            self.write(':FREQ:MODE CW')
            self.write(':FREQ:CW ' + str(value * 1e9))
            self.write('TRIG:SEQ:TYPE GATE')
            self.write('TRIG:SEQ:SOUR EXT')
            self.write('TRIG:SEQ:SLOP POS')
            print('CW Frequency set to ' + self.ask(':FREQ:CW?') + 'Hz')

    def chirp(self, center=None):
        if center is None:
            print('Frequency Mode is ' + self.ask(':FREQ:MODE?'))
            print('Chirp Parameter, Count is ' + self.ask(':CHIR:COUN?'))
            print('Chirp Parameter, Time is ' + self.ask(':CHIR:Time?') + ' s')
            print('Chirp Parameter, Direction is ' + self.ask(':CHIR:DIR?'))
            print('Chirp Parameter, Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')
            print('Chirp Parameter,Frequency Span is ' + self.ask(':FREQ:SPAN?') + ' Hz')
            print('Chirp Parameter,Frequency Start is ' + self.ask(':FREQ:STAR?') + ' Hz')
            print('Chirp Parameter,Frequency Stop is ' + self.ask(':FREQ:STOP?') + ' Hz')
            print('Trigger Parameter,Type ' + self.ask(':TRIG:SEQ:TYPE?'))
            print('Trigger Parameter,Source ' + self.ask(':TRIG:SEQ:SOUR?'))
            print('Trigger Parameter,Slope ' + self.ask(':TRIG:SEQ:SLOP?'))
        else:
            self.write(':FREQ:MODE CHIR')
            self.write(':CHIR:COUN INF')
            self.write(':CHIR:TIME 0.001')
            self.write(':CHIR:DIR UD')
            self.write(':FREQ:CENT ' + str(center * 1e9))
            self.write(':FREQ:SPAN ' + str(0.1 * 1e9))
            #self.write('TRIG:SEQ:TYPE GATE') # EXT Trigger
            #self.write('TRIG:SEQ:SOUR EXT')
            #self.write('TRIG:SEQ:SLOP POS')


    def chirpblank(self, status=None):
        if status is None:
            response = self.ask(':CHIR:BLAN?')
            if response == '1':
                return 'Blanking ON'
            else:
                return 'Blanking OFF'
        else:
            self.write(':CHIR:BLAN ' + status.upper())
            
    def DNP_Freq(self,D1,DNP_Start,DNP_Step):
        while True:
            if GPIO.input(Iput):
                self.write(':OUTP:STAT OFF')
                self.chirp(DNP_Start)
                DNP_Start = DNP_Start + DNP_Step
                print('Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')
                self.write(':OUTP:STAT ON')
                time.sleep(1.0*D1/2.0)
            
class AnapicoApsyn420_linux(usbtmc.Instrument):
    def __init__(self,vendor=0x03eb,product=0xafff):
        super(AnapicoApsyn420_linux,self).__init__(vendor,product)
        
    def write(self,cmd):
        response=super(AnapicoApsyn420_linux,self).write(cmd +'\n')
        return response
        
    def read(self):
        response=super(AnapicoApsyn420_linux,self).read()
        return response
        
    def ask(self, cmd):
        self.write(cmd)
        response = self.read()
        return response
        
    def power(self, status=None):
        if status is None:
            response = self.ask(':OUTP:STAT?')
            if response == '1':
                print('Power is ON')
            else:
                print('Power is OFF')
        else:
            self.write(':OUTP:STAT ' + status.upper())

    def reset(self):
        self.write('*RST')

    def cw(self, value=None):
        if value is None:
            print('Frequency Mode is ' + self.ask(':FREQ:MODE?'))
            print('Trigger Parameter,Type ' + self.ask(':TRIG:SEQ:TYPE?'))
            print('Trigger Parameter,Source ' + self.ask(':TRIG:SEQ:SOUR?'))
            print('Trigger Parameter,Slope ' + self.ask(':TRIG:SEQ:SLOP?'))
            response = self.ask(':FREQ:CW?')
            return 'Current CW Frequency is ' + response + ' Hz'
        else:
            self.write(':FREQ:MODE CW')
            self.write(':FREQ:CW ' + str(value * 1e9))
            self.write('TRIG:SEQ:TYPE GATE')
            self.write('TRIG:SEQ:SOUR EXT')
            self.write('TRIG:SEQ:SLOP POS')
            print('CW Frequency set to ' + self.ask(':FREQ:CW?') + 'Hz')

    def chirp(self, center=None):
        if center is None:
            print('Frequency Mode is ' + self.ask(':FREQ:MODE?'))
            print('Chirp Parameter, Count is ' + self.ask(':CHIR:COUN?'))
            print('Chirp Parameter, Time is ' + self.ask(':CHIR:Time?') + ' s')
            print('Chirp Parameter, Direction is ' + self.ask(':CHIR:DIR?'))
            print('Chirp Parameter, Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')
            print('Chirp Parameter,Frequency Span is ' + self.ask(':FREQ:SPAN?') + ' Hz')
            print('Chirp Parameter,Frequency Start is ' + self.ask(':FREQ:STAR?') + ' Hz')
            print('Chirp Parameter,Frequency Stop is ' + self.ask(':FREQ:STOP?') + ' Hz')
            print('Trigger Parameter,Type ' + self.ask(':TRIG:SEQ:TYPE?'))
            print('Trigger Parameter,Source ' + self.ask(':TRIG:SEQ:SOUR?'))
            print('Trigger Parameter,Slope ' + self.ask(':TRIG:SEQ:SLOP?'))
        else:
            self.write(':FREQ:MODE CHIR')
            self.write(':CHIR:COUN INF')
            self.write(':CHIR:TIME 0.001')
            self.write(':CHIR:DIR UD')
            self.write(':FREQ:CENT ' + str(center * 1e9))
            self.write(':FREQ:SPAN ' + str(0.001 * 1e9))
            self.write('TRIG:SEQ:TYPE GATE') # EXT Trigger
            self.write('TRIG:SEQ:SOUR EXT')
            self.write('TRIG:SEQ:SLOP POS')
            print('Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')

    def PulseMod(self, center=None):
        if center is None:
            print('Frequency Mode is ' + self.ask(':FREQ:MODE?'))
            print('Chirp Parameter, Count is ' + self.ask(':CHIR:COUN?'))
            print('Chirp Parameter, Time is ' + self.ask(':CHIR:Time?') + ' s')
            print('Chirp Parameter, Direction is ' + self.ask(':CHIR:DIR?'))
            print('Chirp Parameter, Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')
            print('Chirp Parameter,Frequency Span is ' + self.ask(':FREQ:SPAN?') + ' Hz')
            print('Chirp Parameter,Frequency Start is ' + self.ask(':FREQ:STAR?') + ' Hz')
            print('Chirp Parameter,Frequency Stop is ' + self.ask(':FREQ:STOP?') + ' Hz')
            print('Trigger Parameter,Type ' + self.ask(':TRIG:SEQ:TYPE?'))
            print('Trigger Parameter,Source ' + self.ask(':TRIG:SEQ:SOUR?'))
            print('Trigger Parameter,Slope ' + self.ask(':TRIG:SEQ:SLOP?'))
        else:
            self.write(':FREQ:MODE CHIR')
            self.write(':CHIR:COUN INF')
            self.write(':CHIR:TIME 0.001')
            self.write(':CHIR:DIR UD')
            self.write(':FREQ:CENT ' + str(center * 1e9))
            self.write(':FREQ:SPAN ' + str(0.001 * 1e9))
            self.write('TRIG:SEQ:TYPE GATE') # EXT Trigger
            self.write('TRIG:SEQ:SOUR EXT')
            self.write('TRIG:SEQ:SLOP POS')
            print('Central Frequency is ' + self.ask(':FREQ:CENT?') + ' Hz')

    def blanking(self, status=None):
        if status is None:
            response = self.ask(':CHIR:BLAN?')
            if response == '1':
                return 'Blanking ON'
            else:
                return 'Blanking OFF'
        else:
            self.write(':CHIR:BLAN ' + status.upper())
            
    def DNP_Freq(self,D1,DNP_Start,DNP_Step):
        try:
            while True:
                if GPIO.input(Iput):
                    self.write(':OUTP:STAT OFF')
                    #self.chirp(DNP_Start)
                    self.cw(DNP_Start)
                    DNP_Start = DNP_Start + DNP_Step
                    self.write(':OUTP:STAT ON')
                    time.sleep(1.0*D1/2.0)  
        except KeyboardInterrupt:
            self.write(':OUTP:STAT OFF')
            self.power()

    def OnOffMW(self,Iput):
        self.write(':OUTP:STAT OFF')
        time.sleep(Depr/2.0)
        self.write(':OUTP:STAT ON') 
            
    def OnOffTrigout(self,value,delay):
        self.cw(value)
        try:
            while True:
                GPIO.output(Oput,1)
                self.write(':OUTP:STAT ON')
                time.sleep(delay/2.0)
                GPIO.output(Oput,0)
                self.write(':OUTP:STAT OFF')                          
                time.sleep(delay/2.0)
        except KeyboardInterrupt:
            self.write(':OUTP:STAT OFF')
            self.power()
            #GPIO.cleanup()
                
    def EPR_DNP_TrigIn(self,value,Delay):
        global Depr
        Depr = Delay
        self.cw(value)
        GPIO.add_event_detect(Iput,GPIO.RISING,callback = self.OnOffMW)
        self.write(':OUTP:STAT ON')
        try:
            while True:
                i = 0                     
        except KeyboardInterrupt:
            self.write(':OUTP:STAT OFF')
            self.power()
            GPIO.cleanup()

#device = AnapicoApsyn420()
#device.chirp(2)
#device.power('On')
