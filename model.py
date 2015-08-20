import sys, pickle, gc
from collections import defaultdict
from argparse import ArgumentParser, FileType

def count2probability(d): # type of d is dict whose value's type is int
    sum_count = 0
    for key in d:
        sum_count += d[key]
    for key in d:
        d[key] = d[key] / sum_count
    return 

def dump_count_and_probability(start_count, lm, start_count_file, lm_file):
    count2probability(start_count)
    for key in lm:
        count2probability(lm[key])

    pickle.dump(start_count, start_count_file)
    pickle.dump(lm, lm_file)
    return
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--lm', '-l', type=FileType('wb'), required=True, help='a file to store trigram language model in pickle format')
    parser.add_argument('--start', '-s', type=FileType('wb'), required=True, help='a file to store start-of-sentence probabilities in pickle format')

    args = parser.parse_args()

    print('You must use Ctrl-C when you are short of memory and want to stop computing', file=sys.stderr)
    
    start_count = defaultdict(int)
    trigrams_once = set()
    trigrams_more_than_twice = set()
    lm = dict(defaultdict(int))

    num_sentences = 0

    try:
        for sentence in sys.stdin:
            mrphs = sentence.rstrip().split(' ')
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


            if num_sentences % 10000 == 0:
                print(num_sentences, "sentences were processed,", len(trigrams_more_than_twice), 'trigrams are in current language model, and', len(trigrams_once), 'trigrams were appeared only once')
                if len(trigrams_once) > 2**23:   # if more than 8M trigrams
                    print('trigrams which were appeared only once, were flushed')
                    trigrams_once = set()
                    gc.collect()



    except KeyboardInterrupt:
        del trigrams_once
        print(len(trigrams_more_than_twice), 'trigrams are in this language model')
        del trigrams_more_than_twice
        dump_count_and_probability(start_count, lm, args.start, args.lm)
        sys.exit(0)

    del trigrams_once
    print(len(trigrams_more_than_twice), 'trigrams are in this language model')
    del trigrams_more_than_twice
    dump_count_and_probability(start_count, lm, args.start, args.lm)
