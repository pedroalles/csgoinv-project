import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.figure import Figure
from matplotlib import ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
matplotlib.use("TkAgg")

# from dateutil import parser
# import PyQt5
# import pylab

import sqlite3
import time
import datetime
import threading

########################################################################################

t_start = time.time()

URL = 'https://csgobackpack.net/?nick=pedroalles&currency=BRL'

page = requests.get(URL, headers={})
# print("request done")
table = pd.read_html(page.text)
# print("table done")
table_df = pd.DataFrame(table[0])
# print("table df done")
table_final = pd.DataFrame()

soup = BeautifulSoup(page.content, 'html.parser')
user_name = soup.find(class_="media-heading").text

id_col = table_df['#'].apply(lambda x: ("{:03d}".format(int(x))))
name_col = table_df['Name'].apply(lambda x: str(x[10:]).title())
amount_col = table_df['Amount']
price_col = table_df['Price'].apply(lambda x: ("{:.2f}".format(float(x[2:]))))
total_col = table_df['In Total'].apply(lambda x: ("{:.2f}".format(float(x[2:]))))
trend_col = table_df['Trend(%)'].apply(lambda x: ("{:+.2f}".format(float(x))))

table_final['ID'] = id_col
table_final['Sticker'] = name_col
table_final['Amount'] = amount_col
table_final['Price'] = price_col
table_final['In Total'] = total_col
table_final['Trend(%)'] = trend_col

total_value = table_df['In Total'].apply(lambda x: float(x[2:])).sum()
total_value = "{:.2f}".format(total_value)
total_value_print = "R$ "+ total_value

total_quant = table_df['Amount'].sum()

########################################################################################

conection = sqlite3.connect('INV_doG.db')  # criando conexao com o banco de dados
c = conection.cursor()  # criando o cursor

def create_table():  # criando a tabela
    c.execute(
        'CREATE TABLE IF NOT EXISTS dados (id INTEGER PRIMARY KEY, date text, quantidade text, valor real, stemp integer)')

create_table()  

def dataentry():  # inserindo dados

    date = str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%d/%m/%Y - %H:%M:%S'))
    dateStemp = (int(time.time()))
    c.execute("INSERT INTO dados VALUES (null,?,?,?,?)", (date, str(total_quant), total_value, dateStemp))
    conection.commit()  # funcao commit para salvar os dados

dataentry()  

########################################################################################

def createNewWindow():
    global newWindow

    try:
        newWindow.destroy()
    except:
        pass
    
    newWindow = Toplevel(root)

    newWindow.attributes('-alpha', 0.0)  # make window transparent

    # newWindow.bind('<Escape>', onclick3)
    newWindow.title('Inventory Graph')
    newWindow.resizable(False, False)
    newWindow.configure(bg='black')
    # window_height = 690
    # window_width = 1200
    # screen_width = newWindow.winfo_screenwidth()
    # screen_height = newWindow.winfo_screenheight()
    # x_cordinate = int((screen_width/2) - (window_width/2))
    # y_cordinate = int((screen_height/2) - (window_height/2))
    # newWindow.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, 0))
    newWindow.state('zoomed')
    graph_data()    

def graph_thread():
    graph_t= threading.Thread(name="Graph Thread",target=createNewWindow)
    graph_t.daemon = True
    graph_t.start()

def graph_data():
    global datenums
    global fig 
    global datas_plot
    global qntd_plot
    global valores_plot

    conection = sqlite3.connect('INV_doG.db')  # criando conexao com o servidor
    c = conection.cursor()  # criando o cursor
    c.execute("SELECT stemp FROM dados")
    datas = c.fetchall()
    c.execute('SELECT valor FROM dados')
    valores_ = c.fetchall()
    c.execute('SELECT quantidade FROM dados')
    quantidade_ = c.fetchall()

    qtd_ = []
    qntd_plot = []
    dat_ = []
    datas_plot = []
    vals_ = []
    valores_plot = []

    for cont, i in enumerate(datas):
        dat_.append(i)
        datas_plot.append(str(dat_[cont][0]).strip(','))
        vals_.append(valores_[cont])
        valores_plot.append(str(vals_[cont][0]).strip(','))
        qtd_.append(quantidade_[cont])
        qntd_plot.append(str(qtd_[cont][0]).strip(','))

    
    for cont, i in enumerate(datas_plot):
        datas_plot[cont]=float(datas_plot[cont])
        #print(type(um_[cont]))
        valores_plot[cont]=float(valores_plot[cont])
        qntd_plot[cont]=int(qntd_plot[cont])

    dates=[datetime.datetime.fromtimestamp(ts) for ts in datas_plot]
    datenums=md.date2num(dates)
        
    fig = Figure(figsize=(13, 6), dpi=100, facecolor="black", edgecolor="blue" )
    ax = fig.add_subplot()
    ax2 = fig.add_subplot()
    fig.autofmt_xdate(rotation=30)
    xfmt = md.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(xfmt)
    formatter = ticker.FormatStrFormatter('R$%1.2f')
    ax.yaxis.set_major_formatter(formatter)
    ax2 = ax.twinx()
    formatter = ticker.FormatStrFormatter('%1.0f')
    ax2.yaxis.set_major_formatter(formatter)
    ax2.plot(datenums,valores_plot, linewidth=0.5)
    ax2.plot(datenums,qntd_plot, linewidth=0.5)

    ax2.spines['bottom'].set_color('gray')
    ax2.spines['top'].set_color('gray') 
    #ax.spines['right'].set_color('red')
    #ax.spines['left'].set_color('red')

    ax.tick_params(axis='x', colors='gray')
    ax.tick_params(axis='y', colors='gray')
    ax2.tick_params(axis='x', colors='gray')
    ax2.tick_params(axis='y', colors='gray')

    ax.patch.set_facecolor('black')
    #ax.set_xlabel('Data')
    #ax.set_ylabel('Valor')
    #ax.title.set_text('Valor x Tempo')
    ax.grid(color='gray', linestyle='-', linewidth=0.2,axis='y')

    t0, = ax.plot(datenums, valores_plot, linewidth=0.5)
    t1, = ax.plot(datenums, qntd_plot, linewidth=0.5)

    fig.legend((t0, t1), ('Inventory Value', 'Item Amount'), 'upper center')
    canvas = FigureCanvasTkAgg(fig, newWindow)
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

    tollbar = NavigationToolbar2Tk(canvas, newWindow)
    tollbar.update()
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

    # newWindow.deiconify()
    newWindow.after(350, newWindow.attributes, "-alpha", 1.0)  # back to normal

########################################################################################

color_border = 'gray10'
color_inside = 'gray6'
color_effect = 'SteelBlue2'

root = Tk()
root.title('CsInvLog')
root.configure(bg=color_border)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_height = 690
window_width = 650

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

root.geometry("+{}+{}".format(x_cordinate, 0))
root.resizable(False, False)

my_top_frame = Frame(root, bg=color_border)
my_top_frame.pack(pady=(10,0), padx=(0))

label_name = Label(my_top_frame, text="User Name" , width=10, font=('bold',11), fg="white", bg=color_border)
label_name.pack(side=LEFT, expand=1, ipady=1)

username = StringVar()
entry_name = Entry(my_top_frame, textvariable=username, borderwidth=4, width=11, justify=CENTER, font=('bold',11), fg="white", bg=color_inside)
entry_name.pack(side=LEFT, expand=1, ipady=1)

label_value = Label(my_top_frame, text="Inventory Value" ,width=12, font=('bold',11), fg="white", bg=color_border)
label_value.pack(side=LEFT, expand=1, ipady=1)

valor_total = StringVar()
entry_value = Entry(my_top_frame, textvariable=valor_total, borderwidth=4, width=10, justify=CENTER, font=('bold',11), fg="white", bg=color_inside)
entry_value.pack(side=LEFT, expand=1, ipady=1)

label_quant = Label(my_top_frame, text="Item Amount" ,width=10, font=('bold',11), fg="white", bg=color_border)
label_quant.pack(side=LEFT, expand=1, ipady=1)

quant_total = StringVar()
entry_quant = Entry(my_top_frame, textvariable=quant_total, borderwidth=4, width=10, justify=CENTER, font=('bold',11), fg="white", bg=color_inside)
entry_quant.pack(side=LEFT, expand=1, ipady=1)

bt_graph = Button(my_top_frame, text="Graph", justify='center', borderwidth=3, bg=color_effect, command=graph_thread, font=('bold',10), fg="black")
bt_graph.pack(side=LEFT, expand=1, ipady=0, padx=(10,10))

my_frame = Frame(root)
my_frame.pack(pady=(5,10), padx=(0))

tree_scroll = Scrollbar(my_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

def disableEvent(event):
    if my_tree.identify_region(event.x, event.y) == "separator":
        return "break"

my_tree = ttk.Treeview(my_frame, height=30, yscrollcommand=tree_scroll.set)
my_tree.pack()

my_tree.bind("<Button-1>", disableEvent)

tree_scroll.config(command=my_tree.yview)

style = ttk.Style()
style.theme_use("default")

style.configure("Treeview.Heading", font=(None, 11), borderwidth=4, background=color_effect, foreground="black", fieldbackground=color_inside)
style.configure("Treeview", font=(None, 11), borderwidth=4, background=color_inside, foreground="white", fieldbackground=color_inside)

style.map("Treeview.Heading", foreground=[('pressed', 'white')], background=[('pressed', color_inside)])
style.map("Treeview", foreground=[('selected', 'black')],  background=[('selected', color_effect)])

entry_name.delete(0,END)
entry_name.insert(0, user_name)

entry_value.delete(0,END)
entry_value.insert(0, total_value_print)

entry_quant.delete(0,END)
entry_quant.insert(0, total_quant)

my_tree["column"] = list(table_final.columns)
my_tree["show"] = "headings"

my_tree.column("ID", minwidth=55, width=55, anchor='center')
my_tree.column("Sticker", minwidth=250, width=250)
my_tree.column("Amount", minwidth=75, width=75, anchor='center')
my_tree.column("Price", minwidth=75, width=75, anchor='center')
my_tree.column("In Total", minwidth=75, width=75, anchor='center')
my_tree.column("Trend(%)", minwidth=75, width=75, anchor='center')

def treeview_sort_column(my_tree, col, reverse):

    l = [(my_tree.set(k, col), k) for k in my_tree.get_children('')]
    try:
        l.sort(key=lambda t: float(t[0]), reverse=reverse)

    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        my_tree.move(k, '', index)

    my_tree.heading(col, command=lambda: treeview_sort_column(my_tree, col, not reverse)) 

    my_tree.yview_moveto(0) #move scrollbar to top

for column in my_tree["column"]:
    my_tree.heading(column, text=column,command=lambda _col=column: treeview_sort_column(my_tree, _col, False))

df_rows = table_final.to_numpy().tolist()

for row in df_rows:
    my_tree.insert("", "end", values=row)

t_end = time.time()

print(f"Execution (seconds): {t_end - t_start:0.2f}")

root.mainloop()