import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter import ttk

import sqlite3
import time
import datetime

########################################################################################

URL = 'https://csgobackpack.net/?nick=pedroalles&currency=BRL'

page = requests.get(URL, headers={})
table = pd.read_html(page.text)
table_df = pd.DataFrame(table[0])
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

color_border = 'gray10'
color_inside = 'gray6'
color_effect = 'SteelBlue2'

root = Tk()
root.title('CsInvLog')
root.configure(bg=color_border)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_height = 700
window_width = 650

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

root.geometry("+{}+{}".format(x_cordinate, 0))
root.resizable(False, False)

my_top_frame = Frame(root, bg=color_border)
my_top_frame.pack(pady=(5,0), padx=(5), fill=X)

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

my_frame = Frame(root)
my_frame.pack(pady=(5,5), padx=(5))

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


root.mainloop()