#!/usr/bin/env python
# encoding: utf-8

import wx, os
from pyo import *

server = Server(sr=44100, nchnls=2, buffersize=512, duplex=1).boot()

WITH_GUI = True
########################
###soundbank##############
snds = ["smpl/01.wav", "smpl/02.wav", "smpl/03.wav"]
########################
###dictionnaire presets########
presets = {"khalif": {"taps": 5, "pulses": 2},
                "cumbia": {"taps": 4, "pulses": 3},
                "ruchenitza": {"taps": 7, "pulses": 3},                
                "tresillo": {"taps": 8, "pulses": 3},
                "ruchenitza2": {"taps": 7, "pulses": 4},
                "aksak": {"taps": 9, "pulses": 4},
                "zappa": {"taps": 11, "pulses": 4},
                "york": {"taps": 6, "pulses": 5}, 
                "nawakhat": {"taps": 7, "pulses": 5},
                "cinquillo": {"taps": 8, "pulses": 5},
                "agsag": {"taps": 9, "pulses": 5},
                "moussorgsky": {"taps": 11, "pulses": 5},
                "venda": {"taps": 12, "pulses": 5},
                "bossa": {"taps": 16, "pulses": 5},
                "bendir": {"taps": 8, "pulses": 7},
                "west-africa": {"taps": 12, "pulses": 7},
                "central-africa": {"taps": 16, "pulses": 9}
                }
########################
########################               
class Voix :
    def __init__(self, path=snds[0], vol=0.75, pan=.5, bpm=160, taps=8, pulses=3, pitch=2, HPfreq=40, LPfreq=20000) :
        self.sample= SndTable(path)
        self.dur= self.sample.getDur()
        self.volume = Sig(vol)
        self.pan = Sig(pan)
        self.bpm = Sig(bpm)
        self.pitch = Sig(pitch)
        self.HPfreq = Sig(HPfreq)
        self.LPfreq = Sig(LPfreq)
        self.time = (30000/self.bpm)*0.001
        self.tap = taps
        self.pulse = pulses
        self.pitpit= self.dur * self.pitch
        self.trig= Euclide(time=self.time, taps=taps, onsets=pulses).play()
        self.tuti= TrigEnv(self.trig, self.sample, dur=self.pitpit, mul=self.volume)
        self.HPbandpass = ButHP(self.tuti, freq=self.HPfreq)
        self.LPbandpass = ButLP(self.HPbandpass, freq = self.LPfreq)
        self.ou = Pan(self.LPbandpass, outs=2, pan=self.pan)
                                     
    def setPath(self, x):
        self.sample.path = x  

    def setVol(self, x):
        self.volume.value = x

    def setPan(self, x):
        self.pan.value = x

    def setBPM(self, x):
        self.bpm.value = x
        
    def setPitch(self, x):
        self.pitch.value = x

    def setHP(self, x):
        self.HPfreq.value = x

    def setLP(self, x):
        self.LPfreq.value = x

    def setTaps(self, x):
        self.trig.taps = x
    
    def setPulses(self, x):
        self.trig.onsets = x
        
    def choose(self, preset_name):
        preset = presets[preset_name]
        taps = preset["taps"]
        pulses = preset["pulses"]
        self.setTaps(taps)
        self.setPulses(pulses)   
            

    def stop(self):
        self.trig.stop()
        return self    

    def play(self):
        self.trig.play()
        
    def out(self):
        self.ou.out()
        return self
        

########################################
#####GRAPHIQUES#########################
if WITH_GUI:
    class MyFrame(wx.Frame):
        def __init__(self, parent, title, pos, size, audio):
            wx.Frame.__init__(self, parent, id=-1, title=title, pos=pos, size=size)
            self.audio = audio
            self.panel = wx.Panel(self)
            self.panel.SetBackgroundColour("#LSD12V")
###Set to play###
            self.onOffText = wx.StaticText(self.panel, id=-1, label="tic tic toc tic", 
                                                    pos=(10,10), size=wx.DefaultSize)
            self.onOff = wx.ToggleButton(self.panel, id=-1, label="I-O", 
                                                pos=(8,27), size=wx.DefaultSize)
            self.onOff.Bind(wx.EVT_TOGGLEBUTTON, self.handleAudio)

###choose sample###       
            sample = [f for f in os.listdir(os.getcwd()) if f[-4:] in ['.wav']]
            self.smplText = wx.StaticText(self.panel, id=-1, label="Son", 
                                                    pos=(10,103), size=wx.DefaultSize)
            self.smpl = wx.Choice(self.panel, id=-1, pos=(8,120), 
                                        size=wx.DefaultSize, choices=sample)
            self.smpl.Bind(wx.EVT_CHOICE, self.setSound)

###choose rythm###
            self.popupText = wx.StaticText(self.panel, id=-1, label="Rythme", 
                                                    pos=(10,60), size=wx.DefaultSize)
            self.popup = wx.Choice(self.panel, id=-1, pos=(8,77), size=wx.DefaultSize, 
                                        choices=presets.keys())
            self.popup.Bind(wx.EVT_CHOICE, self.setRythm)
###set Pitch###
            self.pitText = wx.StaticText(self.panel, id=-1, label="Pitch : 1.0", 
                                               pos=(10, 188), size=wx.DefaultSize)
            self.pit= wx.Slider(self.panel, id=-1, value=1000, minValue=100, 
                                 maxValue=4000, pos=(10, 203), size=wx.DefaultSize)
            self.pit.Bind(wx.EVT_SLIDER, self.changePitch)
###set Volume###
            self.volText = wx.StaticText(self.panel, id=-1, label="Volume : 1.0",
                                                pos=(10, 149), size=wx.DefaultSize)
            self.vol= wx.Slider(self.panel, id=-1, value=1000, minValue=1, 
                                  maxValue=2000, pos=(10, 164), size=wx.DefaultSize)
            self.vol.Bind(wx.EVT_SLIDER, self.changeVolume)
###set Pan###
            self.panText = wx.StaticText(self.panel, id=-1, label="Left : Right",
                                                pos=(10, 228), size=wx.DefaultSize)
            self.pan= wx.Slider(self.panel, id=-1, value=50, minValue=1, 
                                  maxValue=100, pos=(10, 243), size=wx.DefaultSize)
            self.pan.Bind(wx.EVT_SLIDER, self.changePan)
###set BPM###
            self.bpmText = wx.StaticText(self.panel, id=-1, label="BPM : 160",
                                                pos=(10, 267), size=wx.DefaultSize)
            self.bpm= wx.Slider(self.panel, id=-1, value=1600, minValue=100, 
                                  maxValue=4000, pos=(10,282), size=wx.DefaultSize)
            self.bpm.Bind(wx.EVT_SLIDER, self.changeBPM)
###setHP###
            self.hpText = wx.StaticText(self.panel, id=-1, label="Highpass : 40",
                                                pos=(10, 305), size=wx.DefaultSize)
            self.hp= wx.Slider(self.panel, id=-1, value=40, minValue=40, 
                                  maxValue=20000, pos=(10,320), size=wx.DefaultSize)
            self.hp.Bind(wx.EVT_SLIDER, self.changeHP)
###setLP###        
            self.lpText = wx.StaticText(self.panel, id=-1, label="Lowpass : 20000",
                                                pos=(10, 345), size=wx.DefaultSize)
            self.lp= wx.Slider(self.panel, id=-1, value=20000, minValue=40, 
                                  maxValue=20000, pos=(10,360), size=wx.DefaultSize)
            self.lp.Bind(wx.EVT_SLIDER, self.changeLP)            

        def handleAudio(self, evt):
            if evt.GetInt() == 1:
                server.start()
            else:
                server.stop()
        
        def setSound(self, evt):
            x = self.pit.GetValue()*0.001 
            self.audio.sample.path = os.getcwd() + "/smpl/" + evt.GetString()
            self.audio.dur= self.audio.sample.getDur() * x
        
                
        def setRythm(self, evt):
            preset = presets[evt.GetString()]
            taps = preset["taps"]
            pulses = preset["pulses"]
            self.audio.setTaps(taps)
            self.audio.setPulses(pulses)   
        
        def changePitch(self, evt):
            x = evt.GetInt() * 0.001
            self.pitText.SetLabel("Pitch : %.3f" % x)
            self.audio.tuti.dur = self.audio.sample.getDur() * x
        
        def changeVolume(self, evt):
            x = evt.GetInt() * 0.001
            self.volText.SetLabel("Volume : %.2f" % x)
            self.audio.volume.value = x
        
        def changePan(self, evt):
            x = evt.GetInt() * 0.01
            self.audio.pan.value = x

        def changeBPM(self, evt):
            x = evt.GetInt() * 0.1
            self.bpmText.SetLabel("BPM : %.2f" % x)
            self.audio.bpm.value = x
        
        def changeHP(self, evt):
            x = evt.GetInt()
            self.hpText.SetLabel("Highpass : %f" % x)
            self.audio.HPfreq.value = x

        def changeLP(self, evt):
            x = evt.GetInt()
            self.lpText.SetLabel("Lowpass : %f" % x)
            self.audio.LPfreq.value = x

    app = wx.App()

    audio = Voix().out()

    mainFrame = MyFrame(parent=None, title="polyrythmie eucledienne", 
                               pos=(700,200), size=(150,430), audio=audio)
    mainFrame.Show()

    app.MainLoop()
    
else:
    rt= Voix().out()
    tt= Voix().out()
    server.gui(locals())