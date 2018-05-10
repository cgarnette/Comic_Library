import os
import sys
import time

import shutil
from PIL import ImageTk
import PIL.Image

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    from Tkinter import *
    from Tkinter import ttk
else:
    from tkinter import *
    from tkinter import ttk

class Book:
    def __init__(self, master=None):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack()
        self.full = False

    def FullScreen(self, issue):
        self.full = True
        self.showPage(issue)

    def showPage(self, issue, i=1):
        self.clearFrame()
        w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.master.overrideredirect(1)

        more = False
        for t in range(i, i+3, 1):
            try:
                load = PIL.Image.open(issue + "\\"+str(t)+".jpg")
                more = True
                i = t
                break
            except:
                pass

        if(more is False):
            exit = Button(self.frame, text="Exit", command= lambda: self.Exit())
            back = Button(self.frame, text='Back', command= lambda: self.showPage(issue, i-1))
            exit.pack()
            back.pack()

        elif(self.full):
            height = w
            width = int(load.size[0] * (height/load.size[1])) if load.size[1] > h else h
            load = load.resize((width, height), PIL.Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)
            img = Button(self.frame, image=render, command= lambda: self.showPage(issue, i+1))
            img.image = render
            img.pack()
            self.master.focus_set()    
            self.master.bind("<Escape>", lambda e: self.master.destroy())
        else:
            width = int(h/2)
            height = int(load.size[1] * (width/load.size[0]))

            load = load.resize((width, height), PIL.Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)
            img = Button(self.frame, image=render, command= lambda: self.showPage(issue, i+1))
            fullscreen = Button(self.frame, text="Full Screen", command= lambda: self.FullScreen(issue))
            exit = Button(self.frame, text="Exit", command= lambda: self.Exit())
            back = Button(self.frame, text='Back', command= lambda: self.showPage(issue, i-1))
            img.image = render
            img.pack()
            fullscreen.pack()
            exit.pack()
            back.pack()
            self.master.focus_set()    
            self.master.bind("<Escape>", lambda e: self.master.destroy())

    def clearFrame(self):
        for child in self.frame.winfo_children():
            child.destroy()
    
    def Exit(self):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..','Comics\\temp')
        try:
            shutil.rmtree(dir_path, ignore_errors=True)
        except:
            pass
        self.master.destroy()