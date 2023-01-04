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
        if(response == "y"):
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

        login()

  

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

            key = (lines[i+1]).strip() # get rid of the "\n" at the end
            ''''
            print("new key: \n")
            print(new_key)
            print("key: \n")
            print(key)
            '''
            if new_key == key:
                program()
            else:
                print("Email and Password Combination Invalid \n")
                login()
        i+=1
    print("Email and Pasword Combination Invalid \n")
    login()

def add_contacts():
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

    encName = rsa.encrypt(name_bytes, key)
    encEmail = rsa.encrypt(email_bytes, key)
    

    #file_key.write(newline_byte)
    #file_key.write(encEmail)

    #print(encName)
    #print("\n")
    #print(encEmail)

    file_out = open("contacts.pem", 'wb')
    file_out.write(priv_key)
    file_out.write(newline_byte)
    file_out.write(encName)
    file_out.write(newline_byte)
    file_out.write(encEmail)
    file_out.write(newline_byte)
    file_out.close() 
    
    #print(priv_key)

    print("Contact Added")
    program()


def program():
    print("Welcome to SecureDrop.")
    prompt = "secure_drop$: "
    while True:
        try:
            result = pyip.inputStr(prompt)
    
            if(result == "-h" or result == "help"):
                print("'-h' or 'help' for help")
                print("'add' -> Add a new contact")
                print("'list' -> List all online contacts")
                print("'send' -> Transfer file to contact")
                print("'exit' -> Exit SecureDrop")
                print("End of help.")
            elif (result == "add"): # add contacts have been selected
                add_contacts()
            elif (result == "exit"):
                sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            sys.exit(0)


if __name__ == "__main__":
    main()
