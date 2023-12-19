using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using System.Net;
using System.Net.Sockets;

namespace SharpClient
{
	public enum MessageTypes : int
	{
		MT_INIT,
		MT_EXIT,
		MT_GETDATA,
		MT_DATA,
		MT_NODATA,
		MT_CONFIRM,
		MT_CHECKUSERS
	};

	public enum MessageRecipients : int
	{
		MR_BROKER = 10,
		MR_ALL = 50,
		MR_USER = 100
	};


	[StructLayout(LayoutKind.Sequential)]
	struct MessageHeader
	{
		[MarshalAs(UnmanagedType.I4)]
		public MessageRecipients to;
		[MarshalAs(UnmanagedType.I4)]
		public MessageRecipients from;
		[MarshalAs(UnmanagedType.I4)]
		public MessageTypes type;
		[MarshalAs(UnmanagedType.I4)]
		public int size;
	};

	class Message
	{
		public MessageHeader header;
		public string data;

		public Message(MessageRecipients to, MessageRecipients from, MessageTypes type = MessageTypes.MT_DATA, string data = "")
		{
			this.data = data;
			header = new MessageHeader() { to = to, from = from, type = type, size = data.Length };
		}
	}
}
