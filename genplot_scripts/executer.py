"""
This program will execute provided Phonebook program, and profile its
performance with provided text file, then restore the result.

@argv[1]: profile mode, "Hash" for hash, "Performance" for default
@argv[2]: the file to be executed
@argv[3]: text file to be loaded by provided program
@argv[4]: maximum hash table size (this arg wouldn't be vaild until "Hash" is set)

@Auth: FATESAIKOU
"""

import sys
import os
import numpy as np

from pprint import pprint

def loadDB(filename):
    db = []

    src = open(filename, 'r')
    while True:
        name = src.readline().rstrip()
        
        if not name:
            break
        
        db.append(name)

    src.close()

    db.sort(lambda a, b: len(b) - len(a))

    return db;

def describeDB(db):
    counter = {}

    for n in db:
        n_len = len(n)
        counter[n_len] = counter[n_len] + 1 \
                if n_len in counter.keys() else 1

    return counter


def genDB(db, db_size, mu):
    sigma = round(mu / 2)
    gr = lambda u, s: int(round(np.random.normal(u, s, 1)[0]))

    new_db = []
    for i in xrange(db_size):
        new_len = gr(mu, sigma)
        new_len = 1 if new_len == 0 else new_len

        new_string = db[i][:new_len]
        new_string.ljust(new_len, '-')
        
        new_db.append(new_string)

    return new_db


def dumpDB(db, filename):
    src = open(filename, 'w')
    src.write("\n".join(db))
    src.close()


def main():
    db = loadDB(sys.argv[1])
    pprint(describeDB(db))

    n_db_size = 100
    while True:
        if n_db_size > len(db):
            break

        for j in xrange(1, 10):
            print "Size:", n_db_size, "Len:", j
            n_db = genDB(db, n_db_size, j)

            filename = "dictionary/" + str(n_db_size) + "-" + str(j) + ".txt"
            dumpDB(n_db, filename)
            os.remove(filename)


        n_db_size = int(n_db_size * 1.05)
        

if __name__ == "__main__":
    main()
