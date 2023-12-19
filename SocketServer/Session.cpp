#include "pch.h"
#include "Session.h"

void Session::send(CSocket& s, int to, int from, int type, const string& data)
{
	Message m(to, from, type, data);
	send(s, m);
}

void Session::updateLastInteraction()
{
	lastInteraction = system_clock::now();
}

bool Session::stillActive()
{
	if (this->inActivity() > 300000)
		return false;
	else
		return true;

}

int Session::inActivity()
{
	auto now = system_clock::now();
	auto intSeconds = duration_cast<milliseconds>(now - lastInteraction);
	return intSeconds.count();
}