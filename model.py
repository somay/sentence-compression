import sys, pickle
from collections import defaultdict


def count2probability(d): # type of d is dict whose value's type is int
    sum_count = 0
    for key in d:
        sum_count += d[key]
    for key in d:
        d[key] = d[key] / sum_count
    return 

def dump_count_and_probability(start_count, lm, dump_count=False):
    if dump_count:
        with open('start-mrphs-count.pickle', 'wb') as s, open('trigram-count.pickle', 'wb') as t:
            pickle.dump(start_count, s)
            pickle.dump(lm, t)

    count2probability(start_count)
    for key in lm:
        count2probability(lm[key])

    with open('start-mrphs-probability.pickle', 'wb') as s, open('trigram-model.pickle', 'wb') as t:
        pickle.dump(start_count, s)
        pickle.dump(lm, t)
    return
    

if __name__ == '__main__':
    start_count = defaultdict(int)
    trigrams_once = set()
    trigrams_more_than_twice = set()
    lm = dict(defaultdict(int))

    num_sentences = 0

    try:
        for sentence in sys.stdin:
            mrphs = sentence.split(' ')
            start_count[mrphs[0]] += 1

            for i in range(len(mrphs) - 2):
                ms = (mrphs[i], mrphs[i+1], mrphs[i+2])
                if ms in trigrams_more_than_twice:
                    lm[(mrphs[i], mrphs[i+1])][mrphs[i+2]] += 1
                elif ms in trigrams_once:
                    key = (mrphs[i], mrphs[i+1])
                    if key in lm:
                        lm[key][mrphs[i+2]] = 2
                    else:
                        lm[key] = defaultdict(int)
                        lm[key][mrphs[i+2]] = 2
    
                    trigrams_once.discard(ms)
                    trigrams_more_than_twice.add(ms)
                else:
                    trigrams_once.add(ms)

            num_sentences += 1

            if len(trigrams_once) > 2**25:   # if more than 32M trigrams
                trigrams_once = set()
                print('trigram appeared once have been flushed')

            if num_sentences % 10000 == 0:
                print(num_sentences, "sentences were processed, and", len(trigrams_more_than_twice), 'trigrams are in current language model')


    except KeyboardInterrupt:
        del trigrams_once
        print(len(trigrams_more_than_twice), 'trigrams are in this language model')
        del trigrams_more_than_twice
        dump_count_and_probability(start_count, lm)
        sys.exit(0)

    del trigrams_once
    print(len(trigrams_more_than_twice), 'trigrams are in this language model')
    del trigrams_more_than_twice
    dump_count_and_probability(start_count, lm)
