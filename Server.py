import socket
import sys
from datetime import datetime

#Creating the socket
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Defining the IP address and the Port Number
ip_address = '127.0.0.1'
server_port = 8080
server_address = (ip_address, server_port)
server_ip = server_address[0]
print('S: socket is created on {} port {}'.format(*server_address))


#Log File (LogFile)
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
msg = decoded_data.split(" ")


#Check - if Client request is valid server sends acknowledgement message
if msg[0] == 'com-0':
    ack_to_client = 'com-0 accept ' + server_ip
    soc.sendto(ack_to_client.encode(),address)

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
msg = data.decode().split(" ")

if msg[1] == 'accept': # if true
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
# Setting the timeout to 4 second . If client will not send the message for 4 seconds, server then
# sends a problem message to the client and server will close the socket.
soc.settimeout(4)

while mStr != 'Exit' and mStr != 'exit':

    try:
        # server receiving message from client
        data, address = soc.recvfrom(1024)
        cMsg = data.decode().split(":")

        # client message count and message
        count = int(cMsg[0])
        mStr = cMsg[1]

        #  msg count
        if mStr != 'com-0 accept' and mStr != 'con-res 0xFF' and mStr != "con-h 0x00" and mStr != '':
            print('C:msg-' + str(count) + ' = ' + mStr)

            count = count + 1

            #send the server response
            sMsgCount = str(count) + ':' + response  # "I am server "
            soc.sendto(sMsgCount.encode(), address)
            print('S:msg-' + str(count) + ' = ' + response)

        #heart beat
        elif mStr == "con-h 0x00":
            print(mStr)

        # client side timeout message
        elif mStr == 'con-res 0xFF':
             print('C:con-res 0xFF')
             print('Closing the Socket !')
             soc.close()
             sys.exit()

        # If no client pings the server for 4 seconds, we have to assume that the client is not active
    except socket.timeout as e:
        # in the array  time out value= [0]
        err = e.args[0]
        if err == 'timed out':
            response = "con-res 0xFE"
            # Server sends a special packet to client for shutting down the server
            sMsgCount = str(count) + ':' + response
            soc.sendto(sMsgCount.encode(), address)
            print('S:con-res 0xFE')
            # count = count + 1

        else:
            print(e)
            sys.exit(1)
