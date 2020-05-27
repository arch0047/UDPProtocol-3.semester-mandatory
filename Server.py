import socket
import sys
from datetime import datetime

# Creating the socket
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Defining the IP address and the Port Number
ip_address = '127.0.0.1'
server_port = 8080
server_address = (ip_address, server_port)
server_ip = server_address[0]
print('S: socket is created on {} port {}'.format(*server_address))

# Log File (LogFile)
filepath = r"C:\Users\archa\PycharmProjects\ClientServer\LogFile"
LogFile = open(filepath, "a")  # or 'w'
DtNow = datetime.now()
Dt = DtNow.strftime("%m/%d/%Y, %H:%M:%S")
LogFile.write("****************************************" + "\n")
LogFile.write("TimeStamp->new log: " + Dt + "\n")
LogFile.write('S: socket is created on {} port {}'.format(*server_address) + "\n")

# server binds the port and host together with the socket.
soc.bind(server_address)
print('S: waiting for client message !')
LogFile.write('S: waiting for client message !' + "\n")

# Receiving connection from client with client ip address
data, address = soc.recvfrom(1024)
decoded_data = data.decode()
print('C: ' + decoded_data)
LogFile.write('C: ' + decoded_data + "\n")

# Check - if Client request is valid server sends acknowledgement message
if decoded_data == 'com-0 127.0.0.1':
    ack_to_client = 'com-0 accept ' + server_ip
    soc.sendto(ack_to_client.encode(), address)
    print('S: ' + ack_to_client)
    LogFile.write('S: ' + ack_to_client + "\n")

else:
    fail_to_connect = "Oops, something went wrong, while connecting the socket"
    LogFile.write("Oops, something went wrong, while connecting the socket" + "\n")
    print('S: ' + fail_to_connect)
    LogFile.write('S: ' + fail_to_connect + "\n")
    deny_encoded = fail_to_connect.encode()
    soc.sendto(deny_encoded, address)
    soc.close()

# Client second message as acknowledge message
data, address = soc.recvfrom(1024)

if data.decode() == 'com-0 accept':  # if true
    print('C: ' + data.decode())
    LogFile.write('C: ' + data.decode() + "\n")
    print('Client has accepted the connection !')
    LogFile.write('Client has accepted the connection !' + "\n")

else:
    fail_to_connect = "Oops, something went wrong, while connecting the socket"
    LogFile.write("Oops, something went wrong, while connecting the socket" + "\n")
    print('S: ' + fail_to_connect)
    LogFile.write('S: ' + fail_to_connect + "\n")
    deny_encoded = fail_to_connect.encode()
    soc.sendto(deny_encoded, address)
    soc.close()

# var = count
count = 0
mStr = ' '
cMsg = ' '
response = "I am server "
wrongCmsgNr = 'wrong client message number'
previousSerMsgNr = 0
# Setting the timeout to 4 second . If client will not send the message for 4 seconds, server then
# sends a problem message to the client and server will close the socket.
soc.settimeout(10)

while mStr != 'Exit' and mStr != 'exit':

    try:
        # server receiving message from client
        data, address = soc.recvfrom(1024)
        cMsg = data.decode().split(":")

        # client message count and message
        count = int(cMsg[0])
        mStr = cMsg[1]

        # if count = 0 , first client message - No error (OK)
        # if current client message - previous server message = 1 (no error (OK)
        # Then message sequence is OK
        if (count == 0) and mStr != "con-h 0x00":
            print('C:msg-' + str(count) + ' = ' + mStr)
            count += 1 # increase server response counter by one
            sMsgCount = str(count) + ':' + response  # "I am server "
            soc.sendto(sMsgCount.encode(), address)
            print('S:msg-' + str(count) + ' = ' + response)
            previousSerMsgNr = count  # Save the current server msg.nr.

        # msg count check:( client message Nr , always one UP to previous server message Nr.)
        elif mStr != 'com-0 accept' and mStr != 'con-res 0xFF' and mStr != "con-h 0x00" \
             and mStr != '' and (count - previousSerMsgNr == 1):

            print('C:msg-' + str(count) + ' = ' + mStr)

            count += 1 # increase server response counter by one

            # send the server response
            sMsgCount = str(count) + ':' + response  # "I am server "
            soc.sendto(sMsgCount.encode(), address)
            print('S:msg-' + str(count) + ' = ' + response)
            previousSerMsgNr = count  # Save the current server msg.nr.

        # HeartBeat
        elif mStr == "con-h 0x00":
            print(mStr)

        # client side timeout message
        elif mStr == 'con-res 0xFF':
            print('C:con-res 0xFF')
            print('Closing the Socket !')
            soc.close()
            sys.exit()

        elif (mStr==''):
            mStr = mStr # Do nothing (no action in this case)

        else: # wrong message count, close the server after sending message to client
            print('S:msg-' + str(count) + ' = ' + wrongCmsgNr)
            sMsgCount = str(count) + ':' + wrongCmsgNr
            soc.sendto(sMsgCount.encode(), address)
            soc.close()
            sys.exit()

    # If no client pings the server for 4 seconds, we have to assume that the client is not active
    except socket.timeout as e:
        # in the array  time out value= [0]
        err = e.args[0]
        if err == 'timed out':
            response = "con-res 0xFE"
            # Server sends a special packet to client for shutting down the server

            count += 1  # increase server response counter by one
            sMsgCount = str(count) + ':' + response
            soc.sendto(sMsgCount.encode(), address)
            print('S:con-res 0xFE')

        else:
            print(e)
            sys.exit(1)
