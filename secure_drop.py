#Derrick Lor,Tharith Sovann, Tony Dam
##########PLEASE INSTALL rsa----> pip install rsa
##########PLEASE INSTALL PyInputPlus -----> pip install PyInputPlus
import pyinputplus as pyip
import sys, traceback, json, hashlib, os, rsa
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from os.path import exists

import client

def main():

    #result = pyip.inputMenu(['dog', 'cat', 'moose'], lettered=True, numbered=False)
    first_time_login_prompt = "No users are registered with this client.\nDo you want to register a new user (y/n)?"

    try:
        fin = open("registered.txt","r")
        fin.close()
        login()
    except KeyboardInterrupt:
        exit(0)
    except FileNotFoundError:
        response = input(first_time_login_prompt)
        while (response != "y" and response != "Y"):
            response = input(first_time_login_prompt)
        if(response == "y" or response == "Y"):
            print("SecureDrop Registering:")
            name = pyip.inputStr("Enter Full Name: ")
            email = pyip.inputStr("Enter Email Address: ")
            password = pyip.inputPassword("Enter Password: ")
            password2 = pyip.inputPassword("Re-enter Password: ")
        
            ########PASSWORD HASHING########
            salt = os.urandom(32)

            key = hashlib.pbkdf2_hmac(
                'sha256', # hash digest alggo for HMAC
                password.encode('utf-8'), # convert password to bytes
                salt, # provide the generated salt
                100000  # 100000 iterations of SHA-256
                #dklen=128 #if need a longer key for something like AES, give desired key size to dklen, ex. <--- get 128 byte key    
            )
            ''''
            print("salt: \n")
            print(salt)
            '''
            while (password != password2):
                print("Passwords do not match.")
                password = pyip.inputPassword("Enter Password: ")
                password2 = pyip.inputPassword("Re-enter Password: ")

            print("Passwords Match.")
            #convert name and email str into bytes
            name_bytes = str.encode(name + "\n")
            email_bytes = str.encode(email + "\n")
        
            newline_bytes = str.encode("\n")

            #write to file and save credentials
            fout = open("registered.txt", "wb")
    
            fout.write(name_bytes)
            fout.write(email_bytes)
        
            fout.write(key)
            fout.write(newline_bytes)
            fout.write(salt)
            fout.write(newline_bytes)

            fout.close()
        
            print("User Registered.")
        else:
            print("Exiting Secure Drop.")
            exit(0)

    try:
        login()
    except KeyboardInterrupt:
        exit(0)

  

def login():

    print("SecureDrop Login:")
    email = pyip.inputStr("Enter Email Address: ")
    password = pyip.inputPassword("Enter Password: ")
    #check passwords
    
    email_bytes = str.encode(email + "\n")

    fin = open('registered.txt', 'rb')
    lines = fin.readlines()
    
    i = 1
    while i < len(lines):
        if (lines[i] == email_bytes):
            salt = (lines[i+2]).strip() # get rid of the "\n" at the end
            #print("salt: \n")
            #print(salt)
            #use this salt to hash the input password and verify

            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
                # that dklen thingy for future milestones
            )

            keya = (lines[i+1]).strip() # get rid of the "\n" at the end
            ''''
            print("new key: \n")
            print(new_key)
            print("key: \n")
            print(key)
            '''
            name = lines[0].decode("utf-8")
            if new_key == keya:
                client.client_logged_in(name, email) # makes client call to server to list this user as logged in
                
                program(name, email)
            else:
                print("Email and Password Combination Invalid \n")
                login()
        i+=1
    print("Email and Pasword Combination Invalid \n")
    login()
       





def add_contacts(user_email):
    #inputs
    print("Who would you like to add?: ")
    name = pyip.inputStr("Enter Full Name: ")
    email = pyip.inputStr("Enter Email Address: ")

    
    #keys that is randomly generated
    key = RSA.generate(2048) 

    #convert name and email str into bytes
    name_bytes = str.encode(name)
    email_bytes = str.encode(email)
    newline_byte = str.encode("\n")

    #code needed to access contacts decryption
    #fin = open('contacts.pem', 'rb')
    #lines = fin.readlines()

   # priv_key_bytes = str.encode(priv_key + "\n")
    
    priv_key = key.export_key() #creates a private key

    overwrite = 0

    lines = []

    if (exists('contacts.pem')):
        with open('contacts.pem') as my_file:
            for line in my_file:
                lines.append(line)

    stripped_lines = [line.strip() for line in lines]

    i = 1
    while i < len(stripped_lines):
        print(type(stripped_lines[i]), "comparing with", type(email))
        stripped_line = stripped_lines[i]
        if stripped_line.strip() == email:
            print("OVERWRITING DATA...")
            stripped_lines[i - 1] = name
            overwrite = 1

            client.remove_overwritten_contact_from_server(user_email, stripped_lines[i - 1])

        i += 2

    if overwrite == 1:
        file_out = open("contacts.pem", 'wb')
        for item in stripped_lines:
            file_out.write(str.encode(item))
            file_out.write(newline_byte)

    if overwrite == 0:
        
        file_out = open("contacts.pem", 'ab')
        #file_out.write(priv_key)
        #file_out.write(newline_byte)
        #file_out.write(encName)
        file_out.write(name_bytes)
        file_out.write(newline_byte)
        #file_out.write(encEmail)
        file_out.write(email_bytes)
        file_out.write(newline_byte)

    file_out.close() 
    
    #print(priv_key)

    client.client_req_add(user_email, email)

    print("Contact Added")








def list_contacts():
    #send server a list of our contacts
    #server replies with list of contacts that are online
    #display contacts that are online   
    lines = []
    email_list = []

    if (exists('contacts.pem')): # gets a list of emails of contacts 
        with open('contacts.pem') as my_file:
            for line in my_file:
                lines.append(line)

    stripped_lines = [line.strip() for line in lines]

    i = 1
    while i < len(stripped_lines):
        stripped_line = stripped_lines[i]
        email_list.append(stripped_lines[i].strip())
        i += 2

    name_email_arr = []
    my_email = ""

    if (exists('registered.txt')): # gets the email of logged in user to pass to server
        with open('registered.txt', 'rb') as login_info:
            for info in login_info:
                name_email_arr.append(info)

    name_email_arr = [line.strip() for line in name_email_arr]
    my_email = (name_email_arr[1]).decode("utf-8")

    online_list = client.client_req_list(my_email, email_list) # use these two info to make client call to server
                                                                # to list out online contacts
    i = 0
    print("The following contacts are online: ")
    #print(online_list)
    online_list_arr = online_list.split(",")
    while i < len(online_list_arr) and i != (len(online_list_arr) - 1):
        name_email = online_list_arr[i].split('_')
        print("* ", name_email)
        #print(name_email[0], " ", name_email[1])
        i+=1
    





def send_file(result):
    arr_result = result.split()
    try:
        recipient_email = arr_result[1]
    except:
        print("No recipient specified.")
        return
    try:
        filename = arr_result[2]
    except:
        print("No filename specified.")
        return

    
    try:
        # Check the file exists
        content = open(filename, "rb")
    except:
        print ("Couldn't open file. Make sure the file name was entered correctly.")
        return

    print("Transmitting {} ...".format(filename))

    client.client_req_send(recipient_email, filename)
    


def download_file(my_email):

    client.client_req_download(my_email)








def program(name, email):
    prompt = "secure_drop$: "
    while True:
        try:
            result = pyip.inputStr(prompt)
    
            if(result == "-h" or result == "help"):
                print("'-h' or 'help' for help")
                print("'add' -> Add a new contact")
                print("'list' -> List all online contacts")
                print("'send' -> Transfer file to server")
                print("'download' -> Download file from server")
                print("'exit' -> Exit SecureDrop")
                print("End of help.")
            elif (result == "add"): # add contacts have been selected
                add_contacts(email)
            elif (result == "list"): # add contacts have been selected
                #print("Entering List_Contacts Function")
                list_contacts()
            elif (result[:4] == "send"):
                send_file(result)
            elif (result == "download"):
                download_file(email)
            elif (result == "exit"):
                client.client_logged_out(name, email) # makes client call to server to list this user as logged out
                sys.exit(0)
        except KeyboardInterrupt:
            client.client_logged_out(name, email) # makes client call to server to list this user as logged out
            sys.exit(0)
        except Exception:
            #client.client_logged_out(email)
            traceback.print_exc(file=sys.stdout)
            sys.exit(0)
        #except SystemExit:
            #client.client_logged_out(email)
        #finally:
            #client.client_logged_out(email)



if __name__ == "__main__":
    main()