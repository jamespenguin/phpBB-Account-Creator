#!/usr/bin/env python
#
# Generate Username - Unique, realistic looking usernames on the fly!
# By James Penguin (brandon.smith@studiobebop.net)
#
import random

def random_noun():
    nouns = open("nouns.txt", "r").read().split("\n")
    return random.choice(nouns)

def random_adjective():
    adjectives = open("adjectives.txt", "r").read().split("\n")
    return random.choice(adjectives)

def random_username():
    adjective = random_adjective()
    noun = random_noun().title()
    return "%s%s%d" % (adjective, noun, random.randint(2000, 2100))

if __name__ == '__main__':
    print random_username()