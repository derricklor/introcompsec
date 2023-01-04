# -- coding: utf-8 --

import socket
import sys
import json
import os

online_clients = [] #global list
# online_clients = [ ("email", "name", port#),
#                    ("email", "name", port#)]

#server side database of client's contact list

#client_contacts = [ ("client_email", [ "contact_email", "contact_email"]),
#                    ("client_email", [ "contact_email", "contact_email"]) ]
try:
    fin = open("client_contacts.json","r")
    client_contacts = json.load(fin)
except:
    print("No client_contacts.json found.\n")

    fout = open("client_contacts.json", "w")

    print("Empty new client_contacts.json created.")

    #client_contacts = [("hi","bye"), ("hiagain","byeagain")]
    client_contacts = []
    
    json_string = json.dumps(client_contacts)

    fout.write(json_string)
    fout.close


#server side database of available download list
#available_downloads = ["filename", "filename"]
try:
    fin = open("available_downloads.json","r")
    available_downloads = json.load(fin)
except:
    print("No available_downloads.json found.\n")

    fout = open("available_downloads.json", "w")

    print("Empty new available_downloads.json created.")

    #available_downloads = ["filename", "filename"]
    available_downloads = []
    
    json_string = json.dumps(available_downloads)

    fout.write(json_string)
    fout.close



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
  print("sender:")
  print(sender)
  print("request:")
  print(request)
  print("MESSAGE DECODED", message_decoded)  

  print("online_clients:", online_clients)
  ##@@@@!!!!!!@@@@@@####@@@!!!!@@### UPDATES PORT AFTER EVERY CLIENT CALL, BIG SECURITY HOURS ###@@!!!!!@####
  for tuple in online_clients: # update the port number of corresponding client
    if sender == tuple[0]:     # so the server knows the port # to send to according to whatever email 
      new_tuple = (tuple[0], tuple[1],  addr[1]) #("email", "name", port#)
      online_clients.remove(tuple)
      online_clients.append(new_tuple)

  
  #client sends email to server, and appends to online clients
  if request == "login":
    print("login client call port #: ", addr[1])
    client_email = message_arr[0]
    client_name = message_arr[2].split('_')
    client_tuple = (client_email, client_name[0], addr[1])
    online_clients.append(client_tuple)
    #print(online_clients)
    client.send(bytes("1", "utf-8"))




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
  





  if request == "add":
    newContactEmail= message_arr[2]
    foundFlag = 0 
    #check if sender email already exists in client_contacts
    #if so, append newContactEmail to sender
    for tuple in client_contacts:
      if tuple[0] == sender:
        foundFlag = 1
        tuple[1].append(newContactEmail) # new email arg

    if foundFlag == 0:  #then sender was not found in client_contacts
      #add sender in client_contacts
      tuple = (sender,[newContactEmail])
      client_contacts.append(tuple)


    #receive message in format of: <my_email> add <email of new contact> 
    #check if request is add
    #append email of new contact to client_contacts[my_email] 

    #save the client_contacts to json and write to file
    fout = open("client_contacts.json", "w")
    json_string = json.dumps(client_contacts)
    fout.write(json_string)
    fout.close

    reply_string = "Contact added to server"
    print(reply_string)
    client.send(bytes(reply_string, "utf-8"))







  if request == "list":  ###################### one thing left, cross check to see both clients have each other added
    email_list = [] #at every index greater than 0 and 1, add to list
    i = 2           #ignore indexes 0,1 of message_arr because those are email and name
    while i < len(message_arr):
      email_list.append(message_arr[i]) #appends client list of emails
      i+=1

    online_list = list_out_contacts(email_list)
    # online_list = [ ("name", "email"),("name", "email")]

    #use client_contacts = [("client_email", [ "contact_email", "contact_email"]),
    #                       ("client_email", [ "contact_email", "contact_email"])]

    ###########mutual contacts###############
    # for each person in online_list
    # check if they have me, sender, in their contact list

    mutual_list = []

    for ele in online_list:
        email = ele[1]
        for tuple in client_contacts:
             if tuple[0] == email:
                 for y in tuple[1]:
                     if y == sender:
                         tup = ele
                         mutual_list.append(tup)

    reply_string = ""
    for e in mutual_list:
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

    #receive recipient name, filename, filesize
    file_contents_decoded = client.recv(1024).decode("utf-8")
    send_details = file_contents_decoded.split()

    recipient_email = send_details[0]
    filename = send_details[1]
    #add to list of available files to download
    tuple = (recipient_email, filename)
    available_downloads.append(tuple)

    #save the available_downloads to json and write to file
    fout = open("available_downloads.json", "w")
    json_string = json.dumps(available_downloads)
    fout.write(json_string)
    fout.close

    filesize = int(send_details[2])

    output_file = open(filename, "w")
    bytes_received = 0

    while bytes_received < filesize:
        data = client.recv(1024).decode("utf-8")
        output_file.write(data)
        bytes_received += 1024
    output_file.close()

    reply_string = "Done"
    client.send(bytes(reply_string, "utf-8"))




########### download ###########

  if request == "download":

    
    message = ""
    for tuple in available_downloads:
      if tuple[0] == sender:
        message += tuple[1] + " "

    if message == "": #no available files to download
      message = " "   #cant send string of size 0 through socket
    
    #send list of file names to client
    client.send(bytes(message, "utf-8")) 

    if message != " ":  #if no available files skip code below
      #receive file name to download
      filename = client.recv(1024).decode("utf-8")

      print("filename received:")
      print(filename)
      # send_request = filename bytes
      send_request = filename + " "
      sizeinbytes = os.path.getsize(filename)
      send_request += str(sizeinbytes)

      print(send_request)

      client.send(bytes(send_request, "utf-8"))

      
      #converts and sends file as string to client
      server_file = open(filename, "rb")
      client_file_data = server_file.read(1024)

      sentbytes = 0
      while sentbytes < sizeinbytes:
          client.send(client_file_data)
          client_file_data = server_file.read(1024)
          sentbytes += 1024
      
      server_file.close()

      message = client.recv(1024).decode("utf-8")
      print(message)




  print("The sender is : ", sender)
  print("client replied, socket closed")
