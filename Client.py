import socket
import time
from threading import Timer

# Reading the configuration file (opt.conf)
filepath = r"C:\Users\archa\PycharmProjects\ClientServer\opt.conf"
with open(filepath) as fp:
    # Read the first line of the file
    line = fp.readline()
    cnt = 1  # count = cnt

    # if the read line have text then continue reading otherwise exit the while loop
    while line:
        if cnt == 1:
            KeepALive, value = line.split(":")  # splitting the line at :
            KeepALive = value.strip()  # Removing white space from the line

        if cnt == 2:
            default_package_size, value = line.split(":")  # splitting the line at :
            default_package_size = int(value.strip())  # Removing the white space from the line

        line = fp.readline()
        cnt += 1
    # End of reading file configuration method

# client sends a heartbeat  to the server every 3rd seconds
dummyCount = 0


def heart_beat():
    if KeepALive == "True":
        Timer(4.0, heart_beat).start()  # timer with 2 parameter
        mHeart_beat = str(dummyCount) + ':' + "con-h 0x00"
        soc.sendto(mHeart_beat.encode(), server_address)
        return
    else:
        return


# Create a UDP socket
# SOCK_DGRAM UDP protocol
soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Defining the IP address and the Port Number
ip_address = '127.0.0.1'
server_port = 8080
server_address = (ip_address, server_port)
print("Socket successfully created")

client_ip = '127.0.0.1'

# Hack_ip= '127.00.2'     #  ip address "To Hack Myself"

# client makes a Connection request and send it to the server
request_message = 'com-0 ' + client_ip
print('C: ' + request_message)

# client encode the message before sending
request_message_encoded = request_message.encode()
soc.sendto(request_message_encoded, server_address)

# client receives the acceptance message
data, address2 = soc.recvfrom(1024)
decoded_data = data.decode()
print('S:' + decoded_data)

# client sends accept message
if address2 == server_address and decoded_data == 'com-0 accept 127.0.0.1':
    connection_accept = 'com-0 accept'

    connection_message__encoded = connection_accept.encode()
    soc.sendto(connection_message__encoded, server_address)
    print('C: ' + connection_accept)
    tw_handshake_complete = True
    print('C: Three way handshake is successfully completed.')

else:
    tw_handshake_complete = False
    print('C: Closing socket')
    soc.close()

# variables
count = 0
AutoMsg_count = 0
mStr = ' '
cMsgCount = ' '  # message with count
startTime = 0
endTime = 0
TIMEOUT = 10  # if time out set to 4 second then client need to wait for 5 second and
# then show the timeout message and press enter this is to avoid the situation where
# client side console wait to write a message instead writing a self message for the console.


while mStr != 'Exit' and mStr != 'exit' and tw_handshake_complete == True:

    # send 25 package automatically in 1 second when "default_package_size"  is set
    # less <= 25
    AutoMsg_count = 0
    startTime = time.time()

    while default_package_size > AutoMsg_count and AutoMsg_count < 25 and endTime - startTime <= 1:
        AutoMsgStr = str(count) + ':' + 'Automatic_message-' + str(AutoMsg_count)
        soc.sendto(AutoMsgStr.encode(), server_address)
        print('C:msg-' + str(count) + ' = ' + 'Automatic_message'+ str(AutoMsg_count))
        AutoMsg_count += 1  # package message count

        # server message count and message
        data, address2 = soc.recvfrom(1024)
        sMsg = data.decode().split(":")
        count = int(sMsg[0])
        print('S:res-' + str(count) + ' = ' + sMsg[1])
        count += 1  # client message counter
        endTime = time.time()

    heart_beat()

    try:
        # converting  integer into string str(count)
        cMsgCount = 'C:msg-' + str(count) + ' = '

        t = Timer(TIMEOUT, print, ['Time Out:Press Enter to continue/exit:'])
        t.start()

        mStr = input(cMsgCount)
        cMsgCount = str(count) + ':' + mStr
        t.cancel()

        if mStr == " ":
            mStr = 'con-res 0xFF'
            count = count + 1
            cMsgCount = str(count) + ':' + mStr
            soc.sendto(cMsgCount.encode(), server_address)
            mStr = 'Exit'
            soc.close()
        else:
            soc.sendto(cMsgCount.encode(), server_address)

        # server message count and message
        data, address2 = soc.recvfrom(1024)
        sMsg = data.decode().split(":")
        count = int(sMsg[0])
        decoded_data = sMsg[1]

        # idle_check_server(data.decode())
        if decoded_data != 'con-res 0xFE':
            print('S:res-' + str(count) + ' = ' + decoded_data)
            count = count + 1

        else:  # send the acknowledge message to the server to confirm that client has received the closing message
            mStr = 'con-res 0xFE'
            print('S:' + mStr)
            cStrMessage = 'con-res 0xFF'
            count = count + 1
            cMsgCount = str(count) + ':' + cStrMessage
            soc.sendto(cMsgCount.encode(), server_address)
            count = count + 1
            print('C:' + 'con-res 0xFF')
            mStr = 'Exit'
            soc.close()

    # If no client pings the server for 4 seconds, we have to assume that the client is not active
    except socket.timeout as e:
        # if array [0] is = timed out
        data, address2 = soc.recvfrom(1024)
        print('S:ServerStoppingMessage to Client:' + data.decode())
        err = e.args[0]
        if err == 'timed out' and data.decode() == 'con-res 0xFE99':
            cStrMessage = 'con-res 0xFF'
            soc.sendto(cStrMessage.encode(), server_address)
            print('C:ClientAcknowledgeMessage to Server:con-res 0xFF99')
            soc.close()

        else:
            print(e)
