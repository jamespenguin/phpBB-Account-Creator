#!/usr/bin/env python
#
# Moroni's Fist Account Creator!
#
import sys, time, threading
import progressBar
import phpBB

###
# Global Config
###
# Cosmetic Variables
title = "phpBB Account Creator"
version = "1.0"

# Other Variables
output_path        = "credentials.txt"
start_url          = "" # Put here the registration link of the forum you'd like to make accounts for
show_bar           = False
number_of_accounts = 0
credentials        = []
count              = 0
thread_limit       = 20

#!# End Config #!#

def header():
    global title, version
    header = "-" * 60 + "\n"
    header += "|" + " " * 58 + "|\n"
    temp = "| " + "%s v%s" % (title, version)
    header += temp + " " * (59 - len(temp)) + "|\n"
    header += "|" + " " * 58 + "|\n"
    header += "-" * 60 + "\n"
    return header

def save_credentials(credentials):
    output_file = open(output_path, "w")
    for username, password in credentials:
        output_file.write("%s:%s\n" % (username, password))
    output_file.close()

def get_numerical_input(prompt):
    value = ""
    while not value:
        value = raw_input("[?] %s: " % prompt)
        try:
            value = int(value)
        except:
            value = 0
    return value

def display_bar():
    global number_of_accounts, count
    bar = progressBar.progressBar(number_of_accounts)
    while show_bar:
        if count >= number_of_accounts:
            break
        sys.stdout.write("\r[+] %s" % bar.get_bar(count))
        sys.stdout.flush()
        time.sleep(0.20)
    print "\r[+] %s" % bar.get_bar(number_of_accounts)

def register_account():
    global credentials, count, number_of_accounts

    p = phpBB.phpBB()
    try:
        if len(credentials) < number_of_accounts:
            account = p.create_account(start_url)
            if account and len(credentials) < number_of_accounts:
                credentials.append(account)
                count += 1
    except:
        pass


if __name__ == '__main__':
    try:
        print header()
    
        print "-" * 60
        print "[+] It's configuration time!"
        number_of_accounts = get_numerical_input("How many accounts should be made?")

        print "-" * 60
        print "[+] It's show time, here we go!"
        print "[+] Creating accounts..."

        show_bar = True
        t = threading.Thread(target=display_bar)
        t.start()
        while len(credentials) < number_of_accounts:
            while threading.activeCount() >= thread_limit:
                time.sleep(0.3)
            if len(credentials) >= number_of_accounts:
                break
            t = threading.Thread(target=register_account)
            t.start()
        show_bar = False
        while threading.activeCount() > 1:
            time.sleep(0.3)
        print "[+] The accounts have been created, now it's time to verify them!"

        count = 0
        show_bar = True
        t = threading.Thread(target=display_bar)
        t.start()
        for username, password in credentials:
            p = phpBB.phpBB()
            try:
                p.verify_email(username)
            except:
                pass
            time.sleep(3)
            count += 1
        show_bar = False
        while threading.activeCount() > 1:
            time.sleep(0.3)
        print "[+] All accounts have been verified!"

        sys.stdout.write("[+] Writing accounts ot %s, " % output_path)
        sys.stdout.flush()
        save_credentials(credentials)
        print "Done"

        print "-" * 60
        raw_input("[+] Press enter to exit...")

    except KeyboardInterrupt:
        show_bar = False
        print
    except:
        show_bar = False
        import traceback
        traceback.print_exc()