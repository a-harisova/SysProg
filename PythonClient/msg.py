import threading
from dataclasses import dataclass
import socket, struct, time

MT_INIT		= 0
MT_EXIT		= 1
MT_GETDATA	= 2
MT_DATA		= 3
MT_NODATA	= 4
MT_CONFIRM	= 5
MT_CHECKUSERS = 6

MR_BROKER	= 10
MR_ALL		= 50
MR_USER		= 100


@dataclass
class MsgHeader:
	To: int = 0
	From: int = 0
	Type: int = 0
	Size: int = 0

	def Send(self, s):
		s.send(struct.pack(f'iiii', self.To, self.From, self.Type, self.Size))

	def Receive(self, s):
		try:
			(self.To, self.From, self.Type, self.Size) = struct.unpack('iiii', s.recv(16))
		except:
			self.Size = 0
			self.Type = MT_NODATA

class Message:
	def __init__(self, To = 0, From = 0, Type = MT_DATA, Data=""):
		self.Header = MsgHeader(To, From, Type, len(Data))
		self.Data = Data

