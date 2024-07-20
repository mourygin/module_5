#import subprocess
import tkinter as tk
import csv
import tkinter.filedialog
#from tkinter import ttk
from tkinter.messagebox import showwarning
from screeninfo import get_monitors
import hashlib
#import subprocess
#import sys
import webbrowser
import time
import threading

class User():
    def __init__(self, nickname, password, age):
        self.nickname = nickname
        self.password = password
        self.age = age
        self.email = ''
        self.supervisor = False
        self.blocked = False

class Video():
    def __init__(self, title, duration, link=''):
        self.title = title
        self.duration = duration
        self.time_now = 0
        self.adult_mode = False
        self.link = link

class Database():
    # Таблица Users. Словарь где ключ - nickname, а значение - список [password, age, E-mail, supervisor, blocked]
    data_users = {'empty': ['0', 0 , '', False, False], \
                  'Admin': ['e3afed0047b08059d0fada10f400c1e5', 34, 'admin@urtube.ru', True, False],
                  'User-max': ['9b51eab87f5669af47c08c788e7ed401', 25, 'user-max@urtube.ru', False, False], \
                  'User-min': ['842129e226f40d24412e10e69df3e0fd', 16, 'user-min@urtube.ru', False, False],
                  'Bad user': ['bae60998ffe4923b131e3d6e4c19993e', 44, 'Bjaka@urtube.ru', False, True]}
    # Таблица Films. Словарь где ключ - title, а значение - список [duration, time_now, adult_mode, link]
    data_movies = {'Java или Python: что выбрать в 2024?': [1142, 0, False, 'https://www.youtube.com/watch?v=x38DO4fc2VE'],
                        'Хочу замуж за программиста!': [1122, 300, True, 'https://www.youtube.com/watch?v=IKdhzNr4duw'],
                   'Пустой отладочный ролик': [20, 5, True, '']}
    #def __init__(self):
    def set_film_moment(film_title, time):
        Database.data_movies[film_title][1] = time
    def get_f_link(film_title):
        f_link = Database.data_movies[film_title][3]
        return f_link
    def get_film_lenght(film_title):
        f_leght = Database.data_movies[film_title][0]
        return f_leght
    def get_f_cur_time(film_title):
        cur_time = Database.data_movies[film_title][1]
        return cur_time
    def get_hash_psw():
        hash = Database.data_users[user2edit][0]
        return hash
    def delete_user():
        global user2edit
        del Database.data_users[user2edit]
    def get_status_supervisor(nickname):
        status = Database.data_users[nickname][3]
        return status
    def get_film_details(title):
        details = 'FILM DETAILS:\nFilm duration - ' + PolyWin.sec2time(Database.data_movies[title][0]) + '\nAge restrictions - '
        if Database.data_movies[title][2]:
            details += '18+'
        else:
            details += '0+'
        return details
    def get_user_age(login):
        age = int(Database.data_users[login][1])
        return age
    def get_status_blocked(nickname):
        status = Database.data_users[nickname][4]
        return status
    def get_user_mail(login):
        age = Database.data_users[login][2]
        return age
    def check_password(login, password):
        pwd_from_db = Database.data_users[login][0]
        pwd_enc = password.encode()
        pwd_hash = hashlib.md5(pwd_enc)
        if pwd_hash.hexdigest() == pwd_from_db:
            return True
        else:
            return False
    def get_user_list():
        user_list = list(Database.data_users.keys())
        user_list.remove('empty')
        return user_list
    def get_film_list():
        film_list = Database.data_movies.keys()
        return film_list
    def add_user(nickname, password, age, email, supervisor_status, blocked):
        Database.data_users[nickname] = list([password, age, email, supervisor_status, blocked])
        PolyWin.reform_win('win_umng')
        return
    def add_film(title, duration, adult_mode = False, link = ''):
        Database.data_movies[title] = list([duration, 0, adult_mode, link])
        PolyWin.reform_win('win_fmng')
        return
    def del_film(title):
        del Database.data_movies[title]
class UrTube(Database, User):
    DB = Database()
    def __init__(self):
        self.users = []
        self.videos = []
        self.current_user = None
class PolyWin(Database, User):#, UrTube):
    pointer_min = 58# Крайняя левая позиция ползунка в окне просмотра фильма
    pointer_max = 645# Крайняя правая позиция ползунка в окне просмотра фильма
    film_lenght = 0# Длительность фильма
    film_moment = 0# Текущее время просмотра фильма (сек.)
    pointer_cur_x = 58# Текущая позиция ползунка в окне просмотра фильма
    play_bool = False# Флаг воспроизведения/останова фильма
    #films_mult = set([])# Кажется это лишнее. Пока уберем...
    film_filter = ''
    film_title = ''
    vidgets = []# Список текущих виджетов формы. Предназначен для очистки формы при смене редима.
    pointers = []# Список текущих виджетов "ползунка" в окне просмотра фильма. Предназначен для очистки формы при смещении ползунка.
    win_params = []# Список режимов окна и соответствующих им параметров формы.(служебное название режима, заголовок окна, ширина и высота формы)
    win_params.append(['win_login', 'UrTube. Login.', 280, 185])
    win_params.append(['win_reg', 'UrTube. Registration.', 325, 250])
    win_params.append(['win_main', 'UrTube. Videos.', 425, 430])
    win_params.append(['win_fmng', 'UrTube. Video manager.', 425, 430])
    win_params.append(['win_addf', 'UrTube. Add film.', 330, 160])
    #win_params.append(['win_umng', 'UrTube. User manager.', 450, 500])
    win_params.append(['win_umng', 'UrTube. User manager.', 450, 340])
    win_params.append(['win_screen', 'UrTube. Cinema.', 820, 650])
    actual_username = ''
    new_user = False
    def sec2time(sec):# Перевод секунд в строку формата HH:MM:SS
        sec = int(sec)
        h = sec // 3600
        m = (sec - 3600 * h) // 60
        s = sec - 3600 * h - 60 * m
        time_str = ''
        if h > 0:
            time_str = str(h) + ':'
        if m < 10:
            time_str += '0' + str(m) + ':'
        else:
            time_str += str(m) + ':'
        if s < 10:
            time_str += '0' + str(s)
        else:
            time_str += str(s)
        return time_str

    def clear_win():# Очистка формы от текущих виджетов при смене режима
        while len(PolyWin.vidgets) > 0:
            tk_obj = PolyWin.vidgets.pop()
            tk_obj.destroy()
    def clear_pointers():# Удаление ползунка/ков при его сдвиге.
        while len(PolyWin.pointers) > 0:
            point_obj = PolyWin.pointers.pop()
            point_obj.destroy()
            return
    def win_login_reg():# Нажатие кнопки REGISTER в форме авторизации
        PolyWin.reform_win('win_reg')
    def win_reg_cancel():# Нажатие кнопки CANCEL в форме регистрации
        PolyWin.reform_win('win_login')
    def win_any_exit():# Выход из главного окна (из программы)
        exit()
    def win_any_main():# Переход в главное окно
        PolyWin.reform_win('win_main')
    # def win_usr_edit():
    #     PolyWin.reform_win('win_edit_user')
    def win_addf_back():# закрытие окна добавления фильма без сохранения. Переход в FILM-MANAGER.
        PolyWin.reform_win('win_fmng')

    def reform_win(win_mode='win_login'): #                         ПЕРЕФОРМАТИРОВАНИЕ ОКНА (Все формы программы \
        # реализованы в одном полиморфном окне, которое видоизеняется при помощи данной функции)
        global msg_text, win, root, film_moment, play_bool#, films_mult
        user2edit = ''
        # def win_main_search():
        #     global film_filter
        #     if PolyWin.film_filter == '':
        #         pass
        #     else:
        #         pass

        def win_any_logoff():# Завершение сеанса подключения
            PolyWin.actual_username = ''
            my_tube.current_user = None
            PolyWin.reform_win('win_login')

        def win_login_login():# Обработка нажатия кнопки LOGIN в форме аутентификации
            global root, msg_text
            user_list = Database.get_user_list()
            nickname = login_entry.get()
            password = psw_entry.get()
            if nickname in user_list:
                if Database.check_password(nickname, password):
                    if Database.get_status_blocked(nickname):
                        showwarning(title="UrTube.", message="Your account is blocked. Contact service administrator.")
                    else:
                        aa = Database.get_user_age(nickname)
                        PolyWin.actual_username = nickname
                        my_tube.current_user = User(nickname, password, aa)
                        PolyWin.reform_win('win_main')
                else:
                    showwarning(title="UrTube.", message="Username and password do not match!")
            else:
                showwarning(title="UrTube.", message="The user '" + str(nickname) + "' not found in database. Check spelling, please.")
        def win_main_fmng():# Переход из главного окна в FILE-MANAGER
            PolyWin.reform_win('win_fmng')
        def win_main_umng():# Переход из главного окна в USER-MANAGER
            PolyWin.reform_win('win_umng')
        def win_main_watch():# Переход из главного окна просмотра фильма
            PolyWin.reform_win('win_screen')
        def refill_listbox():# Обновление listbox-а со списком фильмов с учетом установленного фильтра
            try:
                film_list = list(Database.get_film_list())
                criterion = filtr_entry.get()
                criterion_ = criterion.upper()
                while films_lbx.size() > 0:
                    films_lbx.delete(0, films_lbx.size())
                for i in film_list:
                    if (not UrTube.DB.data_movies[i][2]) or (Database.get_user_age(PolyWin.actual_username) >= 18):
                        if i.upper().find(criterion_) >= 0:
                            films_lbx.insert(0, i)
            except:
                return
        if win_mode != 'timer':#
            PolyWin.clear_win()
            for i in PolyWin.win_params:
                if i[0] == win_mode:
                    PolyWin.root = i[1]
                    if win_mode == 'win_umng':
                        str_umng_postfix = '+' + str(int(max_h_pix / 2 - i[2] / 2)) + '+' + str(int(max_v_pix / 2 - i[3] / 2))
                    str_geometry = str(i[2]) + 'x' + str(i[3]) + '+' + str(int(max_h_pix / 2 - i[2] / 2)) + '+' + str(int(max_v_pix / 2 - i[3] / 2))
                    root.geometry(str_geometry)
                    root.title(i[1])
                    PolyWin.clear_win()
                    break
        if win_mode == 'win_login': #                                       ФОРМА ВХОДА
            login_lbl = tk.Label(text='Username:')
            login_lbl.place(x=30, y=15)
            PolyWin.vidgets.append(login_lbl)
            login_entry = tk.Entry(width=25)
            login_entry.place(x=100, y=15)
            PolyWin.vidgets.append(login_entry)
            psw_lbl = tk.Label(text='Password:')
            psw_lbl.place(x=30, y=55)
            PolyWin.vidgets.append(psw_lbl)
            psw_entry = tk.Entry(width=25)
            psw_entry.place(x=100, y=55)
            PolyWin.vidgets.append(psw_entry)
            login_btn = tk.Button(text='Login', width=10, command=win_login_login)
            login_btn.place(x=30, y=95)
            PolyWin.vidgets.append(login_btn)
            exit_btn = tk.Button(text='Exit', width=10, command=PolyWin.win_any_exit)
            exit_btn.place(x=170, y=95)
            PolyWin.vidgets.append(exit_btn)
            registre_btn = tk.Button(text='Register', width=10, command=PolyWin.win_login_reg)
            registre_btn.place(x=30, y=135)
            PolyWin.vidgets.append(registre_btn)
        elif win_mode == 'win_reg': #                                       ФОРМА РЕГИСТРАЦИИ
            def win_reg_reg():
                nick = login_entry.get()
                psw1 = psw_entry.get()
                psw2 = psw_cnf_entry.get()
                age = age_entry.get()
                mail = mail_entry.get()
                if nick == '' or age == '' or mail == '' or psw1 == '':
                    showwarning('Empty fields!', 'You must fill out all fields.')
                else:
                    if psw1 != psw2:
                        showwarning('Password fields!', "The contents of the password fields do not match.")
                    else:
                        psw = psw1.encode()
                        password = str(hashlib.md5(psw).hexdigest())
                        Database.add_user(nick, password, age, mail, False, False)
                        PolyWin.actual_username = nick
                        PolyWin.reform_win('win_main')
            login_lbl = tk.Label(text='Username:')
            login_lbl.place(x=10, y=15)
            PolyWin.vidgets.append(login_lbl)
            login_entry = tk.Entry(width=25)
            login_entry.place(x=150, y=15)
            PolyWin.vidgets.append(login_entry)
            psw_lbl = tk.Label(text='Password:')
            psw_lbl.place(x=10, y=55)
            PolyWin.vidgets.append(psw_lbl)
            psw_entry = tk.Entry(width=25)
            psw_entry.place(x=150, y=55)
            PolyWin.vidgets.append(psw_entry)
            psw_cnf_lbl = tk.Label(text='Confirm password:')
            psw_cnf_lbl.place(x=10, y=85)
            PolyWin.vidgets.append(psw_cnf_lbl)
            psw_cnf_entry = tk.Entry(width=25)
            psw_cnf_entry.place(x=150, y=85)
            PolyWin.vidgets.append(psw_cnf_entry)
            age_lbl = tk.Label(text='Your age:')
            age_lbl.place(x=10, y=125)
            PolyWin.vidgets.append(age_lbl)
            age_entry = tk.Entry(width=25)
            age_entry.place(x=150, y=125)
            PolyWin.vidgets.append(age_entry)
            mail_lbl = tk.Label(text='Your E-mail:')
            mail_lbl.place(x=10, y=165)
            PolyWin.vidgets.append(mail_lbl)
            mail_entry = tk.Entry(width=25)
            mail_entry.place(x=150, y=165)
            PolyWin.vidgets.append(mail_entry)
            ok_btn = tk.Button(text='OK', width=10, command=win_reg_reg)
            ok_btn.place(x=50, y=210)
            PolyWin.vidgets.append(ok_btn)
            cancel_btn = tk.Button(text='Cancel', width=10, command=PolyWin.win_reg_cancel)
            cancel_btn.place(x=185, y=210)
            PolyWin.vidgets.append(cancel_btn)
        elif win_mode == 'win_main': #                                       ГЛАВНАЯ ФОРМА
            filtr_lbl = tk.Label(text='Filter/Search string:')
            filtr_lbl.place(x=10, y=15)
            PolyWin.vidgets.append(filtr_lbl)
            filtr_entry = tk.Entry(width=32)
            filtr_entry.place(x=120, y=15)
            PolyWin.vidgets.append(filtr_entry)
            #search_str = str(filtr_entry.get())
            search_btn = tk.Button(text='Search', width=11, command=refill_listbox)
            search_btn.place(x=325, y=12)
            PolyWin.vidgets.append(search_btn)

            films_lbx = tk.Listbox(width=50, height=20)
            films_lbx.place(x=10, y=50)
            PolyWin.vidgets.append(films_lbx)
            refill_listbox()
            #watch_btn.config(state='disabled')
            def on_change(event):
                widget = event.widget  # виджет, с которым произошло событие (в данном случае listbox)
                selection = widget.curselection()  # получаем tuple из индексов выделенных элементов
                if selection:  # если что-то выделено (tuple не пустой)
                    PolyWin.film_title = widget.get(selection[0])  # Текст в выбранной строке
                    PolyWin.film_lenght = Database.get_film_lenght(PolyWin.film_title)
                    details_text = Database.get_film_details(PolyWin.film_title)
                    details_lbl.config(text=details_text)
                    watch_btn.config(state='normal')
            films_lbx.bind('<<ListboxSelect>>', on_change)
            #--------------------------------------------------------
            exit_btn = tk.Button(text='Exit', width=11, command=PolyWin.win_any_exit)
            exit_btn.place(x=325, y=350)
            PolyWin.vidgets.append(exit_btn)
            logof_btn = tk.Button(text='Logoff', width=11, command=win_any_logoff)
            logof_btn.place(x=325, y=315)
            PolyWin.vidgets.append(logof_btn)
            watch_btn = tk.Button(text='Watch film', width=11, command=win_main_watch)
            watch_btn.config(state='disabled')
            watch_btn.place(x=325, y=270)
            PolyWin.vidgets.append(watch_btn)
            details_lbl = tk.Label(text='', justify='left')
            details_lbl.place(x=10, y=375)
            PolyWin.vidgets.append(details_lbl)
            if Database.get_status_supervisor(PolyWin.actual_username):
                user_mng_btn = tk.Button(text='User manager', width=11, command=win_main_umng)
                user_mng_btn.place(x=325, y=220)
                PolyWin.vidgets.append(user_mng_btn)
                film_mng_btn = tk.Button(text='Film manager', width=11, command=win_main_fmng)
                film_mng_btn.place(x=325, y=185)
                PolyWin.vidgets.append(film_mng_btn)
        elif win_mode == 'win_fmng': #                                       ФОРМА ФИЛЬМ-МЕНЕДЖМЕНТА
            film_title = ''
            filtr_lbl = tk.Label(text='Filter/Search string:')
            filtr_lbl.place(x=10, y=15)
            PolyWin.vidgets.append(filtr_lbl)
            filtr_entry = tk.Entry(width=32)
            filtr_entry.place(x=120, y=15)
            PolyWin.vidgets.append(filtr_entry)
            search_btn = tk.Button(text='Search', width=11, command=refill_listbox)
            search_btn.place(x=325, y=12)
            PolyWin.vidgets.append(search_btn)
            films_lbx = tk.Listbox(width=50, height=20)
            films_lbx.place(x=10, y=50)
            PolyWin.vidgets.append(films_lbx)
            refill_listbox()
            #delf_btn.config(state='disabled')
            def on_change(event):
                global film_title
                widget = event.widget  # виджет, с которым произошло событие (в данном случае listbox)
                selection = widget.curselection()  # получаем tuple из индексов выделенных элементов
                if selection:  # если что-то выделено (tuple не пустой)
                    PolyWin.film_title = widget.get(selection[0])  # Текст в выбранной строке
                    details_text = Database.get_film_details(PolyWin.film_title)
                    details_lbl.config(text=details_text)
                    delf_btn.config(state='normal')
            def win_fmng_del():
                global film_title
                Database.del_film(film_title)
                refill_listbox()
                delf_btn.config(state='disabled')
                details_lbl.config(text='')
            def win_fmng_add():
                PolyWin.reform_win('win_addf')
            def win_fmng_load():
                fn = tkinter.filedialog.askopenfilename(initialfile="*.csv")
                if fn != '':
                    with open(fn, 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile, dialect='excel', delimiter=';')
                        for row in reader:
                            key = row[0]
                            value = list([row[1], row[2], row[3]])
                            Database.add_film(row[0], row[1], row[2], row[3])
                    refill_listbox()
            films_lbx.bind('<<ListboxSelect>>', on_change)
            back_btn = tk.Button(text='Back', width=11, command=PolyWin.win_any_main)
            back_btn.place(x=325, y=350)
            PolyWin.vidgets.append(back_btn)
            details_lbl = tk.Label(text='', justify='left')
            details_lbl.place(x=10, y=375)
            PolyWin.vidgets.append(details_lbl)
            addf_btn = tk.Button(text='Add film', width=11, command=win_fmng_add)
            addf_btn.place(x=325, y=50)
            PolyWin.vidgets.append(addf_btn)
            delf_btn = tk.Button(text='Delete film', width=11, command=win_fmng_del)
            delf_btn.place(x=325, y=85)
            delf_btn.config(state='disabled')
            PolyWin.vidgets.append(delf_btn)
            load_btn = tk.Button(text='Load films', width=11, command=win_fmng_load)
            load_btn.place(x=325, y=120)
            PolyWin.vidgets.append(load_btn)
        elif win_mode == 'win_addf': #                                       ФОРМА ДОБАВЛЕНИЯ ФИЛЬМА
            def add_film():
                title = film_title_entry.get()
                duration = film_duration_entry.get()
                adult_mode = age_restrictions_ckb
                if title != '' and duration != '' and duration.isnumeric():
                    Database.add_film(title, 0, duration, (not adult_chk))
                    win_fadd_back
                else:
                    pass
            def win_fadd_back():
                PolyWin.reform_win('win_fmng')
            film_title_lbl = tk.Label(text='Film title:')
            film_title_lbl.place(x=10, y=15)
            PolyWin.vidgets.append(film_title_lbl)
            film_title_entry = tk.Entry(width=40)
            film_title_entry.place(x=73, y=15)
            PolyWin.vidgets.append(film_title_entry)
            film_duration_lbl = tk.Label(text='Film duration:')
            film_duration_lbl.place(x=10, y=45)
            PolyWin.vidgets.append(film_duration_lbl)
            film_duration_entry = tk.Entry(width=7)
            film_duration_entry.place(x=270, y=45)
            PolyWin.vidgets.append(film_duration_entry)
            age_restrictions_lbl = tk.Label(text='Age restrictions (18+):')
            age_restrictions_lbl.place(x=10, y=75)
            PolyWin.vidgets.append(age_restrictions_lbl)
            adult_chk = tk.BooleanVar()
            age_restrictions_ckb = tk.Checkbutton(variable=adult_chk)
            age_restrictions_ckb.place(x=300, y=75)
            PolyWin.vidgets.append(age_restrictions_ckb)
            addf_btn = tk.Button(text='Add film', width=10, command=add_film)
            addf_btn.place(x=30, y=110)
            PolyWin.vidgets.append(addf_btn)
            cancel_btn = tk.Button(text='Cancel', width=10, command=PolyWin.win_addf_back)
            cancel_btn.place(x=210, y=110)
            PolyWin.vidgets.append(cancel_btn)
        elif  win_mode == 'win_umng': #                                       ФОРМА ЮЗЕР-МЕНЕДЖМЕНТА
            def refill_u_listbox():# Обновление содержимого listbox-а ПОЛЬЗОВАТЕЛИ
                # global
                user_list = list(Database.get_user_list())
                while users_lbx.size() > 0:
                    users_lbx.delete(0, users_lbx.size())
                for i in user_list:
                    users_lbx.insert(0, i)
            def del_user_f():# Обработка нажатия кнопки DELETE в user-manager-e
                global user2edit
                Database.delete_user()
                refill_u_listbox()
                return
            def add_user_f():# Обработка нажатия кнопки ADD USER. Поля ввода/редактирования параметров расположены за пределами границы формы.
                global new_user, user2edit
                str_geometry = '450x500' + str_umng_postfix
                root.geometry(str_geometry)# Изменение размеров формы чтобы открыть скрытые поля.
                new_user = True
                user2edit = 'empty'
                nick_ent.delete(0, len(nick_ent.get()))
                age_ent.delete(0, len(age_ent.get()))
                psw1_ent.delete(0, len(psw1_ent.get()))
                psw2_ent.delete(0, len(psw2_ent.get()))
                mail_ent.delete(0, len(mail_ent.get()))
                return
            def edit_user_f():# Обработка нажатия кнопки EDIT в user-manager-e
                global new_user, user2edit
                str_geometry = '450x500' + str_umng_postfix
                root.geometry(str_geometry)# Изменение размеров формы чтобы открыть скрытые поля.
                new_user = False
            def save_user():# Обработка нажатия кнопки SAVE в режиме создания/редактирования пользователя.
                global new_user, user2edit
                if new_user:
                    #Create new user
                    if nick_ent.get() == '' or age_ent.get() == '' or mail_ent.get() == '' or psw1_ent.get() == '':
                        showwarning('Empty fields!', "You must fill out all required fields of the form.")
                    else:
                        if psw1_ent.get() != psw2_ent.get():
                            showwarning('Password fields!', "The contents of the password fields do not match.")
                        else:
                            nick = nick_ent.get()
                            age = int(age_ent.get())
                            mail = mail_ent.get()
                            adm = bool(is_adm.get())
                            block = bool(is_blocked.get())
                            psw = psw1_ent.get().encode()
                            password = str(hashlib.md5(psw).hexdigest())
                            Database.add_user(nick, password, age,mail,adm,block)
                            refill_u_listbox()
                else:
                    #Save user parameters changes
                    nick = nick_ent.get()
                    age = int(age_ent.get())
                    mail = mail_ent.get()
                    adm = bool(is_adm.get())
                    if psw1_ent.get() == '':
                        password = Database.get_hash_psw()
                    else:
                        psw = psw1_ent.get().encode()
                        password = str(hashlib.md5(psw).hexdigest())
                    block = bool(is_blocked.get())
                    del_user_f()
                    Database.add_user(nick, password, age,mail,adm,block)
                    refill_u_listbox()

            def win_umng_cancel():# Обработка нажатия кнопки CANCEL в режиме создания/редактирования пользователя.
                my_tube.current_user = None
                PolyWin.actual_username = ''
                nick_ent.delete(0,len(nick_ent.get()))
                age_ent.delete(0,len(age_ent.get()))
                mail_ent.delete(0,len(mail_ent.get()))
                is_adm.set(False)
                psw1_ent.delete(0,len(psw1_ent.get()))
                psw2_ent.delete(0,len(psw2_ent.get()))
                is_blocked.set(False)
                refill_u_listbox()
                str_geometry = '450x340' + str_umng_postfix
                root.geometry(str_geometry)

            users_lbx = tk.Listbox(width=50, height=19)
            users_lbx.place(x=10, y=10)
            PolyWin.vidgets.append(users_lbx)
            def win_umng_load():# Обработка нажатия кнопки LOAD USERLIST
                fn = tkinter.filedialog.askopenfilename(initialfile="*.csv")
                if fn != '':
                    with open(fn, 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile, dialect='excel', delimiter=';')
                        for row in reader:
                            key = row[0]
                            value = list([row[1], row[2], row[3], row[4], row[5]])
                            Database.add_user(row[0], row[1], row[2], row[3], bool(int(row[4])), bool(int(row[5])))
            refill_u_listbox()
            def on_change(event):# Псевдособытие CLICK в списке пользователей при выборе пользователя для его просмотра/редактирования/удаления
                global user2edit, new_user
                widget = event.widget
                selection = widget.curselection()
                if selection:
                    user2edit = widget.get(selection[0])
                    nick_ent.delete(0, len(nick_ent.get()))
                    nick_ent.insert(0, user2edit)
                    age_ent.delete(0, len(age_ent.get()))
                    age_ent.insert(0, Database.get_user_age(user2edit))
                    mail_ent.delete(0, len(mail_ent.get()))
                    mail_ent.insert(0, Database.get_user_mail(user2edit))
                    is_adm.set(bool(Database.get_status_supervisor(user2edit)))
                    is_blocked.set(bool(Database.get_status_blocked(user2edit)))
                    edit_user_btn.config(state='normal')
                    del_user_btn.config(state='normal')
                    new_user = False
            users_lbx.bind('<<ListboxSelect>>', on_change)
            load_ulist_btn = tk.Button(text='Load userlist', width=13, command=win_umng_load)# Кнопка LOAD USERLIST
            load_ulist_btn.place(x=340, y=10)
            PolyWin.vidgets.append(load_ulist_btn)
            add_user_btn = tk.Button(text='Add user', width=13, command=add_user_f)# Кнопка добавления пользователя
            add_user_btn.place(x=340, y=45)
            PolyWin.vidgets.append(add_user_btn)
            del_user_btn = tk.Button(text='Delete user', width=13, command=del_user_f)# Кнопка удаления пользователя
            del_user_btn.place(x=340, y=80)
            del_user_btn.config(state='disabled')
            PolyWin.vidgets.append(del_user_btn)
            edit_user_btn = tk.Button(text='Edit user', width=13, command=edit_user_f)# Кнопка редактирования пользователя
            edit_user_btn.place(x=340, y=115)
            edit_user_btn.config(state='disabled')
            PolyWin.vidgets.append(edit_user_btn)
            back_btn = tk.Button(text='Back', width=13, command=PolyWin.win_any_main)# Кнопка выхода из USER-MANAGER-a
            back_btn.place(x=340, y=305)
            PolyWin.vidgets.append(back_btn)
            line_lbl = tk.Label(text=chr(9472)*36)# Линия отделяющая зону полей ввода/редактирования параметров пользователя
            line_lbl.place(x=5, y=330)
            PolyWin.vidgets.append(line_lbl)
            nick_lbl = tk.Label(text='Nickname:')
            nick_lbl.place(x=10, y=355)
            PolyWin.vidgets.append(nick_lbl)
            nick_ent = tk.Entry(width=39)# Ввод/редактирование имени пользователя.
            nick_ent.place(x=75, y=355)
            PolyWin.vidgets.append(nick_ent)
            age_lbl = tk.Label(text='Age:')
            age_lbl.place(x=10, y=380)
            PolyWin.vidgets.append(age_lbl)
            age_ent = tk.Entry(width=5)# Ввод/редактирование возраста пользователя.
            age_ent.place(x=75, y=380)
            PolyWin.vidgets.append(age_ent)
            mail_lbl = tk.Label(text='E-mail:')
            mail_lbl.place(x=115, y=380)
            PolyWin.vidgets.append(mail_lbl)
            mail_ent = tk.Entry(width=23)# Ввод/редактирование почты пользователя.
            mail_ent.place(x=170, y=380)
            PolyWin.vidgets.append(mail_ent)
            adm_lbl = tk.Label(text='Admin:')
            adm_lbl.place(x=10, y=405)
            PolyWin.vidgets.append(adm_lbl)
            blk_lbl = tk.Label(text='Blocked:')
            blk_lbl.place(x=115, y=405)
            PolyWin.vidgets.append(blk_lbl)
            #---------------------------------------------
            is_adm = tk.BooleanVar()# Две tk-переменные, привязанные к соответствующим виджетам.
            is_blocked = tk.BooleanVar()
            adm_chk = tk.Checkbutton(root, variable=is_adm)# Флажок установки/снятия админских прав пользователя
            adm_chk.place(x=70, y=405)
            PolyWin.vidgets.append(adm_chk)
            blk_chk = tk.Checkbutton(root, variable=is_blocked)# Флажок установки/отмены блокировки аккаунта пользователя
            blk_chk.place(x=165, y=405)
            PolyWin.vidgets.append(blk_chk)
            #---------------------------------------------
            psw1_lbl = tk.Label(text='Password:')
            psw1_lbl.place(x=10, y=430)
            PolyWin.vidgets.append(psw1_lbl)
            psw1_ent = tk.Entry(width=32)# Поле ввода пароля
            psw1_ent.place(x=115, y=430)
            PolyWin.vidgets.append(psw1_ent)
            psw2_lbl = tk.Label(text='Repeat password:')
            psw2_lbl.place(x=10, y=455)
            PolyWin.vidgets.append(psw2_lbl)
            psw2_ent = tk.Entry(width=32)# Поле повторного ввода пароля
            psw2_ent.place(x=115, y=455)
            PolyWin.vidgets.append(psw2_ent)
            save_btn = tk.Button(text='Save', width=13, command=save_user)# Кнопка SAVE в режиме  ввода/редактирования параметров пользователя
            save_btn.place(x=340, y=350)
            PolyWin.vidgets.append(save_btn)
            cancel_btn = tk.Button(text='Cancel', width=13, command=win_umng_cancel)# Кнопка CANCEL в режиме  ввода/редактирования параметров пользователя
            cancel_btn.place(x=340, y=385)
            PolyWin.vidgets.append(cancel_btn)
        elif win_mode == 'win_screen':#                     ОКНО ПРОСМОТРА ФИЛЬМА
            PolyWin.play_bool = False

            def from_cinema():# Обработка нажатия кнопки BACK. Выход из окна просмотра фильма
                global film_title
                Database.set_film_moment(PolyWin.film_title, PolyWin.film_moment)
                PolyWin.clear_pointers()
                PolyWin.reform_win('win_main')
            def to_start():# Обработка нажатия кнопки "В НАЧАЛО ФИЛЬМА"
                PolyWin.film_moment = 0
                PolyWin.clear_pointers()
                pointer_btn = tk.Button(text='')
                pointer_btn.place(x=PolyWin.pointer_min, y=620)
                PolyWin.pointers.append(pointer_btn)
                return
            def play_stop():# Обработка нажатия кнопки PLAY/STOP
                if PolyWin.play_bool:
                    PolyWin.play_bool = False
                    play_stop_btn.config(text=chr(9205))
                    return
                else:
                    PolyWin.play_bool = True
                    play_stop_btn.config(text=chr(9208))
                    repeater(1)# Запуск самовоспроизводящегося таймера
                    return
            def on_youtube():
                webbrowser.open(f_link)
                return
            #                                                                               ВИДЖЕТЫ:
            film_max = Database.get_film_lenght(PolyWin.film_title)
            you_whatch_lbl = tk.Label(text="You are watching the film", font='Arial,24')#                           Вы смотрите
            you_whatch_lbl.place(x=300, y=200)
            PolyWin.vidgets.append(you_whatch_lbl)
            f_title_lbl = tk.Label(text=PolyWin.film_title,bd=5, font='Arial 20 bold', width=47, justify='left')#   Название фильма
            f_title_lbl.place(x=1, y=230)
            PolyWin.vidgets.append(f_title_lbl)
            to_start_btn = tk.Button(text=chr(9204), command=to_start)#, font='Arial 16 bold')#                     Кнопка "В начало фильма"
            to_start_btn.place(x=5, y=620)
            PolyWin.vidgets.append(to_start_btn)
            play_stop_btn = tk.Button(text=chr(9205), command=play_stop)#, font='Arial 16 bold')#                   Кнопка PLAY/STOP
            play_stop_btn.place(x=30, y=620)
            PolyWin.vidgets.append(play_stop_btn)
            #                                                                                                       Ползунок
            line_lbl = tk.Label(text=chr(9472)*98)
            line_lbl.place(x=60, y=620)
            PolyWin.vidgets.append(line_lbl)
            pointer_btn = tk.Button(text='')#, command=set_new_moment)
            pointer_btn.place(x=645, y=620)
            PolyWin.pointers.append(pointer_btn)
            PolyWin.film_moment = Database.get_f_cur_time(PolyWin.film_title)#                                      Установка текущего момента фильма
            x_ = PolyWin.pointer_min + int((PolyWin.pointer_max - PolyWin.pointer_min) / int(film_max) * PolyWin.film_moment)
            pointer_btn.place(x=x_, y=620)
            to_main_btn = tk.Button(text='Back', command= from_cinema)#, font='Arial 16 bold')#                     Кнопка "Выход"
            to_main_btn.place(x=780, y=620)
            PolyWin.vidgets.append(to_main_btn)
            to_youtube = tk.Button(text='Watch on YouTube', command=on_youtube)  # , font='Arial 16 bold')#         Кнопка YouTube
            to_youtube.place(x=665, y=620)
            PolyWin.vidgets.append(to_youtube)
            f_link = Database.get_f_link(PolyWin.film_title)
            if f_link == '':
                to_youtube.config(state='disabled')
            #repeater(1)
            pass
        if win_mode == 'timer':  #                              СДВИГ ПОЛЗУНКА
            pointer_btn = tk.Button(text='')
            PolyWin.clear_pointers()
            pointer_btn.place(x=PolyWin.pointer_cur_x, y=620)
            PolyWin.pointers.append(pointer_btn)

    def __init__(self):
        global root
        root = tk.Tk()
        #---------------------------------------
        root.resizable(width=False, height=False)
        PolyWin.reform_win()
        #---------------------------------------
        root.mainloop()
def every_second():# ЕЖЕСЕКУНДНАЯ ОБРАБОТКА ОКНА.
    if PolyWin.play_bool:
        time_ = PolyWin.film_moment
        if time_ < PolyWin.film_lenght:
            time_ += 1
            PolyWin.film_moment = time_
            PolyWin.pointer_cur_x = int(PolyWin.pointer_min + (PolyWin.pointer_max - PolyWin.pointer_min) * time_ / PolyWin.film_lenght)
            PolyWin.reform_win('timer')
        else:# Если достигнут конец фильма
            PolyWin.film_moment = 0
            PolyWin.play_bool= False
            PolyWin.pointer_cur_x = PolyWin.pointer_min
            PolyWin.clear_pointers()
            Database.set_film_moment(PolyWin.film_title,0)
            PolyWin.reform_win('win_screen')
    return
def repeater(interval):# Создает в отдельном потоке таймер, который через заданный интервал вновь вызовет эту функцию.
    #Запускает функцию ежесекундной обработки окна. Вызов функции repeater происходит при нажатии кнопки PLAY.
    if PolyWin.play_bool:
        threading.Timer(interval, repeater, [interval]).start()
        every_second()



if __name__ == '__main__':
    # Определение параметров экрана для центрального позиционирования окна
    # Протестировано только на одномониторных системах.
    for monitor in get_monitors():
        max_h_pix = monitor.width
        max_v_pix = monitor.height
    my_tube = UrTube()
    win = PolyWin()
    user2edit = ''