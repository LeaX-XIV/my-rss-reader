import os, requests, traceback
from difflib import Differ
from datetime import datetime
import xml.etree.ElementTree as ET
from pprint import pprint
from plyer import notification
import webbrowser
from win10toast import ToastNotifier
import shelve

class Feed:
	"""The Feed class manages one instance of an RSS feed.

	TODO Refarcor

	"""



	default_settings = {
		"last_modified": "Thu, 1 Jan 1970 00:00:00 GMT",
		"etag": None,
		"feed_length": 0,
		"feed_new": 0
	}

	def __init__(self, feed_link, name, curr_dir, **kwargs):
		"""Constructor method. Creates directory in curr_dir/name

		:param feed_link: URL of the feed
		:param name: name of directory and title for notification
		:param curr_dir: parent directory for saving directory
		:param last_modified: data for HTTP header If-Modified-Since
		:param etag: data for HTTP header If-None-Match
		:param feed_length: number of items in the feed
		:param feed_new: bitmask of feed_length bits: 1 not seen 0 seen
		"""
		self.feed_link = feed_link
		self.name = name
		self.curr_dir = os.path.abspath(os.path.join(curr_dir, name))
		# If no additional arguments are passed, use default settings
		if len(kwargs) == 0:
			kwargs = Feed.default_settings
		self.last_modified = kwargs["last_modified"]
		self.etag = kwargs["etag"]
		self.feed_length = kwargs["feed_length"]
		self.feed_new = kwargs["feed_new"]

		# If directory doen't exist, create it
		if not os.path.exists(self.curr_dir):
			os.makedirs(self.curr_dir)
		# Paths for files in directory
		self.favicon_path = os.path.join(self.curr_dir, "favicon.ico")
		self.feed_path = os.path.join(self.curr_dir, "rss.xml")
		self.data_path = os.path.join(self.curr_dir, "data.bin")


	@classmethod
	def from_shelve(cls, shelve_path):
		"""Loads a Feed object previously saved with shelve library

		:param shelve_path: path and name of shelve files w/o extension
		:return: Feed
		"""
		with shelve.open(shelve_path) as sf:
			return cls(
				feed_link = sf["feed_link"],
				# Use shelve_path to get saving path
				name = os.path.basename(os.path.dirname(shelve_path)),
				curr_dir = os.path.dirname(os.path.dirname(shelve_path)),
				last_modified = sf["last_modified"],
				etag = sf["etag"],
				feed_length = sf["feed_length"],
				feed_new = sf["feed_new"]
			)

	def update(self):
		"""Makes HTTP GET request to retrieve RSS feed.
		If there are news, updates what needs to be updated and sends notifications.

		"""

		def get():
			headers = {
				"User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; Pixel XL Build/OPR6.170623.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.107 Mobile Safari/537.36",
				"If-Modified-Since": self.last_modified
			}
			if self.etag is not None:
				headers["If-None-Match"] = self.etag

			return requests.get(self.feed_link, headers = headers)

		def need_rewrite(new_text):
			if not os.path.exists(self.feed_path):
				return (True, "")

			with open(self.feed_path, encoding="utf-8") as old_file:
				old_text = old_file.read()

			d = Differ()
			cmp_result = list(d.compare(old_text.splitlines(keepends=True), new_text.splitlines(keepends=True)))

			for line in cmp_result:
				if not line.startswith(" "):
					return (True, old_text)

			return (False, old_text)

		def update_bitmask(before, after, bitmask):
			def ET_eq(item1, item2):
				if item1.tag != item2.tag: return False
				if item1.text != item2.text: return False
				if item1.tail != item2.tail: return False
				if item1.attrib != item2.attrib: return False
				if len(item1) != len(item2): return False
				return all(ET_eq(c1, c2) for c1, c2 in zip(item1, item2))

			feed_new = bitmask
			if before == "":
				itemsA = ET.fromstring(after).find("channel").findall("item")
				for i in range(len(itemsA)):
					feed_new += 1<<i
				
				print(bin(feed_new)[2:], len(bin(feed_new)[2:]))
				return (feed_new, [], [])

			itemsB = ET.fromstring(before).find("channel").findall("item")
			itemsA = ET.fromstring(after).find("channel").findall("item")

			b, a= (0, 0)
			feed_old = bitmask
			feed_new = 0
			
			while a < len(itemsA) and not ET_eq(itemsB[b], itemsA[a]):
				feed_new += 1 << a
				a += 1

			notif_messages = []
			notif_links = []
			for index in range(len(bin(feed_new)[2:])):
				if(bin(feed_new)[index+2]) == "1":
					notif_messages.append(itemsA[index].find("title").text)
					notif_links.append(itemsA[index].find("link").text)

			feed_old = feed_old << a
			feed_new |= feed_old

			limit = 1 << len(itemsA) + 1
			limit -= 1
			feed_new &= limit

			print(bin(feed_new)[2:], len(bin(feed_new)[2:]))
			return (feed_new, notif_messages, notif_links)

		def store_new_feed(path, iterable):
			with open(path, "bw") as file:
				if iterable is not None:
					for chunk in iterable.iter_content(10000):
						file.write(chunk)

		def send_notifications(title, messages, icon_path, links):
			toast = ToastNotifier()
			# Add callbacks
			for i in range(len(messages)):
				print(str(datetime.now())[:19] + " " + "Sending notification - " + title + ": " + messages[i])
				if os.path.exists(icon_path):
					toast.show_toast(title, messages[i], icon_path, 10, callback_on_click=lambda: webbrowser.open(links[i]))
				else:
					toast.show_toast(title, messages[i], duration=10, callback_on_click=lambda: webbrowser.open(links[i]))

		try:
			response = get()
			print(str(datetime.now())[:19] + " " + self.name + " " + str(response.status_code), flush=True)
			response.raise_for_status()
		except:
			# print(traceback.format_exc())
			return


		# 304 Not Modified. No further actions required
		if response.status_code != 304:
			# Update variables for next request
			if "Last-Modified" in response.headers.keys():
				self.last_modified = response.headers["Last-Modified"]
			elif "Date" in response.headers.keys():
				self.last_modified = response.headers["Date"]
			else:
				self.last_modified = Feed._datetime_gmt(datetime.now(datetime.timezone.utc))
			if "ETag" in response.headers.keys():
				self.etag = response.headers["ETag"]
			
			need, old_text = need_rewrite(response.text)
			if need:
				new_bitmask, notification_messages, notification_links = update_bitmask(old_text, response.text, self.feed_new)
				self.feed_new = new_bitmask

				store_new_feed(self.feed_path, response)
				
				self.save_shelve()

				notification_messages.reverse()
				notification_links.reverse()
				send_notifications(self.name, notification_messages, self.favicon_path, notification_links)


	def save_shelve(self):
		"""Saves self with shelve library

		"""
		with shelve.open(self.data_path) as sf:
			sf["feed_link"] = self.feed_link
			sf["last_modified"] = self.last_modified
			sf["etag"] = self.etag
			sf["feed_length"] = self.feed_length
			sf["feed_new"] = self.feed_new

	@staticmethod
	def _datetime_gmt(dt):
		return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
