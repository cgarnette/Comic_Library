

import os
import shutil
import time
from tkinter import (Button, Entry, Frame, Label, OptionMenu, StringVar,
                     Toplevel)
from tkinter.filedialog import askopenfilename
from tkinter import filedialog

import patoolib
from PIL import Image
from pyunpack import Archive

from distutils.dir_util import copy_tree


class Add_Series_Window:
    def __init__(self, master=None, publisher=None, df=None):
        self.master = master
        self.root = master.master
        self.publisher = publisher
        self.df = df
        self.new_window()
        self.frame = Frame(self.newWindow, width=500, height=300)
        self.frame.pack_propagate(0)
        self.frame.pack()
        self.initial_frame = Frame(self.frame)
         # Check this out further
        self.initial_build()

    def initial_build(self):
        self.newWindow.protocol("WM_DELETE_WINDOW", self.exit)

        browse_view = Button(self.initial_frame, text='Add File', command=self.add_from_file)
        browse_folder = Button(self.initial_frame, text='Add Folder', command=self.add_folder)

        browse_folder.pack(pady=(75, 0))
        browse_view.pack(pady = (75, 0))

        self.initial_frame.pack()

    def exit(self):
        self.newWindow.destroy()

    def browse(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        filename = askopenfilename (initialdir=dir_path,
                           filetypes =(("Text File", "*.txt"),("All Files","*.*")),
                           title = "Choose Report File for Series")
        self.filename.set(filename)

    def add_folder(self):
        self.initial_frame.destroy()
        from_folder_frame = Frame(self.frame)

        self.selected_choice = StringVar(from_folder_frame)
        self.filename = StringVar(from_folder_frame)
        

        if self.publisher is "DC":
            choices = {'Pre-Crisis', 'Crisis and Post-Crisis', 'Post-Flashpoint', 'Post-Rebirth', 'Crossover with Other Companies', 'Unknown'}
            self.selected_choice.set('Post-Rebirth')
        
        elif self.publisher is "Marvel":
            choices = {'Golden Age', 'Silver Age', '1970s', '1980s', '1990s', '2000s', '2010s', 'Ultimate Marvel'}
            self.selected_choice.set('2010s')

        browse_button = Button(from_folder_frame, text='Browse', command=self.browse_folder)
        browse_button.grid(row=0, column=0)

        lbl = Label(from_folder_frame, textvariable=self.filename)
        lbl.grid(row=0, column=1)

        label_2 = Label(from_folder_frame, text='Comic Era')
        label_2.grid(row=1, column=0)

        options = OptionMenu(from_folder_frame, self.selected_choice, *choices)
        options.grid(row=1, column=1)

        add_btn = Button(from_folder_frame, text='Add', command=self.add)
        add_btn.grid(row=2, column=0, columnspan=2)

        from_folder_frame.pack()
                    
    def browse_folder(self):
        filename = filedialog.askdirectory()
        self.filename.set(filename)

    def add_from_file(self):

        self.initial_frame.destroy()

        from_file_frame = Frame(self.frame)

        self.selected_choice = StringVar(from_file_frame)
        self.filename = StringVar(from_file_frame)

        if self.publisher is "DC":
            choices = {'Pre-Crisis', 'Crisis and Post-Crisis', 'Post-Flashpoint', 'Post-Rebirth', 'Crossover with Other Companies', 'Unknown'}
            self.selected_choice.set('Post-Rebirth')
        
        elif self.publisher is "Marvel":
            choices = {'Golden Age', 'Silver Age', '1970s', '1980s', '1990s', '2000s', '2010s', 'Ultimate Marvel'}
            self.selected_choice.set('2010s')

        browse_button = Button(from_file_frame, text='Browse', command=self.browse)
        browse_button.grid(row=0, column=0)

        lbl = Label(from_file_frame, textvariable=self.filename)
        lbl.grid(row=0, column=1)

        label_1 = Label(from_file_frame, text='Series Title')
        label_1.grid(row=1, column=0)

        self.title_entry = Entry(from_file_frame)
        self.title_entry.grid(row=1, column=1)

        label_3 = Label(from_file_frame, text='Issue Number')
        label_3.grid(row=2, column=0)

        self.num_entry = Entry(from_file_frame)
        self.num_entry.grid(row=2, column=1)

        label_2 = Label(from_file_frame, text='Comic Era')
        label_2.grid(row=3, column=0)

        options = OptionMenu(from_file_frame, self.selected_choice, *choices)
        options.grid(row=3, column=1)

        add_btn = Button(from_file_frame, text='Add', command=self.add)
        add_btn.grid(row=4, column=0, columnspan=3)


        from_file_frame.pack()

    def add(self, df=None):

        if df is None:
            df = self.df
        # Must check dataframe to see if this title already exists.
        # If so then you will just be increasing the number of issues for this title
        # If not then add the title to the df

        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..//bin'))

        if '.' not in str(self.filename.get()):
            title = str(self.filename.get()).split('/')[-1].replace(' ', '-')
            copy_tree(self.filename.get(), path + '\\Comics\\' + title, update=1)
            new_issue = [len(df), title, self.publisher, self.selected_choice.get(), "No", path + '\\Comics\\' + title]
            self.master.update_df(new_issue)
            return None

        try:
            int(str(self.num_entry.get()).strip())
        except:
            return None

        if len(self.title_entry.get()) < 3:
            return None


        title = str(self.title_entry.get()).replace(' ', '-')

        dir_path = path + '\\Comics\\' + title

        if (not os.path.exists(dir_path)):
            os.makedirs(dir_path)

        issue_path = dir_path + '\\' + str(self.num_entry.get())

        try:
            os.makedirs(issue_path)
        except:
            try:
                shutil.rmtree(issue_path, ignore_errors=True)
                os.makedirs(issue_path)
            except:
                pass

        Archive(self.filename.get()).extractall(issue_path)

        if len(os.listdir(issue_path)) < 3:
            old_dir = os.listdir(issue_path)[0]
            issue_path = issue_path + '//' + old_dir

        issues = [x for x in os.listdir(issue_path)]

        if '.jpg' not in issues[0]:
            for x in range(0, len(issues), 1):
                im = Image.open(dir_path + '\\' + issues[x])
                rgb_im = im.convert('RGB')
                rgb_im.save(dir_path + '\\' + str(x+1) + '.jpg')
        else:
            for x in range(0, len(issues), 1):
                os.rename(issue_path+'\\' + issues[x], issue_path+'\\' + str(x+1) + '.jpg')

        #['ID', 'Title', 'Publisher', 'Era', 'Favorite', 'Path']

        id = len(df.index)
        self.run_dir_check(dir_path)
        if len(df[df['Title'] == title]) > 0:
            pass
        else:
            new_issue = [id, title, self.publisher, self.selected_choice.get(), "No", dir_path]
            self.master.update_df(new_issue)

        
    def run_dir_check(self, dir_path):

        #dir_path should be ../Comics/*Series Title*
        path = None
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if '.jpg' in file:
                    path = root
                    break
            if path is not None:
                break

        path = os.path.abspath(os.path.join(path, '..//')) #From jpg to issue num dir
        path = os.path.abspath(os.path.join(path, '..//')) #From issue num dir to series title (or should be)

        if path is not dir_path:
            copy_tree(path, dir_path, update=1)
            shutil.rmtree(path, ignore_errors=True)


        # allow the user to add downloaded comics to their library
        # Incorporate CBR and CBZ reading

        # Display a form which first requires the user to find the cbr/cbz file
        # Next Have them input the title of the series
        # Then the era to which it belongs
        # Finally, the issue number which is being added

        # CBR/CBZ files can hold png, gif and jpg files. This reader only reads jpg so we need to convert:
        # from PIL import Image
        # im = Image.open("Ba_b_do8mag_c6_big.png")
        # rgb_im = im.convert('RGB')
        # rgb_im.save('colors.jpg')

        # To open The CBR/CBZ we will use pyunpack
        # pip install pyunpack
        # pip install patool

        # from pyunpack import Archive
        # Archive('a.zip').extractall('/path/to')
    
    def selectIssue(self):
        self.new_window()

    def new_window(self):
        self.newWindow = Toplevel(self.root)
