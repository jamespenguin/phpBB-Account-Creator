#!/usr/bin/env python
#
# phpBB Account Creation Framework
#
import random, os, time, getpass
from Tkinter import *
import Image, ImageTk
import requests
import urlparse
import BeautifulSoup
import form_processor
import decaptcher

###
# Config
###
images_path = "captchas"
adjectives_path = "adjectives.txt"
nouns_path = "nouns.txt"

# Decaptcher Stuff
dc_username = "" # To enable decaptcher, just put in your username and password here
dc_password = ""

# Print DC balance
if dc_username:
    d = decaptcher.decaptcher(dc_username, dc_password)
    print "[+] Decaptcher balance is $%.2f" % d.get_balance()
    print

#!# End Config #!#

def random_sequence(length):
    chars = map(chr, range(48, 58) + range(97, 123))
    big_chars = map(chr, range(65, 91))
    return "".join(map(lambda x: random.choice(chars), range(length))) + random.choice(big_chars)

def random_noun():
    nouns = open(nouns_path, "r").read().split("\n")
    return random.choice(nouns)

def random_adjective():
    adjectives = open(adjectives_path, "r").read().split("\n")
    return random.choice(adjectives)

def random_username():
    adjective = random_adjective()
    noun = random_noun().title()
    return "%s%s%d" % (adjective, noun, random.randint(2000, 2100))

class phpBB:
    def __init__(self):
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008092215 Firefox/3.0.1"}
        self.__session = requests.session(headers=headers)

    def __get_captcha_answer_from_GUI(self, image_file_path):
        def destroy_window(event):
            root.destroy()

        root = Tk()
        root.title("Enter the answer to the CAPTCHA below!")

        image_file = Image.open(image_file_path)
        photo_image = ImageTk.PhotoImage(image_file)
        label_image = Label(root, image=photo_image).pack(pady=5, padx=7)

        Label(root, text="Answer", justify=CENTER).pack()
        answer = StringVar(root)
        answer_input = Entry(root, textvariable=answer, justify=CENTER, width=30)
        answer_input.bind("<Return>", destroy_window)
        answer_input.focus_set()
        answer_input.pack(pady=5)

        go_button = Button(root, text="Go!", padx=60, command=root.destroy)
        go_button.pack(pady=5)

        root.attributes("-topmost", True)
        root.focus_set()
        root.mainloop()
        return answer.get()

    def __get_captcha_answer(self, referer_url, page):
        soup = BeautifulSoup.BeautifulSoup(page)
        for tag in soup.findAll("img"):
            if "mode=confirm" not in tag["src"]:
                continue
            image_url = tag["src"]
            if not image_url.startswith("http"):
                image_url = urlparse.urljoin(referer_url, image_url)

        image_file_name = "%s.jpg" % random_sequence(10)
        image_file_path = os.path.join(images_path, image_file_name)
        if not os.path.exists(images_path):
            os.mkdir(images_path)

        image_data = self.__session.get(image_url).content
        image_file = open(image_file_path, "wb")
        image_file.write(image_data)
        image_file.close()

        if dc_username:
            d = decaptcher.decaptcher("jamespenguin", dc_password)
            captcha_answer = d.solve_image(image_file_path)
        else:
            captcha_answer = self.__get_captcha_answer_from_GUI(image_file_path)            
        os.remove(image_file_path)

        return captcha_answer

    def verify_email(self, username):
        email_link = "http://%s.spam.su/" % username
        page = self.__session.get(email_link)
        soup = BeautifulSoup.BeautifulSoup(page.content)
        for tag in soup.findAll("a"):
            if not tag.has_key("href") or "?msgId=" not in tag["href"]:
                continue
            message_link = tag["href"]
            message_link = urlparse.urljoin(email_link, message_link)

        message_page = self.__session.get(message_link)
        soup = BeautifulSoup.BeautifulSoup(message_page.content)
        for tag in soup.findAll("a"):
            if not tag.has_key("href") or "mode=activate" not in tag["href"]:
                continue
            activation_link = tag["href"]
        activation_page = self.__session.get(activation_link)

    def create_account(self, start_url):
        username = random_username()
        email = "%s@spam.su" % username
        password = random_sequence(10)

        # Tell the forum we agree to their terms.
        start_page = self.__session.get(start_url)
        forms = form_processor.parse_forms(start_url, start_page.content)
        form = forms[-1]
        form_action = form["action"]
        referer = form_action
        form_data = form["inputs"]
        del form_data["not_agreed"]
        request = self.__session.post(form_action, form_data)

        # Process the registration form
        forms = form_processor.parse_forms(form_action, request.content)
        form = forms[-1]
        form_action = form["action"]
        form_data = form["inputs"]

        del form_data["reset"]
        form_data["username"] = username
        form_data["email"] = email
        form_data["email_confirm"] = email
        form_data["new_password"] = password
        form_data["password_confirm"] = password
        form_data["tz"] = random.choice(form_data["tz"])
        form_data["lang"] = random.choice(form_data["lang"])
        form_data["confirm_code"] = self.__get_captcha_answer(form_action, request.content)

        if not form_data["confirm_code"]:
            return self.create_account(start_url)
        else:
            # Sleep for a bit so that we don't tick off the register script
            time.sleep(10)
            # Send the request
            register_request = self.__session.request("POST", form_action, data=form_data,
                                                      headers={"Referer": referer})
            output_page = open("result.html", "w")
            output_page.write(register_request.content)
            output_page.close()
            if "confirmation code" in register_request.content:
                return False
            return username, password

if __name__ == '__main__':
    p = phpBB()
    print p.create_account("http://www.ilovephilosophy.com/ucp.php?mode=register")
    #p.verify_email("moaningHorses2036")