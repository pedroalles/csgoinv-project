# CSGOInv App Project
Desktop App for viewing and storing Steam Counter-Strike: Global Offensive inventory prices.
  
Inventory items and their prices are obtained through <a href="https://csgobackpack.net/">csgobackpack.net</a>.
  
* Process:
	* The page's html is obtained using the <strong>Requests</strong> module.
	* Then a dataframe of the items and prices table is generated using the <strong>Pandas</strong> module.
	* The total inventory value and date are stored in a database using the <strong>Sqlite3</strong> module.
	* Finally, the data is displayed in a GUI using the <strong>Tkinter</strong> module.
	
<kbd><img src="img/csgoinv.png"></kbd>
