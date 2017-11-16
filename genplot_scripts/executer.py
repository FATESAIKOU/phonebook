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
import json
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
    if mu < 0:
        return db[:db_size]

    new_db = []
    sigma = round(mu / 2)
    gr = lambda u, s: int(round(np.random.normal(u, s, 1)[0]))

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
    data['cache-miss-rate'] = data['cache-misses'] * 100.0 / data['cache-references']

    append_times = re.findall('append\(\) : (.+?) sec', outputs)
    data['append-avg'] = sum([float(f) for f in append_times]) / times

    findname_times = re.findall('findName\(\) : (.+?) sec', outputs)
    data['findname-avg'] = sum([float(f) for f in findname_times]) / times

    encode_times = re.findall('encode\(\) : (.+?) sec', outputs)
    data['encode-avg'] = sum([float(f) for f in encode_times]) / times

    collision_count = re.findall('collision : (.+?)', outputs)
    data['collision'] = sum([int(c) for c in collision_count]) / times

    return data


def dumpData(data, db_description, dump_file):
    packed_data = {
        'cache-misses': [],
        'cache-references': [],
        'cache-miss-rate': [],
        'append-avg': [],
        'findname-avg': [],
        'encode-avg': [],
        'collision': []
    }

    for (db_size, mu) in data.keys():
        record = data[(db_size, mu)]
        for col in record.keys():
            packed_data[col].append([db_size, mu, record[col]])

    packed_db_description = [[i, db_description[i]] for i in db_description.keys()]


    packed_result = {
        "data": packed_data,
        "db": packed_db_description
    }

    src = open(dump_file, 'w')
    src.write(json.dumps(packed_result))
    src.close()


def perf(db, phonebook, mode, prime_list):
    n_db_size = 100
    result = {}
    tmp_db_name = "dictionary/tmp.txt"
    exe_command = "perf stat -e cache-misses,cache-references,instructions,cycles --repeat 20 ./" + phonebook + " " + tmp_db_name


    if mode == 'Performance':
        j_iterator = xrange(1, 10)
    elif mode == 'Hash':
        j_iterator = prime_list[:20]


    while True:
        if n_db_size > len(db):
            break

        for j in j_iterator:
            if mode == 'Performance':
                print "Size:", n_db_size, "Mu:", j, "Sigma:", round(j / 2)
                n_db = genDB(db, n_db_size, j)
                real_exe_command = exe_command
            elif mode == 'Hash':
                print "Size:", n_db_size, "Hashsize:", j
                n_db = genDB(db, n_db_size, j)
                real_exe_command = exe_command + ' ' + str(j)

            dumpDB(n_db, tmp_db_name)
            outputs = os.popen(real_exe_command + " 2>&1").read()

            result[(n_db_size, j)] = collectData(outputs, 20)
            pprint(result[(n_db_size, j)])

            os.remove(tmp_db_name)

        n_db_size = int(n_db_size * 2)

    return result


def main():
    mode      = sys.argv[1]
    phonebook = sys.argv[2]
    text_file = sys.argv[3]
    hash_list_file = sys.argv[4]

    db = loadDB(text_file)
    db_description = describeDB(db)

    if mode == 'Performance':
        result = perf(db, phonebook, mode)
    elif mode == 'Hash':
        src = open(hash_list_file)
        prime_nums = json.loads(src.read())
        src.close()
        result = perf(db, phonebook, mode, prime_nums)

    dumpData(result, db_description, 'output.json')


if __name__ == "__main__":
    main()


