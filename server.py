# -- coding: utf-8 --

import socket
import sys
import json

online_clients = [] #global list
# online_clients = [ ("email", "name", port#),
#                    ("email", "name", port#)]

#server side database of client's contact list

# read file
# with open('client_contacts.json', 'r') as myfile:
#   data=myfile.read()

# # parse file
# client_contacts = json.loads(data)

# print(client_contacts)

try:
    fin = open("client_contacts.json","r")
    client_contacts = json.load(fin)
except:
    print("No client_contacts.json found.\n")

    fout = open("client_contacts.json", "w")

    print("Empty new client_contacts.json created.\n")

    client_contacts = [("hi","bye"), ("hiagain","byeagain")]
    #client_contacts = []
    print("client contacts:")
    print(client_contacts)

    json_string = json.dumps(client_contacts)

    print("json string: ")
    print(json_string)

    fout.write(json_string)
    fout.close


print(client_contacts)


#use client_contacts = [ ("client_email", [ "contact_email", "contact_email"]),
#                        ("client_email", [ "contact_email", "contact_email"]) ]

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
host = "localhost"  # localhost
port = 12343 #port number
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind((host,port)) # binds address:(hostname,port#) to socket 
s.listen(5)


######### getter methods ##########

#list_out_contacts() used for checking if contact is online
def list_out_contacts(email_list):  
  online_list = []
  for email in email_list:
    #if email in online_clients:
    for online in online_clients: # online = tuple ("email", "name", "port#")
      if email == online[0]:
        tuple = (online[1], email)
        online_list.append(tuple) # add name & email of online contact, from tuple
  return online_list

#intersection() used for cross checking mutual contacts
def intersection(lst1, lst2):  
    lst3 = [value for value in lst1 if value in lst2]
    return lst3




######### main server feedback loop ##########
  
while True:
  print("Listening at ", s.getsockname())
  client, addr = s.accept() #clients being taken in
  
  
  print("Accept connection from: ", addr)
  print("Connection built from ", client.getsockname(), " and ", client.getpeername())
  
  message_decoded = client.recv(1024).decode("utf-8") #receiving data from client
  print ("[*] Received '", message_decoded,"' from the client") #what data was obtained
  message_arr = message_decoded.split()
  
  sender = message_arr[0]
  request = message_arr[1]

  print("MESSAGE DECODED", message_decoded)  

  print("online_clients:", online_clients)
    ##@@@@!!!!!!@@@@@@####@@@!!!!@@### UPDATES PORT AFTER EVERY CLIENT CALL, BIG SECURITY HOURS ###@@!!!!!@####
  for tuple in online_clients: # update the port number of corresponding client
    if sender == tuple[0]:     # so the server knows the port # to send to according to whatever email 
      new_tuple = (tuple[0], tuple[1],  addr[1]) #("email", "name", port#)
      online_clients.remove(tuple)
      online_clients.append(new_tuple)
      #print("old port #: ", tuple[2])              @@@@@@@need this later
  #print("list client call, new port #: ", addr[1]) @@@@@@@need this later

  #client.send()
  
  #client sends email to server, and appends to online clients
  if request == "login":
    print("login client call port #: ", addr[1])
    client_email = message_arr[0]
    client_name = message_arr[2].split('_')
    client_tuple = (client_email, client_name[0], addr[1])
    online_clients.append(client_tuple)
    print(online_clients)
    client.send(bytes(str(addr[1]), "utf-8"))




  #client sends email to server, and removes them from online clients
  if request == "logout": ######################
    client_email = message_arr[0]
    client_name = message_arr[2].split('_')
    client_tuple = (client_email, client_name[0], addr[1])
    #print(client_email)
    #print(online_clients)
    print(client_tuple)
    print(online_clients)

    #remove ourself from online_clients list
    for tuple in online_clients:
      if client_email == tuple[0]:
        online_clients.remove(client_tuple) 
    print(online_clients)
  



  if request == "list":  ###################### one thing left, cross check to see both clients have each other added
    email_list = [] #at every index greater than 0 and 1, add to list
    i = 2           #ignore indexes 0,1 of message_arr because those are email and name
    while i < len(message_arr):
      email_list.append(message_arr[i]) #appends client list of emails
      i+=1

    print("CHECKPOINT2")
    online_list = list_out_contacts(email_list)

    #use client_contacts = [("client_email", [ "contact_email", "contact_email"]),
    #                       ("client_email", [ "contact_email", "contact_email"])]



    reply_string = ""
    for e in online_list:
      #print("e[0]: ", e[0])
      #print("e[1]: ", e[1])
      full_name = ""
      for name in e[0]:
        full_name += name + " "
      reply_string += full_name + "_" + e[1] + ","

  
    print("REPLY_STRING", bytes(reply_string, "utf-8"))

    if reply_string == "":
      reply_string = "NO FRIENDS ARE ONLINE"
    client.send(bytes(reply_string, "utf-8"))



  if request == "overwrite": ######################
    contact_name_to_remove = message_arr[2]
    print("online_clients BEFORE removing overwritten contact: ", online_clients)
    for tuple in online_clients:
      if contact_name_to_remove == tuple[1]:
        online_clients.remove(tuple)
    print("online_clients AFTER removing overwritten contact: ", online_clients)





  ###########################send#############################

  if request == "send": #checks for the following:
                        #sender is sending, 
                        #receiver's email matches with recipient
                        #if recipient is online
                        #send request to recipient to accept or decline send
    client.send(bytes("Ready for File", "utf-8")) 
    file_contents_decoded = client.recv(1024).decode("utf-8")
    #check if client b
    #FIB server asks client B if they want the file, socket name = recipient_client
    #online clients 


    ##### CREATE NEW SOCKET FOR CLIENT B #####
    #recip_port = get port from online_clients matching recipient email
    #create new socket and bind with ipaddr =localhost and port = recip_port
    
    client.send(bytes("Accept file?"))
    #not sure if i need this
    acceptance = client.recv(1024).decode("utf-8")

    if acceptance == "yes" or acceptance == "Y" or acceptance == "y":
      client.send(file_contents_decoded)
    
    if acceptance == "no" or acceptance == "N" or acceptance == "n":
      break
      
      '''
    recipient_email = 
    email = message_arr[0]
    if (recipient_email == email)
    if ()'''

    # for tuple in online_clients: # update the port number of corresponding client
    #   if sender == tuple[0]:
    #     new_tuple = (tuple[0], tuple[1],  addr[1])
    #     online_clients.remove(tuple)
    #     online_clients.append(new_tuple)

  print("The sender is : ", sender)
  #client.send(bytes(reply_msg, "utf-8"))
  #client.close()


  print("client replied, socket closed")
