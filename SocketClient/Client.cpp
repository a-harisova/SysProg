#include "pch.h"
#include "Client.h"
#include "../SocketServer/Message.cpp"

int Get_Correct_Number(int min, int max)
{
    int value;
    while ((std::cin >> value).fail() || value < min || value > max || std::cin.peek() != '\n')
    {
        std::cin.clear();
        std::cin.ignore(10000, '\n');
        std::cout << "����������, ������� ���������� �������� (" << min << "-" << max << ") : ";
    }
    return value;
};

void Client::send(int to, int type, const string& data)
{
    CSocket s;
    s.Create();
    if (!s.Connect("127.0.0.1", 12345))
    {
        cout << "������ ����������! ���������� �����." << endl;
    }
    Message m(to, id, type, data);
    send(s, m);
}

Message Client::call(int to, int type, const string& data)
{
    CSocket s;
    s.Create();
    if (!s.Connect("127.0.0.1", 12345))
    {
        cout << "������ ����������! ���������� �����." << endl;
    }
    Message m(to, id, type, data);
    send(s, m);

    if (receive(s, m) == MT_INIT)
    {
        id = m.header.to;
    }

    return m;
}

void Client::ProcessMessages()
{
    while (true)
    {
        Message m = call(MR_BROKER, MT_GETDATA);
        switch (m.header.type)
        {
        case MT_DATA:
            cout << endl << "�������� ��������� �� ������� " << m.header.from << " : " << endl << m.data << endl
                 << "�������� ��������: " << endl;
            break;
        case MT_CHECKUSERS:
            cout << endl << "������ ��������: " << endl << m.data << endl
                 << "�������� ��������: " << endl;
            break;
        default:
            Sleep(1000);
            break;
        }
    }
}

void Client::PrintMenu()
{
    cout << endl << "~������ ��������~" << endl
        << "1. ��������� ��������� ���� " << endl
        << "2. ��������� ��������� ������������� ����� " << endl
        << "3. ������� ���� �������� " << endl
        << "4. �����" << endl
        << "�������� ��������: " << endl;
}

Client::Client()
{
    AfxSocketInit();
    thread t(&Client::ProcessMessages, this);
    t.detach();

    Message m = call(MR_BROKER, MT_INIT); 

    this->id = m.header.to;
    MainFunction();
}

void Client::MainFunction()
{
    setlocale(LC_ALL, "Russian");

    cout << "����������� � ������������! ��� ID: " << this->id << endl; 

    while (true)
    {
        PrintMenu();
        switch (Get_Correct_Number(1, 4))
        {
        case 1:
        {
            cout << "������� ���������: ";
            string msg;
            cin.ignore();
            getline(cin, msg);
            send(MR_ALL, MT_DATA, msg);
            break;
        }
        case 2:
        {
            cout << "������� ID �������: ";
            int ClientID = Get_Correct_Number(0, 1000);
            cout << "������� ���������: ";
            string msg;
            cin.ignore();
            getline(cin, msg);
            send(ClientID, MT_DATA, msg);
            break;
        }
        case 3:
        {
            send(MR_BROKER, MT_CHECKUSERS);
            break;
        }
        case 4:
        {
            send(MR_BROKER, MT_EXIT);
            return;
        }
        default:
        {
            cout << "�������� ��������!\n";
        }
        }
    }
}


