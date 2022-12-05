import os
import hashlib
import base64
import sqlite3
import tkinter
from tkinter import messagebox
from tkinter import *


SALT = ''
MASTER_PASSWORD = ''


def copy_data():
    try:
        full_text = mylist.get(mylist.curselection())
        arr = full_text.split('   ')
        window.clipboard_clear()
        window.clipboard_append(arr[1])
    except Exception:
        msg_box_non_chosen()


def trying_delete_data():
    try:
        full_text = mylist.get(mylist.curselection())
        arr = full_text.split('   ')
        delete_data(arr[0])
        generate_table()
    except Exception:
        msg_box_non_chosen()


def add_site_dialog():
    add = Toplevel(window)

    add.title("Ключник")
    x = int((add.winfo_screenwidth() - add.winfo_reqwidth()) / 2.35)
    y = int((add.winfo_screenheight() - add.winfo_reqheight()) / 2.1)
    add.geometry(f'500x200+{x}+{y}')
    add.resizable(False, False)

    photo = PhotoImage(file='key.png')
    add.iconphoto(False, photo)
    lbbg = Label(add, text="")
    lbbg.place(width=500, height=200)
    lb = Label(add, text="Название сайта", font=("Arial", 16))
    lb.place(x=250, y=40, anchor='center')

    input_site = tkinter.Entry(add, textvariable=new_site, font=("Arial", 20))
    input_site.place(x=250, y=90, anchor='center')
    input_site.focus_set()

    def add_exit_button():
        add.destroy()

    def add_button():
        add_site()
        input_site.delete(0, END)

    btn_add_site = Button(add, text="Добавить", font=("Arial Bold", 16), command=add_button)
    btn_add_site.place(x=140, y=160, anchor='center')

    btn_cancel_to_add_site = Button(add, text="Закрыть", font=("Arial Bold", 16), command=add_exit_button)
    btn_cancel_to_add_site.place(x=380, y=160, anchor='center')

    add.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    add.grab_set()
    # фокусируем наше приложение на окне top
    #add.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    add.wait_window()

window = tkinter.Tk()
window.title("Ключник")
x = int((window.winfo_screenwidth() - window.winfo_reqwidth()) / 2.25)
y = int((window.winfo_screenheight() - window.winfo_reqheight()) / 2.6)
window.geometry(f"430x530+{x}+{y}")
window.resizable(False, False)
photo = tkinter.PhotoImage(file='key.png')
window.iconphoto(False, photo)

# Создание меню
menubar = Menu(window)
# Добавление меню записи
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Запись', menu=file)
file.add_command(label='Добавить', command=add_site_dialog)
file.add_command(label='Удалить', command=trying_delete_data)
file.add_separator()
file.add_command(label='Выход', command=window.destroy)
window.config(menu=menubar)

copy_m = Menu(menubar, tearoff=0)
menubar.add_command(label='Копировать', command=copy_data)
window.config(menu=menubar)

scrollbar = Scrollbar(window)
scrollbar.pack(side=RIGHT, fill=Y)

mylist = Listbox(window, yscrollcommand=scrollbar.set, font=("Arial", 20), bg='lightgray')
mylist.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=mylist.yview)

mr_pass = tkinter.StringVar()
mr_word = tkinter.StringVar()
new_site = tkinter.StringVar()


def generate_table():
    # инициализация БД
    db = sqlite3.connect('data.sqlite')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM data WHERE id>1")
    result_all = cursor.fetchall()  # лист кортежей, в каждом - строка из БД

    mylist.delete(0, END)


    for data in result_all:
        site_name = base64.b64decode(data[1].encode()).decode()
        pass64 = base64.b64encode((site_name + SALT).encode()).decode()
        hash_pass = encode_pass(pass64)
        if hash_pass == data[2]:
            show_pass = pass64
        else:
            show_pass = data[2]
        mylist.insert(END, site_name + '   ' + show_pass)

    db.close()


def add_site():
    site = new_site.get()
    pass64 = base64.b64encode((site+SALT).encode()).decode()
    site64 = base64.b64encode(site.encode()).decode()
    hash_pass = encode_pass(pass64)
    add_data(site64, hash_pass)
    generate_table()


# Алгоритм генерации пароля
def encode_pass(passw: str) -> str:
    return hashlib.sha256(passw.encode()).hexdigest()


# Установка мастер-пароля
def setup_master_pass(passw: str):
    passw = encode_pass(passw)
    # инициализация БД
    db = sqlite3.connect('data.sqlite')
    cursor = db.cursor()
    # создание новой таблицы, если другой нет
    cursor.execute('''
                                   CREATE TABLE IF NOT EXISTS data (
                                   id INTEGER PRIMARY KEY,
                                    site TEXT NOT NULL UNIQUE,
                                    pass TEXT NOT NULL)''')
    cursor.execute("INSERT INTO data (site, pass) VALUES (?, ?)", ('master', passw))
    db.commit()
    db.close()


def pass_btn_ok_clicked():
    setup_master_pass(mr_pass.get())
    msg_box_swap_pass()


def pass_btn_cancel_clicked():
    window.destroy()
    exit()


def setup_pass_dialog():
    top = Toplevel(window)

    top.title("Ключник")
    top.geometry('500x200')
    top.resizable(False, False)

    photo = PhotoImage(file='key.png')
    top.iconphoto(False, photo)
    lbbg = Label(top, text="")
    lbbg.place(width=500, height=200)
    lb = Label(top, text="Установка нового мастер-пароля", font=("Arial", 16))
    lb.place(x=250, y=40, anchor='center')

    inp = tkinter.Entry(top, textvariable=mr_pass, show="*", font=("Arial Bold", 20))
    inp.place(x=250, y=90, anchor='center')

    btnOk = Button(top, text="Применить", font=("Arial Bold", 16), command=pass_btn_ok_clicked)
    btnOk.place(x=150, y=160, anchor='center')

    btnCancel = Button(top, text="Выход", font=("Arial Bold", 16), command=pass_btn_cancel_clicked)
    btnCancel.place(x=380, y=160, anchor='center')

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    top.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


def msg_box_swap_pass():
    result = messagebox.showwarning("Сообщение", "Мастер-пароль успешно установлен. Перезапустите программу.")
    if result:
        window.destroy()
        exit()


def msg_box_non_chosen():
    result = messagebox.showwarning("Сообщение", "Сначала выберите запись.")


def msg_box_wrong_pass():
    result = messagebox.showerror("Неправильный пароль!", "Пароль не подходит")
    if result:
        window.destroy()
        exit()


def msg_box_alert():
    result = messagebox.askyesno("ВНИМАНИЕ!", "База данных не найдена. Создать новую?")
    if result:
        setup_pass_dialog()
    else:
        exit()


def auth_dialog():
    def login_btn_clicked():
        global SALT
        password = mr_pass.get()
        SALT = mr_word.get()

        # инициализация БД
        db = sqlite3.connect('data.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM data WHERE site='master'")
        result = cursor.fetchone()
        db.close()
        if encode_pass(password) == result[2]:
            generate_table()
            top.destroy()
        else:
            msg_box_wrong_pass()
    top = Toplevel(window)

    top.title("Ключник")
    x = int((top.winfo_screenwidth() - top.winfo_reqwidth()) / 2.35)
    y = int((top.winfo_screenheight() - top.winfo_reqheight()) / 2.1)
    top.geometry(f'500x200+{x}+{y}')
    top.resizable(False, False)
    def Quit():
        pass
    top.protocol("WM_DELETE_WINDOW", Quit)

    photo = PhotoImage(file='key.png')
    top.iconphoto(False, photo)
    lbbg = Label(top, text="")
    lbbg.place(width=500, height=200)
    lb = Label(top, text="Введите мастер-пароль", font=("Arial", 16))
    lb.place(x=250, y=20, anchor='center')
    lb2 = Label(top, text="Введите кодовое слово", font=("Arial", 16))
    lb2.place(x=250, y=80, anchor='center')

    input_pass = tkinter.Entry(top, textvariable=mr_pass, show="*", font=("Arial", 20))
    input_pass.place(x=250, y=50, anchor='center')

    input_word = tkinter.Entry(top, textvariable=mr_word, show="*", font=("Arial", 20))
    input_word.place(x=250, y=110, anchor='center')

    btnLogin = Button(top, text="Войти", font=("Arial Bold", 16), command=login_btn_clicked)
    btnLogin.place(x=140, y=160, anchor='center')

    btnCancel = Button(top, text="Выход", font=("Arial Bold", 16), command=pass_btn_cancel_clicked)
    btnCancel.place(x=360, y=160, anchor='center')

    top.transient(window)
    # мы передаем поток данному виджету т.е. делаем его модальным
    top.grab_set()
    # фокусируем наше приложение на окне top
    #top.focus_set()
    input_pass.focus_set()
    # мы задаем приложению команду, что пока не будет закрыто окно top пользоваться другим окном будет нельзя
    top.wait_window()


if not os.path.exists('data.sqlite'):
    msg_box_alert()

auth_dialog()

# инициализация БД
db = sqlite3.connect('data.sqlite')
cursor = db.cursor()
# создание новой таблицы, если другой нет
cursor.execute('''
                       CREATE TABLE IF NOT EXISTS data (
                       id INTEGER PRIMARY KEY,
                        site TEXT NOT NULL UNIQUE,
                        pass TEXT NOT NULL)''')


# Выборка данных из БД
def select_data():
    cursor.execute("SELECT * FROM data")
    result_all = cursor.fetchall()  # лист кортежей, в каждом - строка из БД
    return result_all


# Добавление записи в БД
def add_data(site: str, password: str):
    cursor.execute("INSERT INTO data (site, pass) VALUES (?, ?)", (site, password))
    db.commit()


# Удаление записи из БД
def delete_data(site: str):
    site = base64.b64encode((site + SALT).encode()).decode()
    cursor.execute("DELETE FROM data WHERE site=?", (site,))
    db.commit()


window.mainloop()
db.close()
