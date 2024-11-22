import tkinter as tk
import os
import sys
import traceback
from tkinter import messagebox
import threading
import time
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from tkinter import simpledialog
from tkinter import filedialog
import inspect
import ctypes
import datetime
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ECS
from selenium.common.exceptions import TimeoutException
import platform

_os_type_ = platform.system().lower()

if _os_type_ == 'windows':
    from subprocess import CREATE_NO_WINDOW

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = os.getcwd()
win = tk.Tk()
win.title('问卷')
win.resizable(False, False)
frm00 = tk.Frame(win, highlightthickness=2)
frm00.grid(row=0, column=0, columnspan=1, sticky='WENS')
frm01 = tk.Frame(win, bg='#3eddb9', highlightthickness=2)
frm10 = tk.Frame(win, bg='#3eddb9', highlightthickness=2)
frm11 = tk.Frame(win, bg='#4381f3', highlightthickness=2)
frm02 = tk.Frame(win, bg='#4381f3', highlightthickness=2)
frm12 = tk.Frame(win, bg='#ac56eb', highlightthickness=2)
frm22 = tk.Frame(win, bg='#ac56eb', highlightthickness=2)

global bil
bi = tk.Text(win)
hanshu = tk.Text(win)
Excel = tk.Text(win)
log = tk.Text(win)


def judge(fenshu):
    root = '问卷信息.txt'
    with open(root, 'r+', encoding='utf-8') as (f):
        q = f.readlines()
    if len(q) > fenshu - 1:
        quit()


def save_hanshu():
    fileName = os.path.join(BASE_DIR, '填写表.txt')
    with open(fileName, 'w', encoding='utf-8') as (f):
        f.write(hanshu.get(0.0, tk.END))


def save_bi():
    fileName = os.path.join(BASE_DIR, '导出表.txt')
    with open(fileName, 'w', encoding='utf-8') as (f):
        f.write(bi.get(0.0, tk.END))


def save_Excel():
    fileName = os.path.join(BASE_DIR, '数据表.txt')
    with open(fileName, 'w', encoding='utf-8') as (f):
        f.write('')


def save_log():
    fileName = os.path.join(BASE_DIR, '日志信息.txt')
    with open(fileName, 'w', encoding='utf-8') as (f):
        f.write('')


hanshu_button = tk.Button(win, text='保存填写表文档', command=save_hanshu, font=('华文新魏', 19))
bi_button = tk.Button(win, text='保存导出表文档', command=save_bi, font=('华文新魏', 19))
Excel_button = tk.Button(win, text='删除数据表文档', command=save_Excel, font=('华文新魏', 19))
log_button = tk.Button(win, text='删除日志', command=save_log, font=('华文新魏', 19))


def sjbtxt():
    fileName = os.path.join(BASE_DIR, '数据表.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read()
    Excel.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    Excel_button.grid(row=2, column=2, padx=5, pady=5)
    Excel.delete(0.0, tk.END)
    Excel.insert('insert', text)
    bi.grid_forget()
    bi_button.grid_forget()
    hanshu.grid_forget()
    hanshu_button.grid_forget()
    log.grid_forget()
    log_button.grid_forget()
    WA()


def txbtxt():
    fileName = os.path.join(BASE_DIR, '填写表.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read()
    hanshu.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    hanshu_button.grid(row=2, column=2, padx=5, pady=5)
    hanshu.delete(0.0, tk.END)
    hanshu.insert('insert', text)
    bi.grid_forget()
    bi_button.grid_forget()
    Excel.grid_forget()
    Excel_button.grid_forget()
    log.grid_forget()
    log_button.grid_forget()
    background_label.grid_forget()
    background_label1.grid_forget()
    WA()


def dcbtxt():
    fileName = os.path.join(BASE_DIR, '导出表.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read()
    bi.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    bi_button.grid(row=2, column=2, padx=5, pady=5)
    bi.delete(0.0, tk.END)
    bi.insert('insert', text)
    hanshu.grid_forget()
    hanshu_button.grid_forget()
    Excel.grid_forget()
    Excel_button.grid_forget()
    log.grid_forget()
    log_button.grid_forget()
    background_label.grid_forget()
    background_label1.grid_forget()


def logtxt():
    fileName = os.path.join(BASE_DIR, '日志信息.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read()
    log.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    log_button.grid(row=2, column=2, padx=5, pady=5)
    log.delete(0.0, tk.END)
    log.insert('insert', text)
    bi_button.grid_forget()
    bi.grid_forget()
    hanshu_button.grid_forget()
    hanshu.grid_forget()
    Excel.grid_forget()
    Excel_button.grid_forget()
    background_label.grid_forget()
    background_label1.grid_forget()
    WA()


def closeall():
    bi_button.grid_forget()
    bi.grid_forget()
    hanshu_button.grid_forget()
    hanshu.grid_forget()
    Excel.grid_forget()
    Excel_button.grid_forget()
    log.grid_forget()
    log_button.grid_forget()
    background_label.grid_forget()
    background_label1.grid_forget()
    WA()


menubar = tk.Menu(win)
fileMenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='打开', menu=fileMenu)
fileMenu.add_command(label='填写表txt', command=txbtxt)
fileMenu.add_command(label='导出表txt', command=dcbtxt)
fileMenu.add_command(label='数据表txt', command=sjbtxt)
fileMenu.add_command(label='关闭新打开的界面', command=closeall)
fileMenu.add_separator()
fileMenu.add_command(label='退出', command=(win.quit))
win.config(menu=menubar)
editMenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='日志记录', menu=editMenu)
editMenu.add_command(label='打开日志', command=logtxt)
editMenu.add_separator()
editMenu.add_command(label='关闭新打开的界面', command=closeall)
background_label = tk.Button(win)
background_label1 = tk.Button(win)


def closed():
    background_label.grid_forget()
    background_label1.grid_forget()


def data_savingEX():
    X1 = x1.get()
    Y1 = y1.get()
    Begin = begin.get()
    End = end.get()
    SS = ss.get()
    return (
        X1, Y1, Begin, End, SS)


def WA():
    w1.grid_forget()
    w2.grid_forget()
    w3.grid_forget()
    w4.grid_forget()
    w5.grid_forget()
    w6.grid_forget()
    w7.grid_forget()
    w8.grid_forget()
    w9.grid_forget()
    w10.grid_forget()
    w11.grid_forget()
    w12.grid_forget()
    w13.grid_forget()


def QB():
    w1.grid(row=0, column=2, padx=6, pady=6)
    w2.grid(row=0, column=3, padx=6, pady=6)
    w3.grid(row=0, column=4, padx=6, pady=6)
    w4.grid(row=0, column=5, padx=6, pady=6)
    w5.grid(row=0, column=6, padx=6, pady=6)
    w6.grid(row=0, column=7, padx=6, pady=6)
    w8.grid(row=1, column=3, padx=6, pady=6)
    w9.grid(row=1, column=4, padx=6, pady=6)
    w13.grid(row=2, column=2, columnspan=6, padx=6, pady=6)
    bi_button.grid_forget()
    bi.grid_forget()
    hanshu_button.grid_forget()
    hanshu.grid_forget()
    Excel.grid_forget()
    Excel_button.grid_forget()
    log.grid_forget()
    log_button.grid_forget()
    background_label.grid_forget()
    background_label1.grid_forget()


ss = tk.StringVar()
dt = tk.Entry(frm10, textvariable=ss)


def EC():
    value = filedialog.askopenfilenames(title='选择文件', filetypes=[('images', '*.xlsx'), ('All Files', '*')])
    tk.Entry(frm00, textvariable="username")
    ss.set('')
    ss.set(value[0])
    return value[0]


x1 = tk.StringVar()
y1 = tk.StringVar()
begin = tk.StringVar(value=25)
end = tk.StringVar()
w13 = tk.Button(win, text='选择Excel表文件', font=('华文新魏', 19), relief='groove', command=EC)
w1 = tk.Label(win, text='回填表：', font=('华文新魏', 15))
w2 = tk.Label(win, text='第', font=('华文新魏', 15))
w3 = tk.Spinbox(win, width=10, from_=1, to=10000, textvariable=x1)
w4 = tk.Label(win, text='行==到第', font=('华文新魏', 15))
w5 = tk.Spinbox(win, width=10, from_=1, to=10000, textvariable=y1)
w6 = tk.Label(win, text='列', font=('华文新魏', 15))
w7 = tk.Label(win, text='填入', font=('华文新魏', 15))
w8 = tk.Label(win, text='连续报错次数', font=('华文新魏', 15))
w9 = tk.Spinbox(win, width=10, from_=1, to=1000, textvariable=begin)
w10 = tk.Label(win, text='题==到第', font=('华文新魏', 15))
w11 = tk.Spinbox(win, width=10, from_=1, to=1000, textvariable=end)
w12 = tk.Label(win, text='题', font=('华文新魏', 15))
backfill = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='Excel回填设置', menu=backfill)
backfill.add_command(label='回填设置一', command=QB)
backfill.add_separator()
backfill.add_command(label='关闭新打开的界面', command=closeall)
frm01.grid(row=0, column=0, columnspan=1, sticky='WENS')
frm10.grid(row=0, column=1, sticky='WNES')
frm11.grid(row=1, column=0, sticky='WNES')
frm02.grid(row=1, column=1, columnspan=1, sticky='WNES')
frm12.grid(row=2, column=0, columnspan=2, sticky='WNES')


def clear2():
    url.set('')


def data_saving2():
    UIL = url.get()
    TIMES = times.get()
    TIME = random.randint(int(time1.get()), int(time2.get()))
    F1 = time1.get()
    F2 = time2.get()
    A = hour.get()
    B = minute.get()
    C = sec.get()
    print(TIME)
    D = int(A) * 3600 + 60 * int(B) + int(C)
    return UIL, TIMES, TIME, D, A, B, C, F1, F2


url = tk.StringVar()
times = tk.StringVar()
time1 = tk.StringVar()
time2 = tk.StringVar()
tk.Label(frm01, text='输入问卷链接', font=('华文新魏', 19)).grid(row=0, column=0, columnspan=4, padx=6, pady=6)
tk.Button(frm01, text='问卷链接', relief='ridge').grid(row=1, column=0, padx=6, pady=6)
tk.Entry(frm01, width=30, textvariable=url, relief='groove').grid(row=1, column=1, padx=6, pady=6)
tk.Button(frm01, text='清除', command=clear2).grid(row=1, column=2, padx=6, pady=6)
tk.Button(frm01, text='填写问卷次数：', relief='groove').grid(row=2, column=0, padx=6, pady=6)
tk.Spinbox(frm01, width=10, from_=1, to=1000, textvariable=times).grid(row=2, column=1, padx=6, pady=6)
tk.Button(frm01, text='提交时间（s）').grid(row=3, column=0, padx=6, pady=6)
tk.Spinbox(frm01, width=10, from_=1, to=1000, textvariable=time1).grid(row=3, column=1, padx=6, pady=6)
tk.Button(frm01, text='提交时间（s）').grid(row=3, column=0, padx=6, pady=6)
tk.Spinbox(frm01, width=10, from_=2, to=1000, textvariable=time2).grid(row=3, column=2, padx=6, pady=6)
hour = tk.StringVar()
minute = tk.StringVar()
sec = tk.StringVar()
tk.Spinbox(frm01, width=10, from_=0, to=1000, textvariable=hour).grid(row=4, column=1, padx=6, pady=6)
tk.Button(frm01, text='小时').grid(row=4, column=0, padx=6, pady=6)
tk.Spinbox(frm01, width=10, from_=0, to=1000, textvariable=minute).grid(row=5, column=1, padx=6, pady=6)
tk.Button(frm01, text='分钟').grid(row=5, column=0, padx=6, pady=6)
tk.Spinbox(frm01, width=10, from_=0, to=1000, textvariable=sec).grid(row=6, column=1, padx=6, pady=6)
tk.Button(frm01, text='秒').grid(row=6, column=0, padx=6, pady=6)


def ti_shi():
    messagebox.showinfo('提示', '需要点击运行后可倒计时')


tk.Button(frm01, text='运行\n倒计\n时间', font=('华文新魏', 19), command=ti_shi).grid(
    row=4, column=2, rowspan=3, padx=6, pady=6)


def clear3():
    ip_adr.set('')
    api_url.set('')


def data_saving3():
    IP = ip_adr.get()
    API_UIL = api_url.get()
    V = popo.get()
    return IP, API_UIL, V


def i_request():
    save3 = data_saving3()[1]
    try:
        url_1 = str(save3).split(',')
        url_1 = random.choice(url_1)
    except:
        url_1 = str(save3)

    print(url_1)
    response = requests.get(url=url_1)
    proxies = response.text.strip()
    return proxies


def see_about():
    from tkinter import messagebox
    from tkinter import filedialog
    try:
        aa = proxies
        aaa = aa.split(':')[0]
        value = messagebox.askokcancel('是否查询', '查询会卡顿、且有延迟\n是否继续查询？')
        print(value)
        if value:
            url = 'https://api.vvhan.com/api/getIpInfo'
            kv = {'user-agent': 'Mozilla/5.0'}
            data = {'ip': aa}
            r = requests.get(url, headers=kv, verify=False, params=data)
            print(r.url)
            print(r.json()['info'])
            country = r.json()['info']['country']
            prov = r.json()['info']['prov']
            city = r.json()['info']['city']
            lsp = r.json()['info']['lsp']
            messagebox.showinfo('归属地查询成功', '查询成功\n' + aa + '\n' + country + prov + city + lsp)
    except:
        value = messagebox.showwarning('归属地查询失败', '检查网络是否链接？\n检查ip是否正确？')
        print('查询失败')


ip_adr = tk.StringVar()
api_url = tk.StringVar()
title = tk.Label(frm10, text='代理ip', font=('华文新魏', 19))
title.grid(row=0, column=0, columnspan=3, padx=6, pady=6)
tk.Button(frm10, text='ip:端口号').grid(row=1, column=0, padx=6, pady=6)
tk.Entry(frm10, width=30, textvariable=ip_adr).grid(row=1, column=1, padx=6, pady=6)
tk.Button(frm10, text='清除', command=clear3).grid(row=1, column=2, rowspan=2, padx=6, pady=6)
tk.Button(frm10, text='Api链接+').grid(row=2, column=0, padx=6, pady=6)
tk.Entry(frm10, width=30, textvariable=api_url).grid(row=2, column=1, padx=6, pady=6)
edt = tk.Text(frm10, width=30, height=2)
edt.grid(row=4, column=1, padx=5, pady=5, columnspan=2)


def oip():
    try:
        edt = tk.Text(frm10, width=30, height=2)
        edt.grid(row=4, column=1, padx=5, pady=5, columnspan=2)
        edt.insert('insert', proxies)
        edt.config(state='disabled')
    except:
        messagebox.showinfo('提示', '检查是否使用ip')


edt.config(state='disabled')
tk.Button(frm10, text='查询当前ip', command=oip).grid(row=4, column=0, columnspan=1, padx=6, pady=6)
frm10.rowconfigure(5, weight=1)


def kkk():
    print(popo.get())


popo = tk.IntVar(value=2)
tk.Radiobutton(frm10, text='开启代理ip', variable=popo, value=0, command=kkk).grid(row=3, column=0, padx=10,
                                                                               pady=10)
tk.Radiobutton(frm10, text='开启代理Api', variable=popo, value=1, command=kkk).grid(row=3, column=1, padx=10,
                                                                                pady=10)
tk.Radiobutton(frm10, text='关闭', variable=popo, value=2, command=kkk).grid(row=3, column=2, padx=10, pady=10)
tk.Button(frm10, text='保存数据', command=data_saving3).grid(row=5, column=0, columnspan=1, padx=10, pady=10)
tk.Button(frm10, text='清楚数据', command=clear3).grid(row=5, column=1, columnspan=1, padx=10, pady=10)
tk.Button(frm10, text='查询ip归属地', command=see_about).grid(row=5, column=2, columnspan=1, padx=10, pady=10)


def data_saving4():
    global check_s
    S = check_s.get()
    Source = source.get()
    return S, Source


tk.Label(frm11, text='浏览器配置', font=('华文新魏', 16)).grid(row=0, column=0, columnspan=3, padx=6, pady=6)
tk.Label(frm11, text='是否关闭浏览器', font=('华文中宋', 12)).grid(row=1, column=0, padx=6, pady=6)


def rrr():
    pass


check_s = tk.BooleanVar()
tk.Checkbutton(frm11, text='是', variable=check_s, width=20, command=rrr).grid(row=1, column=1, padx=6, pady=6)


def root_in():
    pass


source = tk.IntVar(value=0)
tk.Label(frm11, text='问卷来源', font=('华文新魏', 15)).grid(row=2, column=0, columnspan=3, padx=6, pady=6)
tk.Radiobutton(frm11, text='手机安卓', variable=source, value=0, command=root_in, font=('华文中宋',
                                                                                    12)).grid(row=3, column=0,
                                                                                              padx=10,
                                                                                              pady=10)
tk.Radiobutton(frm11, text='手机苹果', variable=source, value=1, command=root_in, font=('华文中宋',
                                                                                    12)).grid(row=3, column=1,
                                                                                              padx=10,
                                                                                              pady=10)
tk.Radiobutton(frm11, text='手机微信', variable=source, value=2, command=root_in, font=('华文中宋',
                                                                                    12)).grid(row=4, column=0,
                                                                                              padx=10,
                                                                                              pady=10)
tk.Radiobutton(frm11, text='混合来源', variable=source, value=3, command=root_in, font=('华文中宋',
                                                                                    12)).grid(row=4, column=1,
                                                                                              padx=10,
                                                                                              pady=10)


def mouse_down():
    value = messagebox.askokcancel('是否查询', '查询会卡顿、且有延迟\n是否继续查询？')


def clear5():
    pass


def data_saving5():
    Z1 = z1.get()
    Tishu = timu_shu.get()
    return (
        Tishu, Z1)


def fangshi1():
    try:
        iop = []
        kk = eval(data_saving5()[0])
        print(kk)
        url = data_saving2()[0]
        header = {
            'authority': "'s.taobao.com'",
            'cache-control': "'max-age=0'",
            'sec-ch-ua': '\'"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"\'',
            'sec-ch-ua-mobile': "'?0'",
            'sec-ch-ua-platform': '\'"Windows"\'',
            'upgrade-insecure-requests': "'1'",
            'user-agent': "'Mozilla/5.0 (Linux; U; Android 10; zh-cn; MI 9 Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.12'",
            'accept': "'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'",
            'sec-fetch-site': "'same-origin'",
            'sec-fetch-mode': "'navigate'",
            'sec-fetch-user': "'?1'",
            'sec-fetch-dest': "'document'",
            'accept-language': "'zh-CN,zh;q=0.9'",
            'cookie': "'cna=w7y7GYch4kMCAasijBL1tcnw; xlly_s=1; t=d77b430a77fdf76d9c17f2806b57c2ff; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; _m_h5_tk=5ccf9d80baa24976d1bd97719fb7d377_1633327797887; _m_h5_tk_enc=2d2f907d5f3a86f04dbbf2aa73897ecd; _samesite_flag_=true; cookie2=16bd808d5d4c077a1e5f8e3abc00787e; _tb_token_=e3e5e0fd3333d; sgcookie=E1004cVmZPbUKd%2Bo2Y6ewiI7lmCD2rFerQ9K0Rx3PgQSSoYp%2FWW8LOvfo4oThh7eNLIEFm5uGhkQ9IUsgsWnv4%2BYBvCt6Z2xxPQJp498ChIaTCg%3D; unb=2202345247497; uc3=nk2=F5RBx%2BGr84TAocRa&lg2=URm48syIIVrSKA%3D%3D&vt3=F8dCujaCTG0Yn%2BEGbMY%3D&id2=UUphyItuGYNeDyMxrA%3D%3D; csg=fa72b214; lgc=tb4216148421; cancelledSubSites=empty; cookie17=UUphyItuGYNeDyMxrA%3D%3D; dnk=tb4216148421; skt=a19b5b0102a7b5ee; existShop=MTYzMzM1MjE0MQ%3D%3D; uc4=nk4=0%40FY4KoqHi383HYtpSM0RDmlOwk4iA8Tg%3D&id4=0%40U2grE1hEVww3EVoATgMbl4PMiyTEeIZt; tracknick=tb4216148421; _cc_=W5iHLLyFfA%3D%3D; _l_g_=Ug%3D%3D; sg=17e; _nk_=tb4216148421; cookie1=W8743JHOqTkZp4234GIqb8W2j3pRPRi2%2Ftn1Y16wf2Y%3D; enc=lEu3iTdRRzo2bKJ%2FSRTJ7W3KJmqkZoqJ8qTWcN7Fqxv4oVm4619kntnz84TzJb6SnF8AjFC43wovrgqFDVvISLE2T0wQC8D4h3ZzkSjIpSs%3D; mt=ci=0_1; uc1=existShop=false&pas=0&cookie21=Vq8l%2BKCLjhZM&cookie16=UtASsssmPlP%2Ff1IHDsDaPRu%2BPw%3D%3D&cookie14=Uoe3dP4mSshcOw%3D%3D&cookie15=WqG3DMC9VAQiUQ%3D%3D; JSESSIONID=338CCA02A39CF025F71F1BF78290B3CC; tfstk=c_YCB2ijKJ2I0Vnz8BGaUpf5nnb5aLH1sD6pO3g3IVJs9xRcBsmQutMG732Gz_C1.; l=eBxAgJEmghiX7hpyBO5Cnurza77OFIRbzPVzaNbMiInca6OA9FiEjNCLQg5JWdtjgt5xNFtzh0NBGRE6SuzLRxGjL77kRs5mpI96Re1..; isg=BD09yvnBAAYXt6RpoStY_zgXTJk32nEsV3r_rv-C1hTDNl9owymX_Iuk4Gpws4nk'"}
        r = requests.get(url, headers=header, timeout=30)
        soup = BeautifulSoup(r.text, 'html.parser')
        for op in kk:
            if type(op) == type(()):
                oop = range(op[0], op[1])
                p = list(oop)
                for opl in p:
                    iop.append(opl)

                iop.append(op[1])
            if type(op) == type([]):
                for opl in op:
                    iop.append(opl)

        fileName = os.path.join(BASE_DIR, '填写表.txt')
        with open(fileName, 'w', encoding='utf-8') as (f):
            hhhsss = []
            i = 0
            for a in soup.find_all(class_='fieldset'):
                for c in a.find_all('div', type=True):
                    i = i + 1
                    den = int(c.get('type'))
                    if den == 1:
                        y = '第' + str(i) + '题  填空'
                        f.write(y)
                        f.write('\n')
                        f.write(c.text)
                        f.write('\n')
                        if i in iop:
                            wj1 = '#gwenjuan1(driver, {}, datas(x,))# 第{}题'
                            wj1 = wj1.format(i, i)
                        else:
                            wj1 = '#wenjuan1(driver, {}, ["无"])# 第{}题 填空'
                            wj1 = wj1.format(i, i)
                        f.write(wj1)
                        f.write('\n')
                        hhhsss.append(wj1)
                        f.write('\n')
                    elif den == 2:
                        y = '第' + str(i) + '题  大填空'
                        f.write(y)
                        f.write('\n')
                        f.write(c.text)
                        f.write('\n')
                        if i in iop:
                            wj2 = '#gwenjuan2(driver,{},datas(x,))#第{}题 大填空'
                            wj2 = wj2.format(i, i)
                        else:
                            wj2 = '#wenjuan2(driver,{}, ["无"])#第{}题 大填空'
                            wj2 = wj2.format(i, i)
                        f.write(wj2)
                        f.write('\n')
                        hhhsss.append(wj2)
                        f.write('\n')
                    elif den == 3:
                        y = '第' + str(i) + '题  单选题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)

                        f.write('\n')
                        h = c.find_all('div', class_='ui-radio')
                        for p in h:
                            xinxi = p.text
                            f.write(xinxi)
                            f.write('\n')

                        if i in iop:
                            wj3 = '#gwenjuan3(driver,{},datas(x,))#第{}题 单选'
                            wj3 = wj3.format(i, i)
                        else:
                            wj3 = '#wenjuan3(driver,{}, {}, [])#第{}题 单选'
                            wj3 = wj3.format(i, len(h), i)
                        f.write(wj3)
                        f.write('\n')
                        hhhsss.append(wj3)
                        f.write('\n')
                    elif den == 4:
                        y = '第' + str(i) + '题  多选'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)

                        f.write('\n')
                        for h in c.find_all('div', class_='ui-controlgroup'):
                            for p in h:
                                xinxi = p.text
                                f.write(xinxi)
                                f.write('\n')

                            if i in iop:
                                g = 0
                                for l in h.find_all('a'):
                                    g = g + 1
                                    wj4 = '#gwenjuan4(driver,{},{}, datas(x,))#第{}题 多选'
                                    wj4 = wj4.format(i, g, i)
                                    f.write(wj4)
                                    f.write('\n')
                                    hhhsss.append(wj4)

                            else:
                                wj4 = '#wenjuan4(driver,{}, {}, [],random.randint(1, {}))#第{}题 多选'
                                wj4 = wj4.format(i, len(h), round(len(h) / 2) + 1, i)
                                f.write(wj4)
                                f.write('\n')
                                hhhsss.append(wj4)
                            f.write('\n')

                    elif den == 5:
                        y = '第' + str(i) + '题  形状单选'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)

                        f.write('\n')
                        if i in iop:
                            wj5 = '#gwenjuan5(driver,{},datas(x,))#第{}题 形状单选'
                            wj5 = wj5.format(i, i)
                        else:
                            for h in c.find_all('ul', tp='d'):
                                wj5 = '#wenjuan5(driver,{}, {},[])#第{}题 形状单选'
                                wj5 = wj5.format(i, len(h), i)

                        f.write(wj5)
                        f.write('\n')
                        hhhsss.append(wj5)
                        f.write('\n')
                    elif den == 6:
                        y = '第' + str(i) + '题  量表题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)

                        f.write('\n')
                        q = 0
                        p = c.find_all('tr', class_='rowtitle')
                        if i in iop:
                            for h in c.find_all('tr', tp=True):
                                p = c.find_all('tr', class_='rowtitle')[q].text
                                f.write(p)
                                f.write('\n')
                                q = q + 1
                                wj6 = '#gwenjuan6(driver,{}, {}, datas(x,))#第{}题 量表题'
                                wj6 = wj6.format(i, q, i)
                                f.write(wj6)
                                f.write('\n')
                                hhhsss.append(wj6)

                        else:
                            for h in c.find_all('tr', tp=True):
                                p = c.find_all('tr', class_='rowtitle')[q].text
                                f.write(p)
                                f.write('\n')
                                o = h.find_all('a')
                                q = q + 1
                                wj6 = '#wenjuan6(driver,{}, {}, {}, [])#第{}题 量表题'
                                wj6 = wj6.format(i, q, len(o), i)
                                f.write(wj6)
                                f.write('\n')
                                hhhsss.append(wj6)

                        f.write('\n')
                        print(iop)
                    elif den == 7:
                        y = '第' + str(i) + '题  下拉题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)

                        f.write('\n')
                        xla = c.find_all('option')
                        for xinxi in xla:
                            f.write(xinxi.text)
                            f.write('\n')

                        if i in iop:
                            wj7 = '#gwenjuan7(driver,{},datas(x,))#第{}题 下拉题'
                            wj7 = wj7.format(i, i)
                        else:
                            wj7 = '#wenjuan7(driver,{},{}, [])#第{}题 下拉题'
                            wj7 = wj7.format(i, len(xla) - 1, i)
                        f.write(wj7)
                        f.write('\n')
                        hhhsss.append(wj7)
                        f.write('\n')
                    elif den == 8:
                        y = '第' + str(i) + '题  滑动题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)
                            f.write('\n')

                        if i in iop:
                            wj8 = '#gwenjuan8(driver,{}, datas(x,))#第{}题 滑动题'
                            wj8 = wj8.format(i, i)
                        else:
                            wj8 = '#wenjuan8(driver,{},[])#第{}题 滑动题'
                            wj8 = wj8.format(i, i)
                        f.write(wj8)
                        f.write('\n')
                        hhhsss.append(wj8)
                        f.write('\n')
                    elif den == 9:
                        y = '第' + str(i) + '题  量表滑动题（和三个填空）'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)
                            f.write('\n')

                        r = 0
                        for q in c.find_all('input'):
                            try:
                                p = c.find_all('tr', class_='rowtitletr')[r].text
                                f.write(p)
                                f.write('\n')
                            except:
                                pass

                            r = r + 1
                            if i in iop:
                                wj9 = '#gwenjuan9(driver,{}, {}, datas(x,))#第{}题 量表滑动题（和三个填空）'
                                wj9 = wj9.format(i, r, i)
                            else:
                                wj9 = '#wenjuan9(driver,{}, {}, [])#第{}题 量表滑动题（和三个填空）'
                                wj9 = wj9.format(i, r, i)
                            f.write(wj9)
                            f.write('\n')
                            hhhsss.append(wj9)
                            f.write('\n')

                    elif den == 10:
                        wj10 = '#wenjuan10(driver,[])#第{}题 暂无不做矩阵多选'
                        f.write(wj10)
                        f.write('\n')
                    elif den == 11:
                        y = '第' + str(i) + '题  排序题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)
                            f.write('\n')

                        for xinxi in c.find_all('li'):
                            f.write(xinxi.text)
                            f.write('\n')

                        if i in iop:
                            h = c.find_all('li')
                            wj11 = '#gwenjuan11(driver,{},datas(x,))#第{}题 排序题'
                            wj11 = wj11.format(i, i)
                        else:
                            h = c.find_all('li')
                            wj11 = '#wenjuan11(driver,{}, {}, {})#第{}题 排序题'
                            wj11 = wj11.format(i, '[]', len(h), i)
                        f.write(wj11)
                        f.write('\n')
                        hhhsss.append(wj11)
                        f.write('\n')
                    elif den == 12:
                        y = '#第' + str(i) + '题  固定比例量表题'
                        f.write(y)
                        f.write('\n')
                        for q in c.find_all('div')[:1]:
                            f.write(q.text)
                            f.write('\n')

                        q = 0
                        for liab in c.find_all('input'):
                            try:
                                p = c.find_all('tr')[q * 2].text
                                f.write(p)
                                f.write('\n')
                            except:
                                pass

                            q = q + 1
                            if i in iop:
                                wj12 = '#gwenjuan12(driver, {}, {},datas(x,))#第{}题 固定比例量表题'
                                wj12 = wj12.format(i, q, i)
                            else:
                                wj12 = '#wenjuan12(driver, {}, {}, [])#第{}题 固定比例量表题'
                                wj12 = wj12.format(i, q, i)
                            f.write(wj12)
                            f.write('\n')
                            hhhsss.append(wj12)
                            f.write('\n')

                fan = '#fany(driver)#翻页'
                f.write(fan)
                f.write('\n')
                hhhsss.append(fan)

        messagebox.showinfo('成功', '提取成功')
    except:
        messagebox.showerror('失败', '查看链接是否输入\n回填题目格式是否正确')


def fangshi2():
    try:
        import re
        fileName = os.path.join(BASE_DIR, '填写表.txt')
        with open(fileName, 'r', encoding='utf-8') as f:
            text = f.read()
            lines = re.findall('#(.*?)#', text)
        with open((os.path.join(BASE_DIR, '导出表.txt')), 'w', encoding='utf-8') as (f):
            for i in lines:
                f.write(i)
                f.write('\n')

        messagebox.showinfo('成功', '导出成功')
    except:
        messagebox.showerror('失败', '查看填写表内容是否正确')


z1 = tk.StringVar()
timu_shu = tk.StringVar(value='(0),[0]')
lb = tk.Label(frm02, text='作答', font=('华文新魏', 15))
lb.grid(row=0, column=0, columnspan=4, padx=6, pady=6)
tk.Button(frm02, text='分析题目', font=('华文中宋', 12), command=fangshi1).grid(row=1, column=0, columnspan=1, padx=10,
                                                                        pady=10)
tk.Button(frm02, text='导出函数', font=('华文中宋', 12), command=fangshi2).grid(row=1, column=1, columnspan=1, padx=10,
                                                                        pady=10)
tk.Button(frm02, text='设置回填题目', font=('华文新魏', 14)).grid(row=2, column=0, columnspan=1, padx=10, pady=10)
w14 = tk.Label(frm02, text='回填Excel表中的第几个表：(默认为表一)', font=('华文新魏', 14))
w15 = tk.Spinbox(frm02, width=10, from_=1, to=10000, textvariable=z1)
zong = tk.Entry(frm02, width=30, textvariable=timu_shu)
zong.grid(row=2, column=1, padx=5, pady=5, columnspan=2)


def All_data():
    Data1 = data_saving2()
    Data2 = data_saving3()
    Data3 = data_saving4()
    Data4 = data_saving5()
    Data5 = data_savingEX()
    fileName = os.path.join(BASE_DIR, '数据表.txt')
    with open(fileName, 'w', encoding='utf-8') as (f):
        f.write(str(Data1))
        f.write('\n')
        f.write(str(Data2))
        f.write('\n')
        f.write(str(Data3))
        f.write('\n')
        f.write(str(Data4))
        f.write('\n')
        f.write(str(Data5))
        f.write('\n')
    print(data_saving5())
    print(data_savingEX())


def daoru_sj():
    fileName = os.path.join(BASE_DIR, '数据表.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read().split('\n')
        print(text)
        print(eval(text[0])[0])
    url.set(eval(text[0])[0])
    times.set(eval(text[0])[1])
    time1.set(eval(text[0])[7])
    time2.set(eval(text[0])[8])
    hour.set(eval(text[0])[4])
    minute.set(eval(text[0])[5])
    sec.set(eval(text[0])[6])
    ip_adr.set(eval(text[1])[0])
    api_url.set(eval(text[1])[1])
    popo.set(eval(text[1])[2])
    check_s.set(eval(text[2])[0])
    source.set(eval(text[2])[1])
    timu_shu.set(eval(text[3])[0])
    z1.set(eval(text[3])[1])
    x1.set(eval(text[4])[0])
    y1.set(eval(text[4])[1])
    begin.set(eval(text[4])[2])
    end.set(eval(text[4])[3])
    ss.set(eval(text[4])[4])


def qc_sj():
    url.set('')
    times.set('')
    time1.set('')
    time2.set('')
    hour.set('')
    minute.set('')
    sec.set('')
    ip_adr.set('')
    api_url.set('')
    timu_shu.set('')
    z1.set('')
    x1.set('')
    y1.set('')
    begin.set('')
    end.set('')
    ss.set('')


tk.Button(frm11, text='保存所有数据', command=All_data, font=('华文中宋', 12)).grid(row=5, column=2, columnspan=1,
                                                                          padx=10,
                                                                          pady=10)
tk.Button(frm02, text='清除所有数据', command=qc_sj, font=('华文中宋', 12)).grid(row=3, column=0, columnspan=1, padx=10,
                                                                       pady=10)
tk.Button(frm02, text='导入数据', font=('华文中宋', 12), command=daoru_sj).grid(row=3, column=1, columnspan=1, padx=10,
                                                                        pady=10)


def sxlogtxt():
    fileName = os.path.join(BASE_DIR, '日志信息.txt')
    with open(fileName, 'r', encoding='utf-8') as (f):
        text = f.read()
    log.delete(0.0, tk.END)
    log.insert('insert', text)


tk.Button(frm02, text='刷新日志', font=('华文新魏', 14), command=sxlogtxt).grid(row=3, column=2, columnspan=1, padx=10,
                                                                        pady=10)


def biil(q, weight, chioce_num=1):
    flat_list = []
    listxx = []
    for i in range(q):
        listxx.append(i + 1)
    for i in range(len(listxx)):
        for j in [listxx[i]] * weight[i]:
            flat_list.append(j)

    if chioce_num == 1:
        return random.sample(flat_list, 1)
    s = set()
    while len(s) < chioce_num:
        s.add(random.choice(flat_list))

    return s


def fany(driver):
    js = "document.querySelector('#divNext a').click()"
    driver.execute_script(js)


def wenjuan1(driver, q_num, text):
    try:
        jsString = "document.getElementById('q{}').removeAttribute('readonly')".format(q_num)
        driver.execute_script(jsString)
        a = driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '"]').send_keys(random.choice(text))
    except Exception:
        try:
            jsString = "document.getElementById('q{}').removeAttribute('readonly')".format(q_num)
            driver.execute_script(jsString)
            a = driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '"]//label//span').send_keys(
                random.choice(text))
        except:
            try:
                jsString = "document.querySelector('#q2').value='{}'".format(random.choice(text))
                driver.execute_script(jsString)
                print('没太')
            except:
                traceback.print_exc()
                print('没太难受')


def wenjuan2(driver, question_number, text):
    try:
        driver.find_element(By.XPATH, '//textarea[@id="q' + str(question_number) + '"]').send_keys(
            random.choice(text))
    except Exception:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(question_number) + '"]').send_keys(
                random.choice(text))
        except Exception:
            traceback.print_exc()
            pass


def wenjuan3(driver, question_number, option_num, weight):
    try:
        p = biil(option_num, weight)[0]
        driver.find_element(By.XPATH, '//div[@for="q' + str(question_number) + '_' + str(p) + '"]').click()
    except Exception:
        p = biil(option_num, weight)[0]
        driver.find_element(By.XPATH, '//label[@for="q' + str(question_number) + '_' + str(p) + '"]').click()

    return p


def wenjuan4(driver, question_number, option_num, weight, chioce_num):
    try:
        p = biil(option_num, weight, chioce_num)
        questions = driver.find_element(By.XPATH, '//*[@id="div%s"]/div[2]' % str(question_number))
        li = questions.find_elements(By.CLASS_NAME, 'ui-checkbox')
        for i in p:
            li[i - 1].click()
    except:
        traceback.print_exc()


def wenjuan5(driver, q_num, option_num, weight):
    try:
        questions = driver.find_element(By.XPATH, '//div[@id="div%s"]//div[2]//div/ul' % str(q_num))
        li = questions.find_elements(By.CLASS_NAME, 'td')
        p = biil(option_num, weight)[0]
        li[p - 1].click()
        return p
    except:
        try:
            questions = driver.find_element(By.XPATH, '//div[@id="div%s"]//div//div/ul' % str(q_num))
            li = questions.find_elements(By.CLASS_NAME, 'td')
            p = biil(option_num, weight)[0]
            li[p - 1].click()
            return p
        except:
            pass


def wenjuan6(driver, question_number, number, option_num, weight):
    try:
        p = biil(option_num, weight)[0]
        driver.find_element(By.XPATH,
                            '//tr[@id="drv' + str(question_number) + '_' + str(number) + '"]//td//ul//li[' + str(
                                p) + ']').click()
    except Exception:
        try:
            p = biil(option_num, weight)[0]
            driver.find_element(By.XPATH,
                                '//tr[@id="drv' + str(question_number) + '_' + str(number) + '"]' + '/td[' + str(
                                    p) + ']').click()
            return p
        except:
            try:
                p = biil(option_num, weight)[0]
                driver.find_element(By.XPATH,
                                    '//div[@id="div' + str(question_number) + '"]//tbody//tr[' + str(
                                        number) + ']/td[' + str(
                                        p) + ']').click()
            except:
                pass


def wenjuan7(driver, question_number, option_num, weight):
    try:
        answers = driver.find_element(By.XPATH,
                                      '//div//span[@id="select2-q%s-container"]' % str(question_number))
        answers.click()
        p = biil(option_num, weight)[0]
        time.sleep(1)
        ans = driver.find_elements(By.XPATH, ('//span//ul//li'))[p]
        ans.click()
    except:
        pass


def wenjuan8(driver, question_number, text):
    try:
        driver.find_element(By.XPATH, '//textarea[@id="q' + str(question_number) + '"]').send_keys(
            random.choice(text))
    except Exception:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(question_number) + '"]').send_keys(
                random.choice(text))
        except Exception:
            pass


def wenjuan9(driver, q_num, q, text):
    try:
        driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '_' + str(
            q) + '"]' + '/following-sibling::label[1]//span').send_keys(random.choice(text))
    except:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '_' + str(q - 1) + '"]').send_keys(
                random.choice(text))
        except:
            try:
                driver.find_element(By.XPATH, '//div[@id="div' + str(q_num) + '"]' + '//label//span').send_keys(
                    random.choice(text))
            except:
                pass


def wenjuan10():
    pass


def wenjuan11(driver, q_num, bili, n):
    try:
        temp_flag = 0
        temp_answer = []
        ccc = []
        count = 0

        def duoxuan(probability):

            def isInRange(num, start, end):
                if num >= start:
                    if num <= end:
                        return True
                return False

            i = random.randint(1, 100)
            if isInRange(i, 1, probability):
                flag = True
            else:
                flag = False
            return flag

        def quyu(list, ccc, Ttemp):
            shu = 0
            bbb = []
            temp_ans = []
            temp_flag = 0
            while shu < len(ccc):
                if duoxuan(list[ccc[shu]]):
                    temp_ans.append(ccc[shu])
                    temp_flag = temp_flag + 1
                else:
                    bbb.append(ccc[shu])
                shu = shu + 1

            for i in temp_ans:
                Ttemp.append(i)

            if len(temp_ans) == len(ccc):
                pass
            else:
                qqq = bbb
                quyu(list, qqq, Ttemp)
                return Ttemp

        while count < len(bili):
            if duoxuan(bili[count]):
                temp_answer.append(count)
                temp_flag = temp_flag + 1
            else:
                ccc.append(count)
            count = count + 1

        a = quyu(bili, ccc, [])
        for aa in a:
            temp_flag = temp_flag + 1
            temp_answer.append(aa)

        liss = []
        listture = []
        lists = temp_answer
        for ii in range(n):
            listture.append(lists[ii])
            for ioio in range(ii + 1):
                liss.append(lists[ioio])

            for i in range(n - 1 - ii):
                if lists[ii] > lists[i + 1 + ii]:
                    liss.append(lists[i + 1 + ii] + 1)
                else:
                    liss.append(lists[i + 1 + ii])

            lists = liss
            liss = []

        for i in range(n):
            js = "document.querySelectorAll('#div{} li')[{}].click()".format(q_num, listture[i])
            a = driver.execute_script(js)
            time.sleep(0.4)

    except:
        try:
            list = eval('bil[{}]'.format(n))
            for i in range(n):
                js = "document.querySelectorAll('#div{} li')[{}].click()".format(q_num, list[i] - 1)
                a = driver.execute_script(js)

        except:
            pass


def wenjuan12(driver, q_num, q, text):
    try:
        driver.find_element(By.XPATH, '//tr[@id="drv' + str(q_num) + '_' + str(q) + '"]//input').send_keys(
            random.choice(text))
    except:
        pass


def gwenjuan1(driver, q_num, text):
    try:
        jsString = "document.getElementById('q{}').removeAttribute('readonly')".format(q_num)
        driver.execute_script(jsString)
        a = driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '"]').send_keys(text)
    except Exception:
        try:
            jsString = "document.getElementById('q{}').removeAttribute('readonly')".format(q_num)
            driver.execute_script(jsString)
            a = driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '"]//label//span').send_keys(text)
        except:
            pass


def gwenjuan2(driver, question_number, text):
    try:
        driver.find_element(By.XPATH, '//textarea[@id="q' + str(question_number) + '"]').send_keys(text)
    except Exception:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(question_number) + '"]').send_keys(text)
        except Exception:
            pass


def gwenjuan3(driver, question_number, p):
    try:
        driver.find_element(By.XPATH, '//div[@for="q' + str(question_number) + '_' + str(p) + '"]').click()
    except Exception:
        driver.find_element(By.XPATH, '//label[@for="q' + str(question_number) + '_' + str(p) + '"]').click()

    return p


def gwenjuan4(driver, question_number, p, w):
    try:
        if w == 1:
            js = "document.querySelectorAll('#div{} span a')[{}].click()".format(question_number, p - 1)
            a = driver.execute_script(js)
    except Exception:
        pass


def gwenjuan5(driver, q_num, p):
    try:
        questions = driver.find_element(By.XPATH, '//div[@id="div%s"]//div[2]//div/ul' % str(q_num))
        li = questions.find_elements(By.CLASS_NAME, 'td')
        li[p - 1].click()
        return p
    except:
        try:
            questions = driver.find_element(By.XPATH, '//div[@id="div%s"]//div//div/ul' % str(q_num))
            li = questions.find_elements(By.CLASS_NAME, 'td')
            li[p - 1].click()
            return p
        except:
            pass


def gwenjuan6(driver, question_number, number, p):
    try:
        driver.find_element(By.XPATH,
                            '//tr[@id="drv' + str(question_number) + '_' + str(number) + '"]//td//ul//li[' + str(
                                p) + ']').click()
    except Exception:
        try:
            driver.find_element(By.XPATH,
                                '//tr[@id="drv' + str(question_number) + '_' + str(number) + '"]' + '/td[' + str(
                                    p) + ']').click()
            return p
        except:
            try:
                driver.find_element(By.XPATH,
                                    '//div[@id="div' + str(question_number) + '"]//tbody//tr[' + str(
                                        number) + ']/td[' + str(
                                        p) + ']').click()
            except:
                pass


def gwenjuan7(driver, question_number, p):
    try:
        answers = driver.find_element(By.XPATH,
                                      '//div//span[@id="select2-q%s-container"]' % str(question_number))
        answers.click()
        time.sleep(1)
        ans = driver.find_elements(By.XPATH, ('//span//ul//li')[p])
        ans.click()
    except:
        pass


def gwenjuan8(driver, question_number, text):
    try:
        driver.find_element(By.XPATH, '//textarea[@id="q' + str(question_number) + '"]').send_keys(text)
    except Exception:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(question_number) + '"]').send_keys(text)
        except Exception:
            pass


def gwenjuan9(driver, q_num, q, text):
    try:
        driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '_' + str(
            q) + '"]' + '/following-sibling::label[1]//span').send_keys(text)
    except:
        try:
            driver.find_element(By.XPATH, '//input[@id="q' + str(q_num) + '_' + str(q - 1) + '"]').send_keys(
                text)
        except:
            pass


def gwenjuan10():
    pass


def gwenjuan11(driver, q_num, p):
    try:
        js = "document.querySelectorAll('#div{} li a')[{}].click()".format(q_num, p - 1)
        a = driver.execute_script(js)
    except:
        try:
            js = "document.querySelectorAll('#div{} li')[{}].click()".format(q_num, p - 1)
            a = driver.execute_script(js)
        except:
            pass


def gwenjuan12(driver, q_num, q, text):
    try:
        driver.find_element(By.XPATH, '//tr[@id="drv' + str(q_num) + '_' + str(q) + '"]//input').send_keys(text)
    except:
        pass


def relevant(driver, w, option1, p, option2, weight2):
    for kp in range(option1):
        if w == kp + 1:
            kk1 = wenjuan3(driver, p, option2, weight2[kp])
            return kk1


def relevant11(driver, i, option1, weight1, p, option2, weight2):
    w = wenjuan3(driver, i, option1, weight1)
    for kp in range(option1):
        if w == kp + 1:
            kk1 = wenjuan3(driver, p, option2, weight2[kp])
            return (w, kk1)

rid_arr = {}

def mainx(nx):
    global proxies, rid_arr

    exec("iutrhj" + str(nx) + "['text'] = '已运行'")
    save2 = data_saving2()
    save3 = data_saving3()
    save4 = data_saving4()
    save5 = data_saving5()
    save6 = data_savingEX()

    def TIME():
        ciphe = datetime.datetime.now()
        return ciphe

    time.sleep(random.randint(int(save2[3]), int(save2[4])))
    x1 = int(save6[0])
    y1 = int(save6[1])
    begin = int(save6[2])
    end = int(save6[3])
    y = y1 - 1
    x = x1 - 2 - 1
    ctimes = 0
    flag = 0
    try:
        with open((os.path.join(BASE_DIR, '导出表.txt')), 'r', encoding='utf-8') as (f):
            lines = f.read()
            line = lines.split('\n')
            text1 = tuple(line)
    except:
        messagebox.showerror('出错', '查看当前目录中是否有导出表.txt')

    while ctimes < int(save2[1]):
        if not rid_arr[nx]:
            break
        try:
            url = save2[0]
            if int(save3[2]) == 0:
                proxies = save3[0]
            if int(save3[2]) == 1:
                proxies = i_request()
            if int(save3[2]) == 2:
                pass
            option = ChromeOptions()
            if save4[0]:
                option.add_argument('headless')
            try:
                prox = proxies
            except:
                prox = '--无'

            phone = [
                'user-agent="Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Mobile Safari/537.36"',
                'user-agent="Mozilla/5.0 (Linux; Android 10; BKL-AL00 Build/HUAWEIBKL-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 10)"',
                'user-agent="Mozilla/5.0 (Linux; U; Android 10; zh-cn; MI 9 Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.8.12"',
                'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"',
                'user-agent="Mozilla/5.0 (Linux; Android 5.0; SM-N9100 Build/LRX21V) > AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 > Chrome/37.0.0.0 Mobile Safari/537.36 > MicroMessenger/6.0.2.56_r958800.520 NetType/WIFI"',
                'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) > AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D257 > MicroMessenger/6.0.1 NetType/WIFI"']
            if int(save4[1]) == 0:
                option.add_argument(phone[random.choice([0, 2])])
            if int(save4[1]) == 1:
                option.add_argument(phone[3])
            if int(save4[1]) == 2:
                option.add_argument(phone[random.choice([4, 5])])
            if int(save4[1]) == 3:
                option.add_argument(phone[random.choice([0, 5])])
            T1 = TIME()
            fileName = os.path.join(BASE_DIR, '日志运行' + str(nx) + '.txt')
            with open(fileName, 'a', encoding='utf-8') as (f):
                logttxet = '当前使用的代理是' + str(prox) + '==' + '运行时间' + str(T1)
                f.write(logttxet)
                f.write('\n')
            fileName = os.path.join(BASE_DIR, '日志信息.txt')
            with open(fileName, 'a', encoding='utf-8') as (f):
                logttxet = '运行' + str(nx) + '正常运行！  提交成功次数' + str(ctimes) + '==' + '运行时间' + str(T1)
                f.write(logttxet)
                f.write('\n')
            option.add_experimental_option('excludeSwitches', ['enable-automation'])
            option.add_experimental_option('useAutomationExtension', False)
            time.sleep(0.5)
            if int(save3[2]) == 0 or int(save3[2]) == 1:
                print('代理开了')
                option.add_argument('--proxy-server=http://%s' % proxies)
            time.sleep(0.5)
            # 启动 ChromeDriver 进程并隐藏控制台窗口
            #subprocess.Popen([ChromeDriverManager().install()], creationflags=subprocess.CREATE_NO_WINDOW)
            # 创建 ChromeDriver 对象
            #driver = webdriver.Chrome(options=chrome_options)
            myservice = Service(ChromeDriverManager(version="114.0.5735.90").install())
            if _os_type_ == 'windows':
                myservice.creation_flags = CREATE_NO_WINDOW
            driver = webdriver.Chrome(options=option, service=myservice)
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
            driver.get(url)
            import pandas as pd
            path = str(save6[4])
            x = x + 1
            y = y1 - 1

            data = None
            try:
                data = pd.read_excel(path, sheet_name=(nx - 1))
                data.fillna((int(0)), inplace=True)
            except:
                pass

            def datas(x, y):
                try:
                    c = int(data.iloc[(x, y - 1)])
                except:
                    c = data.iloc[(x, y - 1)]

                return c

            js = "\n                            if (!!document.querySelector('#zhezhao2')){\n                 " \
                 "           document.querySelector('#zhezhao2').remove()\n                            " \
                 "document.querySelector('#divContent').className='divContent'\n                            " \
                 "openid=genRandomNum()\n                            " \
                 "access_token='49_pmnnj2iIdbV648vuLwf7u86GoxlllRqy-OoX9CNnw2nT2_tNj3" \
                 "-t6dMkFldIDah4j3Lje_niwaxaohObtIk2o1WJxLP7pBGkJfssq4AEKoU'\n                            " \
                 "isWeiXin=1\n                            }\n                             function " \
                 "genRandomNum(){\n                            let maxNum = 37;\n                            " \
                 "let count = 0;\n                            let str = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', " \
                 "'H', 'I', 'J', 'K','L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W','X', 'Y', " \
                 "'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-' ];\n                            " \
                 "let finalNum=''\n                            while(count < 22){\n                           " \
                 "     let i = randomNum(0,maxNum-1)\n                                if (i >= 0 && i < " \
                 "str.length) {\n                                    finalNum+=(str[i]);\n                    " \
                 "                count ++;\n                                }\n                            " \
                 "}\n                            return finalNum\n                        }\n\n               " \
                 "         function leijia(list,num){\n                            var sum = 0\n              " \
                 "              for(var i=0;i<num;i++){\n                                sum+=list[i];\n      " \
                 "                      }\n                            return sum;\n                        " \
                 "}\n\n                        //生成从minNum到maxNum的随机数\n                        function " \
                 "randomNum(minNum,maxNum){\n                            switch(arguments.length){\n          " \
                 "                      case 1:\n                                    return parseInt(" \
                 "Math.random()*minNum+1,10);\n                                    break;\n                   " \
                 "             case 2:\n                                    return parseInt(Math.random()*(" \
                 "maxNum-minNum+1)+minNum,10);\n                                    break;\n                  " \
                 "              default:\n                                    return 0;\n                     " \
                 "               break;\n                            }\n                        }\n "
            a = driver.execute_script(js)
            for r in text1:
                try:
                    print(r)
                    eval(compile(r, '人工函数.txt', 'exec'))
                    time.sleep(0.7)
                except:
                    traceback.print_exc()
                    pass

            time.sleep(int(save2[2]))
            # try:
            #     button = driver.find_element(By.ID, ('ctlNext'))
            #     driver.execute_script('arguments[0].click()', button)
            # except:
            #     traceback.print_exc()
            #     pass

            try:
                button = driver.find_element(By.ID, ('ctlNext'))
                driver.execute_script('arguments[0].click()', button)
            except:
                traceback.print_exc()
                pass

            time.sleep(1.5)
            try:
                js = "document.querySelector('#rectMask').click()"
                a = driver.execute_script(js)
            except:
                #traceback.print_exc()
                pass
            
            try:
                js = "document.querySelector('#rectTop').click()"
                a = driver.execute_script(js)
            except:
                #traceback.print_exc()
                pass
            
            try:
                js = "document.querySelector('#alert_box button').click()"
                a = driver.execute_script(js)
            except:
                #traceback.print_exc()
                pass
            
            try:
                js = "document.querySelector('#rectBottom').click()"
                a = driver.execute_script(js)
            except:
               # traceback.print_exc()
                pass
            
            try:
                js = "document.querySelector('.sm-ico-wave').click()"
                a = driver.execute_script(js)
            except:
                #traceback.print_exc()
                pass
            
            try:
                js = "document.querySelector('#ctlNext').click()"
                a = driver.execute_script(js)
            except:
                #traceback.print_exc()
                pass

            T2 = TIME()
            stat_time = T1.strftime('%Y-%m-%d %H:%M:%S')
            end_time = T2.strftime('%Y-%m-%d %H:%M:%S')
            dat_time = int((T2 - T1).total_seconds())

            try:
                WebDriverWait(driver, 12).until(ECS.url_contains("complete"))
                print("Desired url was rendered with in allocated time")

                ctimes = ctimes + 1
                flag = 0
                fileName = os.path.join(BASE_DIR, '日志运行' + str(nx) + '.txt')
                with open(fileName, 'a', encoding='utf-8') as (f):
                    logttxet = '第' + str(ctimes) + '次已完成!' + '--' + '开始时间：' + str(
                        stat_time) + '--' + '结束时间：' + str(end_time) + '==' + '当前使用的代理是' + str(
                        prox) + '==' + '运行时间' + str(dat_time) + '秒'
                    f.write(logttxet)
                    f.write('\n')
                    f.write('\n')
                driver.quit()

            except TimeoutException:
                print("Desired url was not rendered with in allocated time")
                flag = flag + 1
                fileName = os.path.join(BASE_DIR, '日志运行' + str(nx) + '.txt')
                with open(fileName, 'a', encoding='utf-8') as (f):
                    logttxet = '运行' + str(nx) + '====连续出错第' + str(flag) + '次--' + '开始时间：' + str(
                        stat_time) + '--' + '结束时间：' + str(end_time) + '==' + '当前使用的代理是' + str(
                        prox) + '==' + '运行时间' + str(dat_time) + '秒'
                    f.write(logttxet)
                    f.write('\n')
                    f.write('\n')
                    try:
                        answers = driver.find_elements(By.CSS_SELECTOR, ('div.errorMessage'))
                        io = []
                        for mlp in answers:
                            io.append(mlp.text)
                        print(io)
                        if '请选择选项' in io:
                            f.write('----出错原因===有题目未选择')
                    except:
                        traceback.print_exc()
                        pass

                    f.write('\n')
                print(flag)
                print(save6[2])
                if flag > int(save6[2]):
                    fileName = os.path.join(BASE_DIR, '日志信息.txt')
                    with open(fileName, 'a', encoding='utf-8') as (f):
                        logttxet = '运行' + str(nx) + '连续失败 ' + str(flag) + ' 次--已经停止'
                        f.write(logttxet)
                        f.write('\n')
                    break
                driver.quit()

        except:
            traceback.print_exc()
            pass


tid_arr = {}


def dx(nx):
    global tid_arr, rid_arr
    rid_arr[nx] = True
    try:
        def tmpmainx():
            mainx(nx)

        f1 = threading.Thread(target=tmpmainx)
        f1.setDaemon(True)
        f1.start()
        tid_arr[nx] = f1.ident
    except:
        traceback.print_exc()
        messagebox.showwarning('错误', '请重新尝试')


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    else:
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError('invalid thread id')
        else:
            if res != 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
                raise SystemError('PyThreadState_SetAsyncExc failed')


def fx(nx):
    try:
        print(tid_arr[nx])
        #_async_raise(tid_arr[nx], SystemExit)
        #os.kill(tid_arr[nx], 9)
        rid_arr[nx] = False
        messagebox.showinfo('线程结束', '请手动关闭浏览器')
        exec("iutrhj" + str(nx) + "['text'] = '运行" + str(nx) + "'")
    except:
        traceback.print_exc()
        messagebox.showwarning('错误', '线程已经结束请勿多次点击')


def stop_all():
    for i in tid_arr.keys():
        try:
            #_async_raise(tid_arr[i], SystemExit)
            #os.kill(tid_arr[i], 9)
            rid_arr[i] = False
            exec("iutrhj" + str(i + 1) + "['text'] = '运行" + str(i) + "'")
        except:
            pass


tk.Button(frm11, text='一键暂停所有', command=stop_all, font=('华文中宋', 12)).grid(row=5, column=1, columnspan=1,
                                                                          padx=10, pady=10)

for i in range(15):
    sxstmp = """
def tmpd""" + str(i + 1) + """():
    dx(""" + str(i + 1) + """)
def tmpf""" + str(i + 1) + """():
    fx(""" + str(i + 1) + """)
    """
    exec(sxstmp)

    exec("iutrhj" + str(i + 1) + " = tk.Button(frm12, text='运行" + str(i + 1) + "', command=tmpd" + str(i + 1) + ")")
    exec("iutrhj" + str(i + 1) + ".grid(row=0, column=" + str(i) + ", columnspan=1, padx=10, pady=10)")
    exec("iutrhs" + str(i + 1) + " = tk.Button(frm12, text='停止" + str(i + 1) + "', command=tmpf" + str(i + 1) + ")")
    exec("iutrhs" + str(i + 1) + ".grid(row=1, column=" + str(i) + ", columnspan=1, padx=10, pady=10)")

frm12.rowconfigure(2, weight=1)

win.rowconfigure(5, weight=1)
win.columnconfigure(0, weight=1)
win.columnconfigure(1, weight=1)
win.rowconfigure(0, weight=1)
win.rowconfigure(1, weight=1)
win.mainloop()
