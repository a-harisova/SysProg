using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using System.Net;
using System.Net.Sockets;

namespace SharpClient
{
    class Client
    {
		int id = 0;
		static Encoding? cp866 = null;
		static Encoding get866()
		{
			if (cp866 is null)
			{
				Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
				cp866 = Encoding.GetEncoding("CP866");
			}
			return cp866;
		}
		static byte[] toBytes(object obj)
		{
			int size = Marshal.SizeOf(obj);
			byte[] buff = new byte[size];
			IntPtr ptr = Marshal.AllocHGlobal(size);
			Marshal.StructureToPtr(obj, ptr, true);
			Marshal.Copy(ptr, buff, 0, size);
			Marshal.FreeHGlobal(ptr);
			return buff;
		}
		static T fromBytes<T>(byte[] buff) where T : struct
		{
			T data = default(T);
			int size = Marshal.SizeOf(data);
			IntPtr i = Marshal.AllocHGlobal(size);
			Marshal.Copy(buff, 0, i, size);
			var d = Marshal.PtrToStructure(i, data.GetType());
			if (d is not null)
			{
				data = (T)d;
			}
			Marshal.FreeHGlobal(i);
			return data;
		}
		void send(Socket s, Message m)
		{
			s.Send(toBytes(m.header), Marshal.SizeOf(m.header), SocketFlags.None);
			if (m.header.size != 0)
			{
				s.Send(get866().GetBytes(m.data), m.header.size, SocketFlags.None);
			}
		}
		void send(MessageRecipients to, MessageTypes type = MessageTypes.MT_DATA, string data = "")
        {
			int nPort = 12345;
			IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), nPort);
			Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
			s.Connect(endPoint);
			if (!s.Connected)
			{
				throw new Exception("Connection error");
			}
			Message m = new Message(to, (MessageRecipients)id, type, data);
			send(s, m);
		}
		static MessageTypes receive(Socket s, Message m)
		{
			byte[] buff = new byte[Marshal.SizeOf(m.header)];
			if (s.Receive(buff, Marshal.SizeOf(m.header), SocketFlags.None) == 0)
			{
				return MessageTypes.MT_NODATA;
			}
			m.header = fromBytes<MessageHeader>(buff);
			if (m.header.size > 0)
			{
				byte[] b = new byte[m.header.size];
				s.Receive(b, m.header.size, SocketFlags.None);
				m.data = get866().GetString(b, 0, m.header.size);

			}
			return m.header.type;
		}
		public Message call(MessageRecipients to, MessageTypes type = MessageTypes.MT_DATA, string data = "")
		{
			int nPort = 12345;
			IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), nPort);
			Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
			s.Connect(endPoint);
			if (!s.Connected)
			{
				throw new Exception("Connection error");
			}
			Message m = new Message(to, (MessageRecipients)id, type, data);
			send(s, m);
			if (receive(s, m) == MessageTypes.MT_INIT)
			{
				id = (int)m.header.to;
			}
			return m;
		}
		void ProcessMessages()
		{
			while (true)
			{
				Message m = call(MessageRecipients.MR_BROKER, MessageTypes.MT_GETDATA);
				switch (m.header.type)
				{
					case MessageTypes.MT_DATA:
						Console.WriteLine($"Получено сообщение от клиента: {m.header.from}");
						Console.WriteLine(m.data); // не робит
						Console.WriteLine("Выберите действие:");
						break;
					case MessageTypes.MT_CHECKUSERS:
						Console.WriteLine("Список клиентов:");
						Console.WriteLine(m.data); // норм вывод кирилицы
						Console.WriteLine("Выберите действие:");
						break;
					default:
						Thread.Sleep(100);
						break;
				}
			}
		}
		static void PrintMenu()
        {
			Console.WriteLine("~Список действий~");
			Console.WriteLine("1. Отправить сообщение всем");
			Console.WriteLine("2. Отправить сообщение определенному юзеру");
			Console.WriteLine("3. Вывести всех клиентов");
			Console.WriteLine("4. Выход");
			Console.WriteLine("Выберите действие:");
		}
		public Client()
        {
			Thread t = new Thread(ProcessMessages);
			t.Start();

			var m = call(MessageRecipients.MR_BROKER, MessageTypes.MT_INIT);
			this.id = (int)m.header.to;
			MainFunction();
		}
		void MainFunction()
        {
			Console.OutputEncoding = Encoding.UTF8;
			Console.WriteLine($"Поздравляем с подключением! Ваш ID: {this.id}");
			while (true)
			{
				PrintMenu();
				switch(Convert.ToInt32(Console.ReadLine()))
                {
					case 1:
						Console.WriteLine("Введите сообщение: ");
						var msg = Console.ReadLine();
						if (msg is not null)
                        {
							send(MessageRecipients.MR_ALL, MessageTypes.MT_DATA, msg);
						}
						break;
					case 2:
						Console.WriteLine("Введите ID клиента: ");
						int ClientID = Convert.ToInt32(Console.ReadLine());
						Console.WriteLine("Введите сообщение: ");
						var msg1 = Console.ReadLine();
						if (msg1 is not null)
						{
							send((MessageRecipients)ClientID, MessageTypes.MT_DATA, msg1);
						}
						break;
					case 3:
						send(MessageRecipients.MR_BROKER, MessageTypes.MT_CHECKUSERS);
						break;
					case 4:
						send(MessageRecipients.MR_BROKER, MessageTypes.MT_EXIT);
						System.Environment.Exit(-1);
						break;
					default:
						Console.WriteLine("Ошибка! Попробуйте еще раз!");
						break;
				}
			}
		}
	}
}
