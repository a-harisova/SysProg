#pragma once

enum MessageTypes
{
	MT_INIT,
	MT_EXIT,
	MT_GETDATA,
	MT_DATA,
	MT_NODATA,
	MT_CONFIRM,
	MT_CHECKUSERS
};

enum MessageRecipients
{
	MR_BROKER = 10,
	MR_ALL = 50,
	MR_USER = 100
};

struct MessageHeader
{
	int to;
	int from;
	int type;
	int size;
};

class Message
{
public:
	MessageHeader header = {0};
	string data;
	static int clientID;

	Message() {}
	Message(int to, int from, int type = MT_DATA, const string& data = "")
	{
		this->data = data;
		header = {to, from, type, int(data.length())};
	}
};

