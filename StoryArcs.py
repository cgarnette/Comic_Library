import os
import re
import sys
import time

import PIL.Image
import requests
from bs4 import BeautifulSoup as bs
from lxml import html
from PIL import ImageTk

from Book import Book

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    from Tkinter import *
    from Tkinter import ttk
else:
    from tkinter import *
    from tkinter import ttk
    import tkinter

class StoryArcs(Frame):

    def __init__(self, master, root, publisher):
        self.master = master
        Frame.__init__(self, master)
        self.root = root
        self.setup(publisher)
        self.pack(fill=BOTH, expand=1)

    def setup(self, publisher):
        self.nb = ttk.Notebook(self)
        self.nb.grid(row=1, column=0)

        #Command to get list of story arc eras
        #Maybe save the eras in a textfile and just run one quick recheck each time the program starts
        #For each era in the list run the following loop:
            # create a new EraFrame
            # In the era frame load all story arcs associated with that era
            # each arc will be a button that is associated with a list of issues within that arc
            # The program will have to access the web each time for a list of arcs and issues
            # There will be an option to save arcs to favorites. Those arcs will not require internet.

        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..//bin'))

        if publisher is "DC":
            with open(path + "//dc.txt") as myFile:
                eras = [x.strip() for x in myFile.readlines()]
        elif publisher is "Marvel":
            with open(path + "//marvel.txt") as myFile:
                eras = [x.strip() for x in myFile.readlines()]

        nums = list()
        for i in range(0, len(eras), 1):
            nums.append(i)

        results = zip(nums, eras)
        eraDict = dict()

        for num, era in results:
            eraDict[num] = era

        for num in nums:
            frame = EraFrame(self.nb, self.root, publisher)
            frame.list_arcs(self.get_comic_arcs(publisher, num))
            self.nb.add(frame, text=eraDict[num])

    def get_comic_arcs(self, publisher, era):

        if publisher is "DC":
            page = requests.get('https://en.wikipedia.org/wiki/Publication_history_of_DC_Comics_crossover_events')
            tree = html.fromstring(page.content)
            soup = bs(page.content, 'lxml')

            tables = [x for x in soup.find_all('table')]
            rows = [row for row in tables[era].find_all('tr')]

        elif publisher is "Marvel":
            page = requests.get('https://en.wikipedia.org/wiki/Publication_history_of_Marvel_Comics_crossover_events')
            tree = html.fromstring(page.content)
            soup = bs(page.content, 'lxml')

            tables = [x for x in soup.find_all('table')]

            b = list()
            for table in tables:
                try:
                    if table.find('b').getText().lower() == "event":
                        b.append(table)
                except:
                    pass

            tables = b.copy()
            rows = [row for row in tables[era].find_all('tr')]
            del rows[0]
        
        arcs = list()

        for row in rows:
            currCell = row.find('td')
            links = currCell.find_all('a')
            name = ''

            try:
                name = currCell.getText()
            except:
                if(len(links) > 0):
                    for link in links:
                        try:
                            name = name + link.getText()
                        except:
                            pass
                if name == '':
                    try:
                        name = name + currCell.find('i').getText()
                    except:
                        pass
            arcs.append(name)

        return arcs


class EraFrame(Frame): #Each tab will have one of these frames which will have all story arcs for whatever era it is

    def __init__(self, master, root, publisher):
        self.master = master
        Frame.__init__(self, master)
        self.root = root
        self.publisher = publisher
        self.buildCanvas()
        self.pack(fill=BOTH, expand=1)

    def buildCanvas(self):
        rWidth = self.master.master.winfo_screenwidth()
        rHeight = self.master.master.winfo_screenheight()-35

        self.canv = Canvas(self, width=rWidth - 15, height=rHeight)
        self.canv.config(width=rWidth, height=rHeight)                
        self.canv.config(scrollregion=self.canv.bbox("all"))

        sbar = Scrollbar(self)
        sbar.config(command=self.canv.yview)                   
        self.canv.config(yscrollcommand=sbar.set)              
        sbar.pack(side=RIGHT, fill=Y)              
        self.canv.pack_propagate(False)       
        self.canv.pack(side="top", expand=YES, fill=BOTH)

        self.createInnerFrame()
        #self.orientCanvas()

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
        self.currentFrame.pack(fill=BOTH, expand=1)
        #self.currentFrame.pack()

    def orientCanvas(self):
        self.interior_id = self.canv.create_window((0,0), window=self.currentFrame, anchor='nw')
        self.currentFrame.bind('<Configure>', self._configure_interior)
        self.canv.bind('<Configure>', self._configure_canvas)
        #self.frame.canv.configure(scrollregion = self.frame.bbox("all"))


    def list_arcs(self, arcs):
        self.currentFrame.grid_forget()
        self.currentFrame.destroy()
        self.createInnerFrame()

        try:
            testconnection = requests.get('http://www.google.com')
            resp = testconnection.status_code
            if int(resp) is not 200:
                lbl = Label(self.currentFrame, text='Connection Error', font=("Calibri Bold", 40), borderwidth=0)
                lbl.grid(column=0, row=0, columnspan=6)
                return None
        except:
            lbl = Label(self.currentFrame, text='Connection Error', font=("Calibri Bold", 40), borderwidth=0)
            lbl.grid(column=0, row=0, columnspan=6)
            return None

        
        lbl = Label(self.currentFrame, text="Story Arcs\t\t\t\t", font=("Calibri Bold", 40), pady=30)
        lbl.grid(column=0, row=0, columnspan=6)

        for x in range(0, len(arcs), 1):
            option = Label(self.currentFrame, text=arcs[x], font=('Arial', 15), pady=15)
            option.grid(column= 0, row= x+1, sticky=W)

            button = Button(self.currentFrame, text="Select",font=('Arial', 15), pady=15, command= lambda x=x: self.test_print(arcs[x]))
            button.grid(column= 1, row=x+1, sticky=W)

        #load = PIL.Image.open(os.path.dirname(os.path.realpath(__file__)) + '\\config\\images\\iconbkgrd.jpg')
        #render = ImageTk.PhotoImage(load)
        #buffer = Label(self.currentFrame, text='', pady=30, borderwidth=0)
        #buffer.image = render
        #buffer.grid(column=0, row=len(stories)+2, columnspan=6)
        self.orientCanvas()

    def test_print(self, title):
        print(title)
        title = title + "-reading-order"
        #Superman Reborn Reading Order
        print(self.show_reading_order(title, self.publisher))


    def show_reading_order(self, url, publisher):
        if publisher is "Marvel":
            page = requests.get('https://comicbookreadingorders.com/marvel/events/'+ url.replace(' ', '-').replace(':','').lower() + '/')
        elif publisher is "DC":
            page = requests.get('https://comicbookreadingorders.com/dc/events/'+ url.replace(' ', '-').replace(':','').lower() + '/')
        
        soup = bs(page.content, 'lxml')
        titles = list()
        try:
            div = soup.find("div", {"class": "x-text cs-ta-left mbl"})
            titles = [x.getText() for x in div.find_all('p')]
        except:
            try:
                div = soup.find("div", {"class": "x-tab-content"})
                paras = [x for x in div.find_all('p')]
                for x in paras:
                    y = str(x)
                    first = y.split('</span>')[0]
                    title = re.search(r'>+([a-zA-Z]+.*:*\s*#*[0-9]*)+', first)
                    titles.append(title.group(0).replace('>', ''))
            except:
                if publisher is "Marvel":
                    try:
                        div = soup.find("div", {"class": "x-text left-text mbl"})
                        titles = [x.getText() for x in div.find_all('p')]
                    except:
                        pass
                if publisher is "DC":
                    pass
        if(len(titles) < 1):
            try:
                search_path = "https://comicbookreadingorders.com/?s=" + url.replace(' ','+').replace(':','').lower()
                page = requests.get(search_path)
                tree = html.fromstring(page.content)
                soup = bs(page.content, 'lxml')

                search_result = soup.find('header', {'class': 'entry-header'})
                link = search_result.find('a', href=True)
                print(link['href'])
            except:
                return None

        return titles
