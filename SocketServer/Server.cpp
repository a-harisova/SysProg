#include "pch.h"
#include "Server.h"
#include "framework.h"
#include "../SocketServer/Message.cpp"

int Server::maxID = MR_USER;

void LaunchClient(LPSTR name)
{
	STARTUPINFO si = { sizeof(si) };
	PROCESS_INFORMATION pi;
	CreateProcess(NULL, name, NULL, NULL, TRUE, CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi);
	CloseHandle(pi.hThread);
	CloseHandle(pi.hProcess);
}

void Server::send(CSocket& s, int to, int from, int type, const string& data)
{
	Message m(to, from, type, data);
	send(s, m);
}

void Server::ProcessClient(SOCKET hSock)
{
	setlocale(LC_ALL, "Russian");
	CSocket s;
	s.Attach(hSock);
	Message m;
	switch (receive(s, m))
	{
	case MT_INIT:
	{
		auto session = make_shared<Session>(++maxID);
		sessions[session->id] = session;
		send(s, session->id, MR_BROKER, MT_INIT);
		session->updateLastInteraction();
		cout << "Клиент " << session->id << " подключился!" << endl;
		break;
	}
	case MT_INITSTORAGE:
	{
		auto session = make_shared<Session>(MR_STORAGE);
		sessions[session->id] = session;
		send(s, session->id, MR_BROKER, MT_INITSTORAGE);
		session->updateLastInteraction();
		cout << "Сервер подключился" << endl;
		break;
	}
	case MT_EXIT:
	{
		CCriticalSection cs;
		CSingleLock lock(&cs, TRUE);
		sessions.erase(m.header.from);
		send(s, m.header.from, MR_BROKER, MT_CONFIRM);
		cout << "Клиент " << m.header.from << " отключился!" << endl;
		break;
	}
	case MT_GETDATA:
	{
		auto iSession = sessions.find(m.header.from);
		if (iSession != sessions.end())
		{
			iSession->second->send(s);
			iSession->second->updateLastInteraction();
		}
		break;
	}
	case MT_CHECKUSERS:
	{
		string str = "";
		auto iSession = sessions.find(m.header.from);
		if (iSession != sessions.end())
		{
			for (auto& [id, session] : sessions)
			{
				if (id != m.header.from && id != MR_STORAGE)
				{
					str.append("ID = ");
					str.append(to_string(session->id));
					str.append("\n");
				}
			}
			Message ms(m.header.from, MR_BROKER, MT_CHECKUSERS, str);
			iSession->second->add(ms);
			iSession->second->updateLastInteraction();
		}
		break;
	}
	case MT_GETLAST:
	{
		if (m.header.from == MR_STORAGE)
		{
			auto iSessionTo = sessions.find(m.header.to);
			if (iSessionTo != sessions.end())
			{
				Message ms = Message(m.header.to, MR_BROKER, MT_GETLAST, m.data);
				iSessionTo->second->add(ms);
			}
		}
		else
		{
			auto iSessionFrom = sessions.find(m.header.from);
			auto StorageSession = sessions.find(MR_STORAGE);
			if (StorageSession != sessions.end() && iSessionFrom != sessions.end())
			{
				iSessionFrom->second->updateLastInteraction();
				Message ms = Message(MR_STORAGE, m.header.from, MT_GETLAST);
				StorageSession->second->add(ms);
			}
		}

		break;
	}
	default:
	{
		auto iSessionFrom = sessions.find(m.header.from);
		auto StorageSession = sessions.find(MR_STORAGE);
		if (iSessionFrom != sessions.end() && m.header.from != MR_STORAGE)
		{
			auto iSessionTo = sessions.find(m.header.to);
			if (iSessionTo != sessions.end())
			{
				iSessionTo->second->add(m);
				if (StorageSession != sessions.end())
				{
					m.data = to_string(m.header.from) + "'&'" + m.data;;
					Message ms = Message(MR_BROKER, m.header.to, MT_DATA, m.data);
					StorageSession->second->add(ms);
				}
			}
			else if (m.header.to == MR_ALL)
			{
				for (auto& [id, session] : sessions)
				{
					if (id != m.header.from && id != MR_STORAGE)
					{
						session->add(m);
						if (StorageSession != sessions.end())
						{
							string mes = to_string(m.header.from) + "'&'" + m.data;;
							Message ms = Message(MR_BROKER, id, MT_DATA, mes);
							StorageSession->second->add(ms);
						}
					}
				}
			}
			iSessionFrom->second->updateLastInteraction();
		}
		break;
	}
	}
}

void Server::IsActive() 
{
	while (true)
	{
		CCriticalSection cs;
		CSingleLock lock(&cs, TRUE);
		for (auto& [id, session] : sessions)
		{
			if (!(session->stillActive()))
			{
				cout << "Время ожидания закончилось. Клиент " << id << " отключён!" << endl;
				sessions.erase(id);
				break;
			}
		}
		Sleep(1000);
	}
}

Server::Server()
{
	thread clientConnection(&Server::IsActive, this);
	clientConnection.detach();
	maxID = MR_USER;

	AfxSocketInit();

	CSocket Server;
	Server.Create(12345);
	
	LaunchClient("SocketClient.exe");
	LaunchClient("SharpClient.exe");

	while (true)
	{
		if (!Server.Listen())
			break;
		CSocket s;
		Server.Accept(s);
		thread t(&Server::ProcessClient, this, s.Detach());
		t.detach();
	}
}


