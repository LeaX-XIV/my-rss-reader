import sys
import webbrowser


class LiveConsole:

	def __init__(self):
		self.prompt = ">"
		self.commands = {}
		self.commands["exit"] = {"action": lambda self: sys.exit(0), "this": self}

	def start(self):
		while True:
			try:
				line = input("\r" + self.prompt + " ")
			except KeyboardInterrupt:
				line = "exit"
			try:
				com, *args = line.split(maxsplit=3)
			except ValueError:
				continue
			try:
				row = self.commands[com]
				(row["action"])(row["this"], *args)
			except KeyError:
				self.live_print("Error")

	def new_command(self, mnemonic, action, this):
		if mnemonic not in self.commands.keys():
			self.commands[mnemonic] = {"action": action, "this": this}
			return True
		else:
			return False

	def live_print(self, line, nl=True):
		print(f"\r{str(line)}", end="")
		if nl:
			print("")
			print(f"{self.prompt} ", end="", flush=True)
