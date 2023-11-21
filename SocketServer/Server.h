#pragma once

#include "Message.h"
#include "Session.h"

class Server
{
	static int maxID;
	map<int, shared_ptr<Session>> sessions;

    static void send(CSocket& s, int to, int from, int type = MT_DATA, const string& data = "");

    static void send(CSocket& s, Message m)
    {
        s.Send(&m.header, sizeof(MessageHeader));
        if (m.header.size)
        {
            s.Send(m.data.c_str(), (int)m.header.size);
        }
    }

    int receive(CSocket& s, Message& m)
    {
        if (!s.Receive(&m.header, sizeof(MessageHeader)))
        {
            return MT_NODATA;
        }
        if (m.header.size)
        {
            vector <char> v(m.header.size);
            s.Receive(&v[0], (int)m.header.size);
            m.data = string(&v[0], m.header.size);
        }
        return m.header.type;
    }

	void ProcessClient(SOCKET hSock);
	void IsActive();

public:
    Server();
};

