import os
import requests

from difflib import Differ
from datetime import datetime
import xml.etree.ElementTree as ET
import shelve

from constants import XSLT_PATH_FROM_XML


class Feed:
	"""The Feed class manages one instance of an RSS feed.
	
	"""
	default_settings = {
		"last_modified": "Thu, 1 Jan 1970 00:00:00 GMT", 
		 "etag": None
	}

	def __init__(self, feed_link, name, curr_dir, print_fnc, last_modified=None, etag=None):
		"""Constructor method. Creates directory in curr_dir/name

		:param feed_link: URL of the feed
		:param name: name of directory and title for notification
		:param curr_dir: parent directory for saving directory
		:param last_modified: data for HTTP header If-Modified-Since
		:param etag: data for HTTP header If-None-Match
		"""
		self.link = feed_link
		self.name = name
		self.dir = os.path.abspath(os.path.join(curr_dir, name))
		self.favicon_path = os.path.join(self.dir, "favicon.ico")
		self.data_path = os.path.join(self.dir, "data.bin")
		self.feed_path = os.path.join(self.dir, "rss.xml")
		self.feed_mod_path = os.path.join(self.dir, "myFeed.xml")
		self.print = print_fnc
		self.last_modified = last_modified or Feed.default_settings["last_modified"]
		self.etag = etag or Feed.default_settings["etag"]
		self.init()

	def init(self):
		if not os.path.exists(self.dir):
			os.makedirs(self.dir)
		else:
			if not os.path.exists(self.feed_path):
				f = open((self.feed_path), "w", encoding="utf-8")
				f.close()
				self.feed_content = ""
				self.feed_etree = None
			else:
				f = open((self.feed_path), "r", encoding="utf-8")
				self.feed_content = f.read()
				f.close()
				self.feed_etree = ET.fromstring(self.feed_content).find("channel")
		if not os.path.exists(self.feed_mod_path):
			f = open((self.feed_mod_path), "w", encoding="utf-8")
			f.close()
		return
	
	@classmethod
	def from_shelve(cls, shelve_path, print_fnc):
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
				print_fnc = print_fnc,
				last_modified = sf["last_modified"],
				etag = sf["etag"],
			)

	def get(self):
		"""Sends a synchronous HTTP GET request to URL of feed.
		
		:return: Response

		"""
		headers = {
			"User-Agent": "Mozilla/5.0 (Linux; Android 8.0.0; Pixel XL Build/OPR6.170623.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.107 Mobile Safari/537.36", 
			 "If-Modified-Since": self.last_modified}
		if self.etag is not None:
			headers["If-None-Match"] = self.etag
		return requests.get((self.link), headers=headers)


	def update_HTTP_variables(self, response):
		"""Updates HTTP header variables for next request, only if needed

		TODO Refactor

		:param response: Response object returned by GET request
		:return: True if action taken, False otherwise
		"""
		if response.status_code != 304:
			if "Last-Modified" in response.headers.keys():
				self.last_modified = response.headers["Last-Modified"]
			else:
				if "Date" in response.headers.keys():
					self.last_modified = response.headers["Date"]
				else:
					self.last_modified = Feed._datetime_gmt(datetime.now(datetime.timezone.utc))
			if "ETag" in response.headers.keys():
				self.etag = response.headers["ETag"]
		return response.status_code != 304


	def is_new_different(self, new_file):
		"""Determines if the new file retrieved from the network is different from the previous one

		:param new_file: str content of the new file
		:return: True if files are different, False otherwhise
		"""
		if not os.path.exists(self.feed_path):
			return True
		d = Differ()
		cmp_result = list(d.compare(self.feed_content.splitlines(keepends=True), new_file.splitlines(keepends=True)))
		return all((not line.startswith(" ") for line in cmp_result))

	def modify_content(self):
		"""


		:return: Number of new items
		"""

		def ET_eq(item1, item2):
			if item1.tag != item2.tag: return False
			if item1.text != item2.text: return False
			if item1.tail != item2.tail: return False
		#   if item1.attrib != item2.attrib: return False
			if len(item1) != len(item2): return False
			return all(ET_eq(c1, c2) for c1, c2 in zip(item1, item2))




		try:
			feed = ET.fromstring(self.feed_content)
			new_items = feed.find("channel").findall("item")
			old_items = ET.ElementTree(file=self.feed_mod_path).find("channel").findall("item")

			i = 0
			while(not ET_eq(new_items[i], old_items[0])):
				new_items[i].attrib["new"] = "new"
				i += 1

			new = i
			for j in range(len(new_items) - i):
				if("new" in old_items[j].attrib.keys()):
					new_items[i].attrib["new"] = "new"
				i += 1

		except (ET.ParseError, IndexError):
			for item in new_items:
				item.attrib["new"] = "new"
			return len(new_items)
		finally:
			final_text = ET.tostring(feed, encoding="utf-8")
			with open(self.feed_mod_path, "w", encoding="utf-8") as feed_mod:
				feed_mod.write(f"<?xml-stylesheet type=\"text/xsl\" href=\"{XSLT_PATH_FROM_XML}\"?>\n")
				feed_mod.write(final_text.decode("utf-8"))
		
		return new




	def update(self):

		# Make GET request and store Response
		try:
			response = self.get()
			self.print(f"{str(datetime.now())[:19]} {self.name} {str(response.status_code)}")
			response.raise_for_status()
		except:
			# self.print(traceback.format_exc())
			return

		updated = self.update_HTTP_variables(response)
		if updated:
			
			different = self.is_new_different(response.text)
			if different:
				try:
					#save new content
					self.feed_content = response.text
					with open(self.feed_path, "w", encoding="utf-8") as feed:
						feed.write(self.feed_content)
					self.feed_etree = ET.fromstring(self.feed_content).find("channel")

					n = self.modify_content()
					self.print(f"{str(n)} new items in {self.name}.")


					# generaten n notifications
					# send notifications in new thread

					self.save_shelve()
				except FileNotFoundError as e:
					raise e





	def save_shelve(self):
		"""Saves self with shelve library

		"""
		with shelve.open(self.data_path) as sf:
			sf["feed_link"] = self.link
			sf["last_modified"] = self.last_modified
			sf["etag"] = self.etag


	@staticmethod
	def _datetime_gmt(dt):
		return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
