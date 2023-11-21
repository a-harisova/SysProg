#include "pch.h"
#include "SocketClient.h"
#include "Client.h"
#include "framework.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

CWinApp theApp;

int main()
{
	int nRetCode = 0;

	HMODULE hModule = ::GetModuleHandle(nullptr);

	if (hModule != nullptr)
	{
		// initialize MFC and print and error on failure
		if (!AfxWinInit(hModule, nullptr, ::GetCommandLine(), 0))
		{
			// TODO: code your application's behavior here.
			wprintf(L"Fatal Error: MFC initialization failed\n");
			nRetCode = 1;
		}
		else
		{
			Client client;
		}
	}
	else
	{
		// TODO: change error code to suit your needs
		wprintf(L"Fatal Error: GetModuleHandle failed\n");
		nRetCode = 1;
	}

	return nRetCode;
}