#pragma once
#include "Message.h"
#include <chrono>

using namespace std::chrono;

class Session
{
	static void send(CSocket& s, int to, int from, int type = MT_DATA, const string& data = "");
	static void send(CSocket& s, Message m)
	{
		s.Send(&m.header, sizeof(MessageHeader));
		if (m.header.size)
		{
			s.Send(m.data.c_str(), (int)m.header.size);
		}
	}

public:
	int id;
	queue<Message> messages;
	system_clock::time_point lastInteraction;

	CCriticalSection cs;
	Session(int _id)
		:id(_id)
	{
	}
	
	void add(Message& m)
	{
		CSingleLock lock(&cs, TRUE);
		messages.push(m);
	}

	void send(CSocket& s)
	{
		CSingleLock lock(&cs, TRUE);
		if (messages.empty())
		{
			send(s, id, MR_BROKER, MT_NODATA);
		}
		else
		{
			Message m = messages.front();
			send(s, m);
			messages.pop();
		}
	}

	void updateLastInteraction();

	bool stillActive();

	int inActivity();
};

