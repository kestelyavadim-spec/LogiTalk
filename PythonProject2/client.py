import threading
from socket import *
from customtkinter import *

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('600x500')
        self.label = None
        self.username = "Guest"
        self.is_show_menu = False
        self.speed_animate_menu = -5

        # menu frame
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)

        # main chat
        self.chat_field = CTkTextbox(self, font=('Arial', 14, 'bold'), state='disable')
        self.chat_field.place(x=0, y=0)

        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:', height=40)
        self.message_entry.place(x=0, y=0)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)

        # підключення до сервера
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('6.tcp.eu.ngrok.io', 18941))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.adaptive_ui()

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            # setting menu widgets
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=10)
            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()
            self.accept_name = CTkButton(self.menu_frame, text='Змінити', width=50, command=self.change_name)
            self.accept_name.pack(pady=10)

            # кнопка зміни теми
            self.theme_button = CTkButton(self.menu_frame, text="Змінити тему", command=self.change_theme)
            self.theme_button.pack(pady=10)

            # перемикач шрифту
            self.font_option = CTkOptionMenu(self.menu_frame, values=["Arial", "Courier"], command=self.change_font)
            self.font_option.pack(pady=10)

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()
                self.accept_name.destroy()
                self.theme_button.destroy()
                self.font_option.destroy()

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width(),
                                  height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width() - self.send_button.winfo_width())
        self.after(30, self.adaptive_ui)

    def add_message(self, text):
        self.chat_field.configure(state='normal')
        self.chat_field.insert(END, text + '\n')
        self.chat_field.configure(state='disable')
        self.chat_field.see("end")

    def send_message(self):
        message = self.message_entry.get().strip()
        if message:
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
                self.add_message(f"{self.username}: {message}")
            except:
                self.add_message("Помилка: повідомлення не надіслано.")
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):
        if not line:
            return
        parts = line.split("@", 3)
        msg_type = parts[0]
        if msg_type == "TEXT" and len(parts) >= 3:
            author = parts[1]
            message = parts[2]
            self.add_message(f"{author}: {message}")
        else:
            self.add_message(line)

    def change_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.entry.delete(0, END)
            info = f"TEXT@{self.username}@[SYSTEM] {self.username} змінив(ла) імʼя\n"
            try:
                self.sock.sendall(info.encode())
            except:
                pass

    def change_theme(self):
        current_mode = get_appearance_mode()
        set_appearance_mode("Dark" if current_mode == "Light" else "Light")

    def change_font(self, font_name):
        self.chat_field.configure(font=(font_name, 14, 'bold'))
        self.message_entry.configure(font=(font_name, 12))

    def on_close(self):
        try:
            self.sock.close()
        except:
            pass
        self.destroy()


win = MainWindow()
win.mainloop()
