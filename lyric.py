# ---------- import statements -------------- #

import requests 
import curses
from bs4 import BeautifulSoup
import mariadb as sql 
import pickle
import os
import time
# --------------------------------------------- #


# ------------------ curses module helper functions ----------------- #

# prints a curses menu in the centre of the screen with contrasting colors for easy navigation
def print_menu(stdscr, selected_row_idx, mlist, text=""):
	stdscr.clear()
	h, w = stdscr.getmaxyx()
	tx = w//2 - len(text)//2 
	ty = h//2 - len(menu)//2 - 2 
	stdscr.addstr(ty, tx, text)
	for idx, row in enumerate(mlist):
		x = w//2 - len(row)//2
		y = h//2 - len(menu)//2 + idx
		if idx == selected_row_idx:
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(y, x, row)
			stdscr.attroff(curses.color_pair(1))
		else:
			stdscr.addstr(y, x, row)
	stdscr.refresh()

# gets the centre coordinates of the screen
def center(stdscr):
	h, w = stdscr.getmaxyx()
	x = w//2
	y = h//2
	return x, y

# outputs text at the centre of the screen
def print_center(stdscr, text):
	stdscr.clear()
	h, w = stdscr.getmaxyx()
	x = w//2 - len(text)//2
	y = h//2
	stdscr.addstr(y, x, text)
	stdscr.refresh()

# receives input from the user with text echoing
def my_raw_input(stdscr, prompt_string):
	curses.echo()
	x, y = center(stdscr)
	x -= len(prompt_string)//2
	stdscr.addstr(y, x, prompt_string)
	stdscr.refresh()
	input = stdscr.getstr(y + 1, x, 40)
	return input

# receives input from the user with text echoing off (for passwords and sensitive information)
def passwordinput(stdscr, prompt_string):
	curses.noecho()
	x, y = center(stdscr)
	x -= len(prompt_string)//2
	stdscr.addstr(y, x, prompt_string)
	stdscr.refresh()
	input = stdscr.getstr(y + 1, x, 20)
	return input

# a login screen to sign in to mySQL
def login(stdscr):
	stdscr.clear()
	# turn off cursor blinking
	curses.curs_set(0)

	# color scheme for selected row
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

	# specify the current selected row
	current_row = 0
	usern = my_raw_input(stdscr, "Enter your SQL username (e.g: root)")
	usern = str(usern)
	usern = usern[2:len(usern)-1]
	stdscr.clear()
	pwd = passwordinput(stdscr, f'Enter password for {usern}')
	pwd = str(pwd)
	pwd = pwd[2:len(pwd)-1]
	stdscr.refresh()

	return usern,pwd

# show error when user credentials are incorrect
def incorrect(stdscr):
	print_center(stdscr, "Your username/password is incorrect")
	time.sleep(2)
	return

# Define the structure of the main menu
menu = ["Search for Lyrics", "View Offline Lyrics","Clear Lyric Database", "Exit"]
# ---------------------------------------------------------------- #


# --------------- receiving and manipulating user's MySQL credentials ------------------- #

if not os.path.isfile("pwds.dat"):
	f = open("pwds.dat", "wb")
	usern, pwd = curses.wrapper(login)
	usertup = (usern,pwd)
	pickle.dump(usertup, f)
	f.close()

f = open('pwds.dat', 'rb')
userdata = pickle.load(f)
usern = userdata[0]
pwd = userdata[1]
f.close()

try:
	con=sql.connect(host='localhost',user=f'{usern}',passwd=f'{pwd}')
except:
	curses.wrapper(incorrect)
	os.remove("pwds.dat")
	quit()
# ---------------------------------------------------------------- #


# --------------- check if necessary database and table exists, if not create it ------------------- #

cur=con.cursor()
cur.execute("show databases")
j = cur.fetchall()

if ('lyrics',) in j:
    cur.execute("use lyrics;")
    cur.execute("show tables;")
    out = cur.fetchall()
    if ('lyric',) not in out:
        cur.execute("create table lyric(aristname varchar(20), songname varchar(30) primary key, lyricss varchar(10000));")
else:
    cur.execute("create database lyrics;")
    cur.execute("use lyrics;")
    cur.execute("create table lyric(aristname varchar(20), songname varchar(30) primary key, lyricss varchar(10000));")

con.commit()
# ---------------------------------------------------------------- #


# -------------------------- function to fetch/load lyrics --------------------------- #

def lyricsfunction(artist, song):
	artist = str(artist.lower())
	artist = artist.replace("b'", "")
	artist = artist.replace("'", "")

	song = str(song.lower())
	song = song.replace("b'", "")
	song = song.replace("'", "")

	art, son = artist, song

	if " " in art:
		art = art.replace(" ","")

	if " " in son:
		son = son.replace(" ","")

	url = f'https://www.azlyrics.com/lyrics/{art}/{son}.html'

	cur.execute("select songname from lyric;")
	myr = cur.fetchall()
	nlist = []

	for i in myr:
		nlist += i


	if song not in nlist:
		try:
			# accessing data from the url using the "get" method
			req = requests.get(url)

			# parsing the html data using python's default html parser through beautifulsoup4
			html = BeautifulSoup(req.text , 'html.parser')

			# ".find" finds the first occurence of the <div> tag with the specified class.
			# ".find_all" finds all occurences of the <div> tag under the <div> tag found initially.
			# ".text" returns the text without any seperators.
			lyrics = html.find('div' , class_ = 'col-xs-12 col-lg-8 text-center').find_all('div')[5].text
			lyrics = lyrics.replace('"', "'")


			print('\n'*100)
			print(f"{artist} - {song}\n{lyrics}")
			print("\n\n[Press Enter to Continue]")

			cur.execute(f'''insert into lyric values("{artist}", "{song}", "{lyrics}");''')
			con.commit()

		except requests.ConnectionError:
			print("Please connect to the internet and try again.")

		except AttributeError:
			print(art,son)
			print("Couldn't find the requested song. Please try again.")

	else:
		cur.execute(f"select lyricss from lyric where songname = '{song}';")
		lyrics = cur.fetchall()
		lyrics = lyrics[0][0]
		print('\n'*100)
		print(f"{artist} - {song}\n{lyrics}")
		print("\n\n[From Local Database]\n")
		print("\n\n[Press Enter to Continue]")
# ------------------------------------------------------------------- #


# --------------------- main function (implement curses) ----------------------- #
def main(stdscr):
	# turn off cursor blinking
	curses.curs_set(0)

	# color scheme for selected row
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)


	# specify the current selected row
	current_row = 0

	# print the menu
	print_menu(stdscr, current_row, menu, "LYRIC FETCHER")

	while 1:
		key = stdscr.getch()

		# Traversing curses menu
		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
		elif key == curses.KEY_DOWN and current_row < len(menu)-1:
			current_row += 1

		elif key == curses.KEY_ENTER or key in [10, 13]:
			
			#song search function	
			if current_row == 0:
				stdscr.clear()
				artist = my_raw_input(stdscr,"Enter Artist Name:")
				stdscr.clear()
				song= my_raw_input(stdscr,"Enter Song Name:")
				stdscr.clear()
				curses.endwin()
				lyricsfunction(artist, song)

				
				while True:
					x = input()
					if x == "":
						break

			elif current_row == 1:
				current = 0
				tableau = []
				cur.execute('select aristname, songname from lyric;')
				off = cur.fetchall()
				for i in range(len(off)):
					x = str(f'{i+1}. {off[i][0]} - {off[i][1]}')
					tableau.append(x)
				tableau.append("back")	
				while True:
					print_menu(stdscr, current, tableau, "OFFLINE LYRICS")
					keypress = stdscr.getch()
					if keypress == curses.KEY_UP and current > 0:
						current-= 1
					elif keypress == curses.KEY_DOWN and current < len(tableau)-1:
						current+= 1
					elif keypress == curses.KEY_ENTER or keypress in [10, 13]:
						if current != len(tableau)-1:
							curses.endwin()
							lyricsfunction(off[current][0], off[current][1])
							while True:
								x = input()
								if x == "":
									break

						else:
							break
							
			elif current_row == 2:
				current = 0
				confirm= ["NO","YES"]
				while True:
					print_menu(stdscr, current, confirm, "Are you sure you want to clear ALL lyrics from the database?")
					keypress = stdscr.getch()
					if keypress == curses.KEY_UP and current > 0:
						current-= 1
					elif keypress == curses.KEY_DOWN and current < len(confirm)-1:
						current+= 1
					elif keypress == curses.KEY_ENTER or keypress in [10, 13]:
						if current == 1:
							cur.execute('truncate table lyric;')
							con.commit()
							print_center(stdscr, "The Database has been Erased")
							time.sleep(3)
							break
						else:
							break
				

			# Exitting the curses menu
			elif current_row == len(menu)-1:
				current = 0
				confirm= ["YES", "NO"]
				while True:
					print_menu(stdscr, current, confirm, "Are you sure you want to exit?")
					keypress = stdscr.getch()
					if keypress == curses.KEY_UP and current > 0:
						current-= 1
					elif keypress == curses.KEY_DOWN and current < len(confirm)-1:
						current+= 1
					elif keypress == curses.KEY_ENTER or keypress in [10, 13]:
						if current == 0:
							return 0	
						else:
							break


		print_menu(stdscr, current_row, menu, "LYRIC FETCHER")
# ------------------------------------------------------------------- #

# call the curses wrapper to display the curses TUI
curses.wrapper(main)
