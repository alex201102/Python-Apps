#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
import ttk
import tkFileDialog
import serial
import serial.tools.list_ports;
import time
#import sys

class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()

        self.filePathVariable = Tkinter.StringVar()
        self.filePath = Tkinter.Entry(self,textvariable=self.filePathVariable)
        self.filePath.grid(column=0,row=1,columnspan=4,sticky='EW')
        self.filePathVariable.set(u"log.txt")

        self.buttonRefresh = Tkinter.Button(self,text=u"Refresh",
                                command=self.OnButtonRefreshClick)
        self.buttonRefresh.grid(column=3,row=2,columnspan=1,sticky='EW')

        self.labelSelectPortVariable = Tkinter.StringVar()
        self.labelSelectPort = Tkinter.Label(self,textvariable=self.labelSelectPortVariable)
        self.labelSelectPort.grid(column=0,row=2,sticky='W')
        self.labelSelectPortVariable.set(u"Port:")

        self.boxValue = Tkinter.StringVar()
        self.box = ttk.Combobox(self, textvariable=self.boxValue)
        self.box['values'] = self.RefreshPortList()
        self.box.configure(state="readonly")
        self.box.current(0)
        self.box.grid(column=1,row=2,columnspan=1,sticky='W')
        
        self.labelStatusVariable = Tkinter.StringVar()
        self.labelStatus = Tkinter.Label(self,textvariable=self.labelStatusVariable,
                              anchor="w",fg="white",bg="blue")
        self.labelStatus.grid(column=0,row=5,columnspan=4,sticky='EW')
        self.labelStatusVariable.set(u"Ready")

        self.buttonBrowse = Tkinter.Button(self,text=u"Browse",command=self.LoadFile)
        self.buttonBrowse.grid(column=3,row=0,sticky='E')

        self.workMode = Tkinter.IntVar()

        self.radioSend = Tkinter.Radiobutton(self, text="Send", variable=self.workMode, value=1)
        self.radioSend.grid(column=1,row=0,sticky='EW')
        
        self.radioSave = Tkinter.Radiobutton(self, text="Save", variable=self.workMode, value=2)                          #command=sel)
        self.radioSave.grid(column=2,row=0,sticky='W')

        self.radioSave.select()

        self.labelSelectVariable = Tkinter.StringVar()
        self.labelSelect = Tkinter.Label(self,textvariable=self.labelSelectVariable)
        self.labelSelect.grid(column=0,row=0,sticky='W')
        self.labelSelectVariable.set(u"Select path for:")

        self.logText = Tkinter.Text(self, height=10, width=38)
        self.scrollBar = Tkinter.Scrollbar(self)
        self.scrollBar.grid(column=3,row=3,columnspan=1,sticky='ENS')
        self.scrollBar.config(command=self.logText.yview)
        self.logText.config(yscrollcommand=self.scrollBar.set)
        self.logText.grid(column=0,row=3,columnspan=4,sticky='W')
        self.logText.configure(state="disabled")

        self.buttonClearLog = Tkinter.Button(self,text=u"Clear Log",
                                command=self.OnButtonClearLogClick)
        self.buttonClearLog.grid(column=2,row=4,columnspan=2,sticky='EW')

        self.buttonStart = Tkinter.Button(self,text=u"Start",
                                command=self.OnButtonStartClick)
        self.buttonStart.grid(column=0,row=4,columnspan=2,sticky='EW')
        
        self.grid_columnconfigure(0,weight=1)
        self.resizable(False,False)

        self.update()        
        self.geometry(self.geometry())
        self.filePath.focus_set()

    def ReadFromFile(self):
        path = self.filePathVariable.get()

        if path != "":

            outputToLog = ''
            
            try:
                inputFile=open(path,"r")
                fileToSend = inputFile.read()
                inputFile.close()

                ser = serial.Serial()
                ser.port = str(self.box.get())

                ser.close()
                ser.open()

                time.sleep(5)

                for c in fileToSend:
                    ser.write(c)
                    while True:
                        bytesToRead = ser.inWaiting()
                        if bytesToRead != 0:
                            outputToLog += ser.read(bytesToRead)
                            #sys.stdout.write(ser.read(bytesToRead))
                            #sys.stdout.flush()
                        else:
                            time.sleep(1)
                            bytesToRead = ser.inWaiting()
                            if bytesToRead == 0:
                                break # There is no more data to read, stop the loop
                            else:
                                outputToLog += ser.read(bytesToRead)
                                #sys.stdout.write(ser.read(bytesToRead))
                                #sys.stdout.flush()

                ser.close()
                
            except Exception, ex:
                outputToLog += '\n' + 'Error: ' + str(ex);
                #print("Error: " + str(ex))

            self.logText.configure(state="normal")
            self.logText.insert(Tkinter.END, outputToLog)
            self.logText.configure(state="disabled")
                
            return
        
    def WriteToFile(self):
        path = self.filePathVariable.get()

        if path != "":

            printStr=''
            
            try:
                outputFile = open(path,'w')
                
                ser = serial.Serial()
                ser.port = str(self.box.get())#'COM5'

                ser.close()
                ser.open()

                time.sleep(5)
                ser.write('p')
                time.sleep(1)

                while True:
                    bytesToRead = ser.inWaiting()
                    if bytesToRead != 0:
                        text = ser.read(bytesToRead)
                        #sys.stdout.write(text)
                        #sys.stdout.flush()
                        printStr += text
                        if '--' in text:
                            ser.write(' ')
                            time.sleep(1)
                    else:
                        time.sleep(1)
                        bytesToRead = ser.inWaiting()
                        if bytesToRead == 0:
                            break # There is no more data to read, stop the loop
                        else:
                            text = ser.read(bytesToRead)
                            #sys.stdout.write(text)
                            #sys.stdout.flush()
                            printStr += text
                            if '--' in text:
                                ser.write(' ')

                ser.close()

                outputFile.write(printStr)
                outputFile.close()
                
            except Exception, ex:
                printStr += '\n' + 'Error: ' + str(ex)
                #print("Error: " + str(ex))

            self.logText.configure(state="normal")
            self.logText.insert(Tkinter.END, printStr)
            self.logText.configure(state="disabled")
            
            return

    def RefreshPortList(self):
        return [i.device for i in serial.tools.list_ports.comports()]

    def OnButtonRefreshClick(self):
        self.box['values'] = self.RefreshPortList()
        self.box.current(0)
        self.update()

    def OnButtonClearLogClick(self):
        self.logText.configure(state="normal")
        self.logText.delete(1.0, Tkinter.END)
        self.logText.configure(state="disabled")
        self.update()

    def OnButtonStartClick(self):
        self.labelStatusVariable.set("Running...")
        self.update()
        self.filePath.focus_set()
        
        if self.workMode.get() == 1:
            self.ReadFromFile()
        else:
            self.WriteToFile()
            
        self.labelStatusVariable.set("Ready")
        self.update()
        
    def LoadFile(self):
        if self.workMode.get() == 1:
            fname = tkFileDialog.askopenfilename(filetypes=(("Text files", "*.txt"),
                                                            ("All files", "*.*") ))
        else:
            fname = tkFileDialog.asksaveasfilename(filetypes=(("Text files", "*.txt"),
                                                              ("All files", "*.*") ))
            
        if fname:
            try:
                self.filePathVariable.set(fname)
            except:
                self.logText.configure(state="normal")
                self.logText.insert(Tkinter.END, "Open Source File: Failed to read file: " + fname)
                self.logText.configure(state="disabled")
            return

if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Command Sender')
    app.mainloop()
