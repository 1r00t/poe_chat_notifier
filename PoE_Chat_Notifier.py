from Tkinter import *
from ttk import *
import tkFileDialog
import ConfigParser
import winsound
import time
import os


class Notifier_GUI(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        # Settings
        self.master.protocol("WM_DELETE_WINDOW", self.quit_program)
        self.config = ConfigParser.RawConfigParser()
        self.config.read("config.cfg")
        self.running = False

        # Menubar
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Open Client.txt", command=self.cltxt_open)
        menu.add_command(label="Exit", command=self.stop)
        menu = Menu(self.menubar, tearoff=0)
        self.master.config(menu=self.menubar)

        # Gerneral UI
        self.chat = Text(self)
        self.chat.grid(row=0, column=0, columnspan=4, sticky=E + W)
        self.chat.config(state=DISABLED)
        self.keywords_label = Label(self, text="Keywords (comma separated):")
        self.keywords_label.grid(row=1, column=0)
        self.keywords = Entry(self, width=50)
        self.keywords.grid(row=1, column=1, sticky=E + W)
        self.start_btn = Button(self, text="start", command=self.start)
        self.start_btn.grid(row=1, column=2, sticky=E + W)
        self.stop_btn = Button(self, text="stop", command=self.stop)
        self.stop_btn.grid(row=1, column=3, sticky=E + W)
        self.stop_btn.config(state=DISABLED)

        # Statusbar
        self.statusbar = StatusBar(self)
        self.statusbar.grid(row=2, column=0, columnspan=4, sticky=E + W)

        self.config_load()

    def config_load(self):
        keywords = self.config.get("Notifier", "keywords")
        self.keywords.insert(INSERT, keywords)

    def config_save(self):
        with open("config.cfg", "w+") as configfile:
            self.config.write(configfile)

    def message_to_chat(self, message):
        self.chat.config(state=NORMAL)
        self.chat.insert(END, message)
        self.chat.config(state=DISABLED)

    def start(self):
        if self.ready_to_go() and not self.running:
            self.start_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
            self.keywords.config(state=DISABLED)
            keywords = self.keywords.get()
            self.config.set("Notifier", "keywords", keywords)
            self.config_save()
            self.statusbar.set("Running!")
            self.run()

    def stop(self):
        if self.running:
            self.running = False
            self.statusbar.set("Stopped!")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.keywords.config(state=NORMAL)

    def cltxt_open(self):
        cltxt_name = tkFileDialog.askopenfilename(
            title="Open \"Client.txt\"",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=self.config.get("Notifier", "client_txt"))
        if cltxt_name:
            self.config.set("Notifier", "client_txt", cltxt_name)
            self.config_save()

    def cltxt_valid(self):
        cltxt_name = self.config.get("Notifier", "client_txt")
        if not cltxt_name:
            self.statusbar.set("No \"Client.txt\" file specified!")
            return False
        if not os.path.isfile(cltxt_name):
            self.statusbar.set("\"{}\" does not exist!".format(cltxt_name))
            return False
        if not os.path.basename(cltxt_name) == "Client.txt":
            self.statusbar.set(
                "\"{}\" is not a valid \"Client.txt\"!".format(cltxt_name))
            return False
        if not os.access(cltxt_name, os.R_OK):
            self.statusbar.set(
                "No permissions to read \"{}\"!".format(cltxt_name))
            return False
        return True

    def keywords_valid(self):
        keywords = self.keywords.get()
        if not keywords:
            self.statusbar.set("No keywords chosen!")
            return False
        return True

    def ready_to_go(self):
        if self.cltxt_valid() and self.keywords_valid():
            self.statusbar.set("")
            return True
        return False

    def run(self):
        self.running = True
        cltxt_name = self.config.get("Notifier", "client_txt")
        fsize = os.stat(cltxt_name)[6]
        f = open(cltxt_name, "r")
        f.seek(fsize)
        self.search_cltxt(cltxt_name, fsize, f)

    def search_cltxt(self, cltxt_name, fsize, f):
        keywords = self.config.get("Notifier", "keywords")
        keywords = [w.strip() for w in keywords.split(",")]
        where = f.tell()
        line = f.readline()
        if not line:
            # time.sleep(1) #  KA ob ich das doch noch brauche :S hoffentlich nicht!
            f.seek(where)
        else:
            line = " ".join(line.split()[7:]) + "\n"
            for keyword in keywords:
                if keyword in line:
                    winsound.Beep(440, 300)
                    self.message_to_chat(line)
                    self.chat.see("end")
                    break
        if self.running:
            self.master.after(1000, self.search_cltxt, cltxt_name, fsize, f)
        else:
            f.close()

    def quit_program(self):
        if self.running:
            self.stop()
        self.quit()




class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, relief=SUNKEN, anchor=E)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()


root = Tk()
root.title("PoE Chat Notifier")
notifier = Notifier_GUI(root)
notifier.pack()
root.mainloop()
