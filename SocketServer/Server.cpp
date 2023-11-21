#include "pch.h"
#include "Server.h"
#include "framework.h"
#include "../SocketServer/Message.cpp"

int Server::maxID = MR_USER;

void LaunchClient()
{
	STARTUPINFO si = { sizeof(si) };
	PROCESS_INFORMATION pi;
	CreateProcess(NULL, (LPSTR)"SocketClient.exe", NULL, NULL, TRUE, CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi);
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
				if (id != m.header.from)
				{
					str.append("Клиент ");
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
	default:
	{
		auto iSessionFrom = sessions.find(m.header.from);
		if (iSessionFrom != sessions.end())
		{
			auto iSessionTo = sessions.find(m.header.to);
			if (iSessionTo != sessions.end())
			{
				iSessionTo->second->add(m);
			}
			else if (m.header.to == MR_ALL)
			{
				for (auto& [id, session] : sessions)
				{
					if (id != m.header.from)
						session->add(m);
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

	for (int i = 0; i < 3; ++i)
	{
		LaunchClient();
		Sleep(100);
	}

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


