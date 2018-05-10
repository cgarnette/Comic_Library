import os
import sys
import time
import pandas as pd

from PIL import ImageTk
import PIL.Image
from Book import Book

from bs4 import BeautifulSoup as bs
from lxml import html
from PIL import ImageTk

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    from Tkinter import *
    from Tkinter import ttk
else:
    from tkinter import *
    from tkinter import ttk
    import tkinter


class ComicDisplay(Frame):

    def __init__(self, master, root, df=None):
        self.master = master
        Frame.__init__(self, master)
        self.root = root
        self.df = df
        self.build_frame()
        self.buildCanvas()
        self.show_comics()
        self.pack(fill=BOTH, expand=1)

    def build_frame(self):
        
        rWidth = self.master.master.winfo_screenwidth()
        rHeight = self.master.master.winfo_screenheight()-35
        self.image_width = int(rWidth * .1333)
        self.xpad = int((15/200)*self.image_width)

        self.max = int(self.master.winfo_screenwidth()/(self.image_width + (2*self.xpad)))
        p = int(self.master.winfo_screenwidth() - (self.max * (self.image_width + (2*self.xpad))))
        self.pad =  int(p - ((1/3)* p))

    def buildCanvas(self):

        rWidth = self.master.master.winfo_screenwidth()
        rHeight = self.master.master.winfo_screenheight()-35

        # 0.1333 is the ratio of image width to screen width
        self.canv = Canvas(self)
        self.canv.config(width=rWidth, height=rHeight)                
        self.canv.config(scrollregion=self.canv.bbox("all"))

        sbar = Scrollbar(self)
        sbar.config(command=self.canv.yview)                   
        self.canv.config(yscrollcommand=sbar.set)              
        sbar.pack(side=RIGHT, fill=Y)                     
        self.canv.pack(side=LEFT, expand=YES, fill=BOTH)

        self.createInnerFrame()
        self.orientCanvas()

        self.canv.xview_moveto(0)
        self.canv.yview_moveto(0)


    def _configure_interior(self, event):
            # update the scrollbars to match the size of the inner frame
            size = (self.currentFrame.winfo_reqwidth(), self.currentFrame.winfo_reqheight())
            self.canv.config(scrollregion="0 0 %s %s" % size)
            if self.currentFrame.winfo_reqwidth() != self.canv.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canv.config(width=self.currentFrame.winfo_reqwidth())

    def _configure_canvas(self, event):
            if self.currentFrame.winfo_reqwidth() != self.canv.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canv.itemconfigure(self.interior_id, width=self.canv.winfo_width())

    def createInnerFrame(self):
        self.currentFrame = Frame(self.canv)
        self.currentFrame.pack()

    def orientCanvas(self):
        self.interior_id = self.canv.create_window((0,0), window=self.currentFrame, anchor='nw')
        self.currentFrame.bind('<Configure>', self._configure_interior)
        self.canv.bind('<Configure>', self._configure_canvas)


    def show_comics(self, restrictions=None, df=None):
        self.currentFrame.grid_forget()
        self.currentFrame.destroy()
        self.createInnerFrame()

        if df is not None:
            self.df = df

        counter = 0
        currRow = 0

        for x in range(0, len(self.df), 1):

            row = self.df.iloc[x]
            path = row['Path']
            title = row['Title']

            # Get first issue in folder
            # We need to drill down till we hit the folder with numerical indexing

            cover_issue = [int(x) if '.' not in x else None for x in os.listdir(path)]
            path = path + '\\' + str(sorted(cover_issue, reverse=True)[0])

            dir_path = os.path.abspath(os.path.join(path, '..//'))

            file_list = [int(str(x).replace('.jpg', '')) for x in os.listdir(path)]
            file_list = sorted(file_list)

            load = PIL.Image.open(path +"\\" +str(file_list[0]) + '.jpg')
            
            height = int(load.size[1] * (self.image_width/load.size[0]))

            load = load.resize((self.image_width, height), PIL.Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)

            img = Button(self.currentFrame, image=render, padx=1000, pady=500, command= lambda bound_dir_path=dir_path: self.show_issues(bound_dir_path))
            img.image = render
            img.grid(column=counter, row=currRow, padx=self.xpad if counter+1 is not self.max else (self.xpad,self.pad), pady=(30, 0))

            series = Label(self.currentFrame, text=title)
            series.grid(column=counter, row=currRow+1)

            counter = counter + 1
            
            if(self.max == counter):
                currRow = currRow + 2
                counter = 0

    def show_issues(self, path):

        #path should be ../Comics/*Series Title*
        self.currentFrame.grid_forget()
        self.currentFrame.destroy()
        self.createInnerFrame()

        counter = 0
        currRow = 0
        for issue in os.listdir(path):
            num = int(str(issue).replace('.jpg','').strip())
            load = PIL.Image.open(path + '\\' + issue)
            
            height = int(load.size[1] * (self.image_width/load.size[0]))

            load = load.resize((self.image_width, height), PIL.Image.ANTIALIAS)
            render = ImageTk.PhotoImage(load)

            img = Button(self.currentFrame, image=render, padx=1000, pady=500)#, command= lambda o=o: master.selectIssue(seriesPath+'\\'+str(o)))
            img.image = render
            img.grid(column=counter, row=currRow, padx=self.xpad if counter+1 is not self.max else (self.xpad,self.pad), pady=(30, 0))

            series = Label(self.currentFrame, text='Issue #' + str(num))
            series.grid(column=counter, row=currRow+1)

            counter = counter + 1
            
            if(self.max == counter):
                currRow = currRow + 2
                counter = 0


    def new_window(self):
        self.newWindow = Toplevel(self.root)
        self.app = Book(self.newWindow)