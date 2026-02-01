from customtkinter import *

class ConnectWindow(CTk):
    def __init__(self):
        super().__init__()

        self.name = None
        self.host = None
        self.port = None
        self.name_entry = CTkEntry(self,placeholder_text="Введи нік",height=50)
        self.name_entry.pack()
        self.host_entry = CTkEntry(self, placeholder_text="Ip сервера",height=50)
        self.host_entry.pack()
        self.port_entry = CTkEntry(self, placeholder_text="Порт сервера",height=50)
        self.port_entry.pack()

        self.join = CTkButton(self, text='Приєднатись', command=self.open_game, height=50)
        self.join.pack()
        self.label = CTkLabel(self,text = 'Agario',height=50)
        self.label.pack()

    def open_game(self):
        self.name = self.name_entry.get()
        self.host = self.host_entry.get()
        self.port = int(self.port_entry.get())
        self.destroy()

