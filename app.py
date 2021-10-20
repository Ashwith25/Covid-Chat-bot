from textwrap import fill
from tkinter import *
from chatbot import startApp, vaccination_by_pincode
from datetime import datetime

BG_GRAY = "#ABB2B9"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

# TODO:
'''
1. Quitting app
2. Chat alignment
'''

class ChatApplication:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        self.forLocation = False
        
    def run(self):
        self.window.mainloop()
        
    def _setup_main_window(self):
        self.window.title("CovidBOT")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=550, height=700, bg=BG_COLOR)
        
        # head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text="Welcome!", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        
        # tiny divider
        line = Label(self.window, width=550, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        
        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        
        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        
        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)
        
        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
     
    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")
        
    def _insert_message(self, msg, sender):
        if not msg:
            return
        now = datetime.now()
        current_time = now.strftime("%D - %H:%M \n")

        self.text_widget.config(state=NORMAL)
        self.text_widget.insert(END, "You: " + current_time + ' ', ("small", "right", "greycolour"))
        self.text_widget.window_create(END, window=Label(self.text_widget, fg="#000000", text=msg, 
        wraplength=300, font=("Arial", 10), bg="lightblue", bd=10, justify="left"))
        self.text_widget.insert(END,'\n ', "left")
        self.text_widget.config(foreground="#FFFFFF", font=("Helvetica", 9))
        self.text_widget.yview(END)

        tag = "Initial"

        if not self.forLocation: res, tag = startApp(msg)

        if self.forLocation:
            pincode, date = msg.split(" ")
            try:
                res = vaccination_by_pincode(pincode, date)
                self.forLocation = False
            except:
                self.text_widget.insert(END, "CovidBOT: " + current_time +' ', ("small", "greycolour", "left"))
                self.text_widget.window_create(END, window=Label(self.text_widget, fg="#000000", text="Enter details properly", anchor='e',
                wraplength=300, font=("Arial", 10), bg="#DDDDDD", bd=10, justify="left"))
                self.text_widget.insert(END, '\n ', "right")
                self.text_widget.config(state=DISABLED)
                self.text_widget.yview(END)
                
                self.msg_entry.delete(0, END)

        if tag == "vaccination_by_pincode":
            self.forLocation = True

        # else:
        self.text_widget.insert(END, "CovidBOT: " + current_time +' ', ("small", "greycolour", "left"))
        self.text_widget.window_create(END, window=Label(self.text_widget, fg="#000000", text=res, 
        wraplength=300, font=("Arial", 10), bg="#DDDDDD", bd=10, justify="left"))
        self.text_widget.insert(END, '\n ', "right")
        self.text_widget.config(state=DISABLED)
        self.text_widget.yview(END)
        
        self.msg_entry.delete(0, END)
        # msg1 = f"{sender}: {msg}\n\n"
        # self.text_widget.configure(state=NORMAL)
        # self.text_widget.insert(END, msg1, "right")
        # self.text_widget.configure(state=DISABLED)
        
        # msg2 = f"CovidBOT: {startApp(msg)}\n\n"
        # self.text_widget.configure(state=NORMAL)
        # self.text_widget.insert(END, msg2, "left")
        # self.text_widget.configure(state=DISABLED)
        
        # self.text_widget.see(END)
             
        
if __name__ == "__main__":
    app = ChatApplication()
    app.run()