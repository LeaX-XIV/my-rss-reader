import os
import time
import webbrowser

from pathlib import Path
from sched import scheduler
from threading import Thread

from shutil import rmtree

from feeddump import Feed
from liveconsole import LiveConsole
from repeater import Repeater

from constants import CSS_CONTENT
from constants import CSS_PATH
from constants import DEBUG
from constants import XSLT_CONTENT
from constants import XSLT_PATH

class FeedManager:

	comands = {
		"add": lambda self, link, name: self.add(link, name), 
	 	"edit": lambda self, name, newlink: self.edit(name, newlink),
		# "edit": lambda self, name, newname: self.edit(name, newname),
		"del": lambda self, name: self.delete(name),

	 	"list": lambda self: self.listAll(),
		 
	 	"open": lambda self, name: self.openAll() if name is None else self.open(name),

	 	"update": lambda self, name=None: self.update(name),
	}

	def __init__(self):
		self.feeds = {}
		self.dir = os.path.join(os.getenv("LOCALAPPDATA"), "myFeedReader/feeds") if not DEBUG else os.path.join("./feeds")
		self.sched = scheduler(time.time, time.sleep)
		self.repeater = Repeater(self.sched)
		self.lc = LiveConsole()
		self.setup_workspace()
		
		# for feed in self.feeds.values():
			# TODO Change to use self.force_update
			# self.repeater.add((self.force_update), 10*60, 1, True, 1, feed.name)
		self.repeater.add((self.force_update), 10*60, 1, True, 1, None)

		t = Thread(target=(self.repeater.start), daemon=True)
		t.start()


		for k, v in FeedManager.comands.items():
			self.lc.new_command(k, v, self)

		self.lc.start()

	def setup_workspace(self):
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)

		if not os.path.exists(os.path.join(self.dir, XSLT_PATH)):
			with open(os.path.join(self.dir, XSLT_PATH), "w") as f:
				f.write(XSLT_CONTENT)
		if not os.path.exists(os.path.join(self.dir, CSS_PATH)):
			with open(os.path.join(self.dir, CSS_PATH), "w") as f:
				f.write(CSS_CONTENT)

		for dirname in os.listdir(self.dir):
			if os.path.isdir(os.path.join(self.dir, dirname)):
				self.feeds[dirname] = Feed.from_shelve(os.path.join(self.dir, dirname, "data.bin"), self.lc.live_print)



	def add(self, link, name):
		return self.add_new_feed(link, name)

	def edit(self, name, newlink):
		return self.edit_feed_link(name, newlink)

	def delete(self, name):
		self.lc.live_print("Are you sure you want to delete " + name + "? This action cannot be undone (Y/n): ", nl=False)
		r = input("")
		if r == "Y":
			if self.delete_feed(name):
				self.lc.live_print("Feed " + name + " successfully removed.")
				return True
			else:
				self.lc.live_print("Error while deleting feed " + name + ". Aborted.")
				return False
		self.lc.live_print("Action canceled")
		return False

	def listAll(self):
		feeds = self.get_all_feeds()
		for feed, link in feeds.items(): self.lc.live_print(feed + "\t-> " + link)
		if(len(feeds.keys()) == 0): self.lc.live_print("No feeds watched at the moment.")

	def openAll(self):
		# TODO
		pass

	def open(self, name):
		webbrowser.open("http://127.0.0.1:8080/" + name + "/myFeed.xml")

	def updateAll(self):
		return self.force_update(None)

	def update(self, name):
		return self.force_update(name)







	def add_new_feed(self, link, name):
		if link:
			if name:
				new_feed = Feed(link, name, self.dir, self.lc.live_print)
				self.feeds[name] = new_feed
				# TODO Change to use self.force_update
				# self.repeater.add((new_feed.update), 10*60, 1, now=True)
				# self.repeater.add((self.force_update), 10*60, 1, True, 1, new_feed.name)
				self.force_update(new_feed.name)
				return True
		return False

	def edit_feed_link(self, name, newlink):
		if name in self.feeds.keys():
			feed = self.feeds[name]
			feed.link = newlink
			self.force_update(name)
			return True
		return False

	def delete_feed(self, name):
		if name in self.feeds.keys():
			try:
				rmtree(os.path.join(self.dir, name))
			except Exception:
				pass
			del self.feeds[name]
			return True
		return False

	def get_all_feeds(self):
		return dict(zip(map(lambda f: f.name, self.feeds.values()), map(lambda f: f.link, self.feeds.values())))

	def force_update(self, feedname=None):
		to_delete = []
		for k, v in self.feeds.items():
			if feedname is None or k == feedname:
				try:
					v.update()
				except FileNotFoundError:
					self.lc.live_print("Error during update on feed " + k + ". Proceding with deletion.")
					to_delete.append(k)
		
		for error_feed in to_delete:
			self.delete_feed(error_feed)