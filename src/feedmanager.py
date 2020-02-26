import os
import time

from pathlib import Path
from sched import scheduler
from threading import Thread

from feeddump import Feed
from repeater import Repeater

from variables import CSS_PATH
from variables import XSLT_PATH

class FeedManager:

	def __init__(self):
		self.feeds = {}
		self.dir = os.path.join(os.getenv("LOCALAPPDATA"), "myFeedReader/feeds")
		self.sched = scheduler(time.time, time.sleep)
		self.repeater = Repeater(self.sched)
		self.setup_workspace()
		
		for feed in self.feeds.values():
			self.repeater.add((feed.update), 10*60, 1, now=True)

		t = Thread(target=(self.repeater.start), daemon=True)
		t.start()

	def setup_workspace(self):
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)

		if not os.path.exists(os.path.join(self.dir, XSLT_PATH)):
			# TODO Copy file to self.dir
			pass
		if not os.path.exists(os.path.join(self.dir, CSS_PATH)):
			# TODO Copy file to self.dir
			pass

		for dirname in os.listdir(self.dir):
			if os.path.isdir(os.path.join(self.dir, dirname)):
				self.feeds[dirname] = Feed.from_shelve(os.path.join(self.dir, dirname, "data.bin"))


	def add_new_feed(self, link, name):
		if link:
			if name:
				new_feed = Feed(link, name, self.dir)
				self.feeds[name] = new_feed
				self.repeater.add((new_feed.update), 10*60, 1, now=True)
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
			del self.feeds[name]
			return True
		return False

	def get_all_feeds(self):
		return dict(zip(self.feeds.keys(), map(lambda f: f.link, self.feeds.values())))

	def force_update(self, feedname=None):
		for k, v in self.feeds.items():
			if feedname is None or k == feedname:
				v.update()