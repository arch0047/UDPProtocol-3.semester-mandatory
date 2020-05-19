import socket
import sys
from datetime import datetime

# Log File (LogFile)
filepath = r"C:\Users\archa\PycharmProjects\ClientServer\LogFile"
LogFile = open(filepath, "a")
DtNow = datetime.now()
Dt = DtNow.strftime("%m/%d/%Y, %H:%M:%S")
LogFile.write("****************************************" + "\n")
LogFile.write("TimeStamp->new log: " + Dt + "\n")

# Creating the socket
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# SOCK_DGRAM UDP protocol

# Defining the IP address and the Port Number
ip_address = '127.0.0.1'
server_port = 8080
server_address = (ip_address, server_port)
server_ip = server_address[0]

print('S: socket is created on {} port {}'.format(*server_address))
LogFile.write('S: socket is created on {} port {}'.format(*server_address) + "\n")

# server binds the port and host together with the socket and
# waits for the connection from the client side to come before accepting the connection.
soc.bind(server_address)
print('S: waiting for client message !')
LogFile.write('S: waiting for client message !' + "\n")

# Receiving connection from client with client ip address
data, address = soc.recvfrom(1024)
# after receiving the data(message) from the client server decode the data
decoded_data = data.decode()
print('C: ' + decoded_data)
LogFile.write('C: ' + decoded_data + "\n")

# if request is valid server accepts and send acknowledgement "Connection accepted = com-0 accept "
if decoded_data == 'com-0 127.0.0.1':
    received_data = 'com-0 accept ' + server_ip
    print('S: ' + received_data)
    LogFile.write('S: ' + received_data + "\n")

    received_encoded = received_data.encode()

    soc.sendto(received_encoded, address)
    accepted = True

    print('C: ' + received_encoded.decode())
    LogFile.write('C: ' + received_encoded.decode() + "\n")
    print('Client has accepted the connection !')
    LogFile.write('Client has accepted the connection !' + "\n")

# if request is not valid server send a denial message to the client 'Connection failed'
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
# Setting the timeout to 4 second . If client will not send the message for 4 seconds, server then
# sends a problem message to the client and server will close the socket.
soc.settimeout(10)

while mStr != 'Exit' and mStr != 'exit':

    try:
        # server receiving message from client
        data, address = soc.recvfrom(1024)
        decoded_data = data.decode()

        if decoded_data == 'con-res 0xFF':
            print('C:con-res 0xFF')
            print('Closing the Socket !')
            soc.close()
            sys.exit()

        # setting msg count for the conversation message
        if decoded_data != 'com-0 accept' and decoded_data != 'con-res 0xFF':
            print('C:msg-' + str(count) + ' = ' + decoded_data)
            # when a new message has been received,the value (message count) has to be incremented by 1
            count = count + 1

        # servers response to the client
        if count != 0 and decoded_data != 'con-res 0xFF' and decoded_data != "con-h 0x00":
            response = "I am server "
            print('S:msg-' + str(count) + ' = ' + response)
            soc.sendto(response.encode(), address)
            count = count + 1

        # If no client pings the server for 4 seconds, we have to assume that the client is not active
    except socket.timeout as e:
        # in the array  time out value= [0]
        err = e.args[0]
        if err == 'timed out':
            response = "con-res 0xFE"
            # Server sends a special packet to client for shutingdown the server
            soc.sendto(response.encode(), address)
            print('S:con-res 0xFE')

        else:
            print(e)
            sys.exit(1)
