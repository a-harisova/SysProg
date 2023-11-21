#pragma once

#include "../SocketServer/Message.h"

class Client
{
private:
	int id = 0;

	void send(int to, int type = MT_DATA, const string& data = "");
    Message call(int to, int type = MT_DATA, const string& data = "");
	void ProcessMessages();
	void PrintMenu();

    void send(CSocket& s, Message m)
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

public:
	Client();
    void MainFunction();
	~Client() {};
};
