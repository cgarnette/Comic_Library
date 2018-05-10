import os
import sys
import time

import pandas as pd
import requests

from Add import Add_Series_Window
from Book import Book
from StoryArcs import StoryArcs
from ComicDisplay import ComicDisplay

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    from Tkinter import *
    from Tkinter import ttk
else:
    from tkinter import *
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename



def showGUI():
    root = Tk()

    #dir_path = os.path.dirname(os.path.realpath(__file__)) + '\\config\\images\\comicicon.ico'
    #root.iconbitmap(dir_path)
    root.state('zoomed')

    rWidth = root.winfo_screenwidth()
    rHeight = root.winfo_screenheight()

    root.geometry(('%dx%d+0+0')%(rWidth, rHeight-35))
    root.focus_set()
    app = Window(root)
    root.mainloop()


class Window(Frame):
    
    def __init__(self, master=None):
        self.master = master
        Frame.__init__(self, master)
        self.init_data()
        self.init_frame()
        self.show_library()

    def init_frame(self):
        self.master.title("Robin Comic Cave")
        self.pack(fill=BOTH, expand=1)
        menu = Menu(self.master)
        self.master.config(menu=menu)

        self.publisher = "DC"
        self.currentView = None

        file = Menu(menu)
        file.add_command(label='Add New Issue', command= self.add_series)
        file.add_command(label='Read CBR/CBZ')
        file.add_command(label='Exit')

        edit = Menu(menu)

        publisher = Menu(menu)
        publisher.add_command(label="DC", command= lambda: self.set_publisher("DC"))
        publisher.add_command(label="Marvel", command= lambda: self.set_publisher("Marvel"))

        view = Menu(menu)
        view.add_command(label='Library', command=self.show_library)
        view.add_command(label='Story Arcs', command= self.show_arcs)

        menu.add_cascade(label='File', menu=file)
        menu.add_cascade(label='Edit', menu=edit)
        menu.add_cascade(label='View', menu=view)
        menu.add_cascade(label="Publisher", menu=publisher)
        #StoryArcFrame.pack()

    def show_arcs(self):
        try:
            self.library_display.pack_forget()
            self.storyArcView.pack()
        except:
            self.storyArcView = StoryArcs(self, self.master, self.publisher)
        self.currentView = self.storyArcView

    def hide_arcs(self):
        self.storyArcView.pack_forget()

    def reset_library(self):
        self.library_display.pack_forget()
        self.library_display.destroy()

    def reset_arcs(self):
        self.storyArcView.grid_forget()
        self.storyArcView.destroy()
    
    def set_publisher(self, publisher):
        self.publisher = publisher
        try:
            self.reset_arcs()
        except:
            pass

    def show_library(self):

        #print(self.df['Title'].values) # returns list of titles from df
        try:
            self.hide_arcs()
            self.library_display.pack()
        except:
            self.library_display = ComicDisplay(master=self, df=self.df, root=self.master)

        self.currentView = self.library_display
        
    def add_series(self):
        self.add_series_window = Add_Series_Window(master=self, df=self.df, publisher=self.publisher)

    def init_data(self): #Quick update check on all data used in program, i.e. scan wikipedia for new comic book eras
        # Check to make sure there is a file to hold the comic eras for each company
        # Add each line to a list for each company
        # Scan wikipedia for a new list of comic eras for that company
        # Check the wikipedia list against the one you have
        # Add any new ones that may have been found on wikipedia

        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..//bin')) + '//data.csv'
        if os.path.isfile(path):
            self.df = pd.read_csv(path)
            #print(self.df)
        else:
            columns = ['ID', 'Title', 'Publisher', 'Era', 'Favorite', 'Path']
            self.df = pd.DataFrame(columns=columns)

    def update_df(self, new_issue):
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..//bin')) + '//data.csv'

        size = len(self.df)
        self.df.loc[size] = new_issue
        self.df.to_csv(path, index=True, header=True)

        self.reset_library()
        self.add_series_window.exit()

        if self.currentView.__class__ == ComicDisplay:
            self.show_library()

        


showGUI()
