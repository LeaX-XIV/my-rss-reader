#! python3
# A simple command-line RSS feed reader

import sys, copy, time, os
from threading import Thread
from repeater import Repeater
from sched import scheduler
from feeddump import Feed

storing_dir = os.path.join(".", "feeds")

s = scheduler(time.time, time.sleep)
r = Repeater(s)
dumps = []

t = Thread(target=r.start)
t.daemon = True
t.start()

if not os.path.exists(storing_dir):
	os.makedirs(storing_dir)
elif not os.path.isdir(storing_dir):
	# raise Error("Cannot execute reader.")
	print("Error.")


for dirname in os.listdir(storing_dir):
	if os.path.isdir(os.path.join(storing_dir, dirname)):
		dumps.append(Feed.from_shelve(os.path.join(storing_dir, dirname, 'data.bin')))


# for k, v in feeds.items():
# 	dumps.append(Feed(v, k, storing_dir))

for d in dumps:
	r.add(d.update, 10*60, 1, now=True)

while(1):
	exec(input())