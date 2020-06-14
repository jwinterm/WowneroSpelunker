from tkinter import *
from PIL import ImageTk, Image
import subprocess
import threading
import queue
import os
import re
from os import system
from re import sub
import sys

os.environ["PYTHONUNBUFFERED"] = "1"

def enqueue_output(p, q):
    while True:
        out = p.stdout.readline()
        if out == '' and p.poll() is not None:
            break
        if out:
            #print(out.strip(), flush=True)
            q.put_nowait(out.strip())


def resource_path(relative_path):    
    try:       
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.started = False
        self.p = None
        self.q = queue.Queue()
        self.threads = 2
        self.urltext = ""
        self.addytext = ""
        self.imgMinerDoge = ImageTk.PhotoImage(Image.open(resource_path("minerdoge.png")))
        self.imgStopped = ImageTk.PhotoImage(Image.open(resource_path("notstress.jpg")))
        self.imgStarted = ImageTk.PhotoImage(Image.open(resource_path("stress.jpg")))
        self.imgVeryStarted = ImageTk.PhotoImage(Image.open(resource_path("verystress.png")))
        self.hugepagesCheckbuttonVar = IntVar()
        self.wowneroRadiobuttonVar = IntVar()
        self.init_window()


    def init_window(self):
        self.master.title("Wownero Spelunker")
        self.pack(fill=BOTH, expand=1)

        self.titleLabel = Label(self, text="Wownero Spelunker", font=("Comic Sans MS", 16))
        self.titleImage = Label(image=self.imgMinerDoge)
        self.titleImage.image = self.imgMinerDoge
        
        self.urlLabel = Label(self, text="Pool URL:port")
        self.urlEntry = Entry(self, textvariable=self.urltext, width=40)
        self.urlEntry.insert(0, "wownero.herominers.com:10661")
        
        self.addyLabel = Label(self, text="Wallet addy")
        self.addyEntry = Entry(self, textvariable=self.addytext, width=40)

        self.statusLabel = Label(self, text="Current status:\nNot mining")
  
        self.statusImage = Label(image=self.imgStopped)
        self.statusImage.image = self.imgStopped

        self.hashrateLabel = Label(self, text="Hashrate: ")

        self.threadsLabel = Label(self, text="# of threads: ")
        self.threadsEntry = Entry(self, textvariable=self.threads, width=5)
        self.threadsEntry.insert(0, "2")

        self.hugepagesCheckbutton = Checkbutton(self, text="Use hugepages", variable=self.hugepagesCheckbuttonVar)
        
        self.wowneroRadiobutton = Radiobutton(self, text="Wownero", variable=self.wowneroRadiobuttonVar, value=1, command=self.wowneroUrl)
        self.wowneroRadiobutton.select()
        self.moneroRadiobutton = Radiobutton(self, text="Monero", variable=self.wowneroRadiobuttonVar, value=2, command=self.moneroUrl)
        self.wowDonateRadiobutton = Radiobutton(self, text="Donate Wownero", variable=self.wowneroRadiobuttonVar, value=3, command=self.wowneroDonate)
        self.moDonateRadiobutton = Radiobutton(self, text="Donate Monero", variable=self.wowneroRadiobuttonVar, value=4, command=self.moneroDonate)

        self.hashrateLabel = Label(self, text="Hashrate: 0 h/s")
        self.hashrateLabel.after(2000, self.refresh_hashrate)
   
        self.startButton = Button(self, text="Start", background="green", command=self.startstop)
        self.quitButton = Button(self, text="Quit", command=self.client_exit)
        
        self.outputLabelLabel = Label(self, text="Miner output:")
        self.outputLabel = Label(self, text="")

        self.titleLabel.place(x=70, y=10)
        self.titleImage.place(x=270, y=0)
        self.urlLabel.place(x=30, y=55)
        self.urlEntry.place(x=112, y=55)
        self.addyLabel.place(x=30, y=75)
        self.addyEntry.place(x=112, y=75)
        self.statusLabel.place(x=50, y=100)
        self.statusImage.place(x=140, y=100)
        self.threadsLabel.place(x=50, y=180)
        self.threadsEntry.place(x=125, y=180)
        self.hugepagesCheckbutton.place(x=220, y=178)
        self.wowneroRadiobutton.place(x=230, y=100)
        self.moneroRadiobutton.place(x=230, y=120)
        self.wowDonateRadiobutton.place(x=230, y=140)
        self.moDonateRadiobutton.place(x=230, y=160)
        self.hashrateLabel.place(x=50, y=220)
        self.outputLabelLabel.place(x=50, y=250)
        self.outputLabel.place(x=50, y=265)
        self.startButton.place(x=100, y=310)
        self.quitButton.place(x=250, y=310)
        
    def clearStuff(self):
        self.urlEntry.delete(0, 'end')
        self.addyEntry.delete(0, 'end')
    def wowneroUrl(self):
        self.urlEntry.delete(0, 'end')
        self.urlEntry.insert(0, "wownero.herominers.com:10661")
    def moneroUrl(self):
        self.urlEntry.delete(0, 'end')
        self.urlEntry.insert(0, "monero.herominers.com:10191")
    def wowneroDonate(self):
        self.clearStuff()
        self.urlEntry.insert(0, "wownero.herominers.com:10661")
        self.addyEntry.insert(0, "Wo3MWeKwtA918DU4c69hVSNgejdWFCRCuWjShRY66mJkU2Hv58eygJWDJS1MNa2Ge5M1WjUkGHuLqHkweDxwZZU42d16v94mP")
    def moneroDonate(self):
        self.clearStuff()
        self.urlEntry.insert(0, "monero.herominers.com:10191")
        self.addyEntry.insert(0, "888tNkZrPN6JsEgekjMnABU4TBzc2Dt29EPAvkRxbANsAnjyPbb3iQ1YBRk1UXcdRsiKc9dhwMVgN5S9cQUiyoogDavup3H")

    def startstop(self):
        if not self.started:
            try:
                self.threads = int(self.threadsEntry.get())
            except:
                self.threads = 2
            if self.threads > 16:  
                self.threads = 16
            self.threadsEntry.delete(0, 'end')
            self.threadsEntry.insert(0, self.threads)
            if self.hugepagesCheckbuttonVar.get():
                hugepages = ""
            else:
                hugepages = "--no-huge-pages"
            print(self.threads)
            if self.wowneroRadiobuttonVar.get() == 1 or self.wowneroRadiobuttonVar.get() == 3:
                algo = "rx/wow"
            else: 
                also = "rx/0"
            self.p = subprocess.Popen([resource_path("xmrig.exe"), "-t", str(self.threads), 
                        hugepages, "--donate-level=1", "-a", algo, "-o", str(self.urlEntry.get()), "-u", str(self.addyEntry.get())],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        #shell=True,
                        encoding='utf-8',
                        #creationflags=0x08000000,
                        errors='replace')
            self.t = threading.Thread(target=enqueue_output, args=(self.p, self.q))
            self.t.daemon = True
            self.t.start()
            self.started = True
            if self.threads < 3:
                self.statusImage = Label(image=self.imgStarted)
                self.statusImage.image = self.imgStarted
            else:
                self.statusImage = Label(image=self.imgVeryStarted)
                self.statusImage.image = self.imgVeryStarted
            self.statusImage.place(x=140, y=100)
            self.statusLabel.config(text="Current status:\nMining")
            self.startButton.config(text="Stop", background="red")
        elif self.started:
            system("taskkill /im xmrig.exe /f")
            self.p.kill()
            self.t.join()
            self.started = False
            self.statusImage = Label(image=self.imgStopped)
            self.statusImage.image = self.imgStopped
            self.statusImage.place(x=140, y=100)
            self.statusLabel.config(text="Current status:\nNot mining")
            self.hashrateLabel.config(text="Hashrate: 0 h/s")
            self.startButton.config(text="Start", background="green")

    def refresh_hashrate(self):
        if not self.started:
            pass
        elif self.started:
            try:
                line = self.q.get_nowait()
                print(line)
                if len(line) > 5:
                    self.outputLabel.config(text=line)
                try:
                    if "speed" in line:
                        hashrate = re.findall(" \d+\.\d+ ", line)[0]
                        self.hashrateLabel.config(text="Hashrate: {0:.2f} h/s".format(float(hashrate)))
                except:
                    pass
            except:
                pass
        self.hashrateLabel.after(1000, self.refresh_hashrate)

    def client_exit(self):
        try:
            system("taskkill /im xmrig.exe /f")
            self.p.kill()
            self.t.join()
        except:
            pass
        sys.exit(0)


root = Tk()
root.iconbitmap(default=resource_path('stress.ico'))
root.geometry("400x350")

app = Window(root)
root.mainloop()

