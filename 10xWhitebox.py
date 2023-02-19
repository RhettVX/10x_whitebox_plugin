# Python API: AddPostFileSaveFunction               Add a function to be called after a file has been saved : AddPostFileSaveFunction(function) : function(filename)
# Python API: AddUpdateFunction                     Add a function that will be called every frame : AddUpdateFunction(function)
# Python API: GetCurrentFilename                    Get the filename of the currently focused file. Empty string if no file focused
# Python API: GetFileText                           Get the entire text for the currently focused file : string GetFileText()
# Python API: GetLine                               Get the line text for the currently focused file : text GetLine(line_index)
# Python API: IsModified                            Return true if the current file has been modified : bool IsModified()
# Python API: RemoveUpdateFunction                  Remove an update function : RemoveUpdateFunction(function)


import N10X
import socket
import json
from pprint import pprint


class WhiteBox10x:
	is_enabled = False
	host = 'localhost'
	port = 19013 
	prev_line = -1
	prev_column = -1

	# NOTE(rhett): stripped from whitebox sublime text plugin
	@classmethod
	def connect(self):
		if(self.is_enabled):
			if not hasattr(self, 'wbsocket'):
				self.wbsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				conerr = self.wbsocket.connect_ex((self.host, self.port))
				if conerr != 0:
					print("WhiteBox Plugin socket error: ", conerr)
					delattr(self, 'wbsocket')
				else:
					print('WhiteBox connected')
		else:
			if hasattr(self, 'wbsocket'):
				delattr(self, 'wbsocket')

	@classmethod
	def disable(self):
		self.is_enabled = False
		if hasattr(self, 'wbsocket'):
				delattr(self, 'wbsocket')

	@classmethod
	def enable(self):
		self.is_enabled = True
		# TODO(rhett): maybe connect as well
		self.connect()

	@classmethod
	def send_state(self):
		current_column, current_line = N10X.Editor.GetCursorPos()

		if N10X.Editor.IsModified():
			dirty = ['unsaved']
		else:
			dirty = []

		payload = {
			'editor': '10x Editor',
			'path': N10X.Editor.GetCurrentFilename(),
			"selection": [{'line': (current_line + 1), 'column': current_column}],
			'dirty': dirty,
		}
		# pprint(payload)
		try:
			self.wbsocket.send(json.dumps(payload).encode("utf8"))
		except Exception as e:
			print("WhiteBox Plugin Send error: ", e)

	@classmethod
	def run_tick(self):
		if N10X.Editor.TextEditorHasFocus() and self.is_enabled and hasattr(self, 'wbsocket'):
			current_column, current_line = N10X.Editor.GetCursorPos()

			if self.prev_line != current_line or self.prev_column != current_column:
				self.prev_line = current_line
				self.prev_column = current_column
				self.send_state()

	@classmethod
	def on_save(self, filename):
		if self.is_enabled and hasattr(self, 'wbsocket'):
			self.send_state()

				
N10X.Editor.AddPostFileSaveFunction(WhiteBox10x.on_save)

def WhiteBoxEnable():
	WhiteBox10x.enable()
	N10X.Editor.AddUpdateFunction(WhiteBox10x.run_tick)

def WhiteBoxDisable():
	WhiteBox10x.disable()
	N10X.Editor.RemoveUpdateFunction(WhiteBox10x.run_tick)

def WhiteBoxConnect():
	WhiteBox10x.connect()
	

