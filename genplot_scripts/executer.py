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
import re
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


def collectData(outputs, times):
    data = {}
    data['cache-misses'] = int(re.search('(.+?)cache-misses', outputs).group(1).replace(',', ''))
    data['cache-references'] = int(re.search('(.+?)cache-references', outputs).group(1).replace(',', ''))
    data['cache-miss-rate'] = str(data['cache-misses'] * 100.0 / data['cache-references']) + '%'

    append_times = re.findall('append\(\) : (.+?) sec', outputs)
    data['append_avg'] = sum([float(f) for f in append_times]) / times

    findname_times = re.findall('findName\(\) : (.+?) sec', outputs)
    data['findname_avg'] = sum([float(f) for f in findname_times]) / times

    encode_times = re.findall('encode\(\) : (.+?) sec', outputs)
    data['encode_avg'] = sum([float(f) for f in encode_times]) / times

    collision_count = re.findall('collision : (.+?)', outputs)
    data['collision'] = sum([int(c) for c in collision_count]) / times

    return data

def main():
    mode      = sys.argv[1]
    phonebook = sys.argv[2]
    text_file = sys.argv[3]


    db = loadDB(text_file)
    pprint(describeDB(db))

    n_db_size = 100
    while True:
        if n_db_size > len(db):
            break

        for j in xrange(1, 10):
            print "Size:", n_db_size, "Mu:", j, "Sigma:", round(j / 2)
            n_db = genDB(db, n_db_size, j)

            filename = "dictionary/" + str(n_db_size) + "-" + str(j) + ".txt"
            dumpDB(n_db, filename)
            outputs = os.popen("perf stat -e cache-misses,cache-references,instructions,cycles --repeat 20 ./" + phonebook + " " + filename + " 2>&1").read()

            pprint(collectData(outputs, 20))
            os.remove(filename)


        n_db_size = int(n_db_size * 1.05)
        

if __name__ == "__main__":
    main()
