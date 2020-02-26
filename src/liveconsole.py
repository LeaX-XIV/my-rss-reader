import sys
import webbrowser

from feedmanager import FeedManager

class LiveConsole:
	comands = {
		"add": lambda self, link, name: self.add(link, name), 
	 	"edit": lambda self, name, newlink: self.edit(name, newlink),
		# "del": lambda self, name: self.delete(name),

	 	"list": lambda self: self.listAll(),
		 
	 	"open": lambda self, name: self.openAll() if name is None else self.open(name),

	 	"update": lambda self, name=None: self.update(name),
		
		"exit": lambda self: sys.exit(0),
	}

	def __init__(self):
		self.feed_mngr = FeedManager()

	def start(self):
		while True:
			try:
				line = input("")
			except KeyboardInterrupt:
				line = "exit"
			try:
				com, *args = line.split(maxsplit=3)
			except ValueError:
				continue
			try:
				(LiveConsole.comands[com])(self, *args)
			except KeyError:
				print("Error")

	def add(self, link, name):
		return self.feed_mngr.add_new_feed(link, name)

	def edit(self, name, newlink):
		return self.feed_mngr.edit_feed_link(name, newlink)

	def delete(self, name):
		print("Are you sure you want to delete " + name + "? This action cannot be undone (Y/n): ", nl = False)
		r = input("")
		if r == "Y":
			return self.feed_mngr.delete_feed(name)
		return False

	def listAll(self):
		feeds = self.feed_mngr.get_all_feeds()
		for feed, link in feeds.items(): print(feed + "\t-> " + link)
		if(len(feeds.keys()) == 0): print("No feeds watched at the moment.")		
		

	def openAll(self):
		# TODO
		pass

	def open(self, name):
		webbrowser.open("http://127.0.0.1:8080/" + name + "/myFeed.xml")

	def updateAll(self):
		return self.feed_mngr.force_update(None)

	def update(self, name):
		return self.feed_mngr.force_update(name)


def live_print(line, nl=True):
	print("\r" + str(line), end="")
	if(nl):
		print("")
		print("> ", end="")