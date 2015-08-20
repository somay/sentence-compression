import sys, pickle
from argparse import ArgumentParser, FileType
from subprocess import Popen, PIPE

import compress

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--lm', '-l', type=FileType('rb'), required=True, help='a pickle file of trigram language model')
    parser.add_argument('--start', '-s', type=FileType('rb'), required=True, help='a pickle file of start-of-sentence probabilities')
    args = parser.parse_args()

    start_prob = pickle.load(args.start)
    lm = pickle.load(args.lm)

    print('language models have been loaded.')

    juman_prc = Popen(('juman', '-b'), stdin=PIPE, stdout=PIPE, universal_newlines=True)

    for line in sys.stdin:
        juman_prc.stdin.write(line)

        sentence = []
        for mrph in juman_prc.stdout:
            if mrph == 'EOS\n':
                break
            sentence.append(mrph.split(' ')[0])
        
        compressed = compress.compress(sentence, start_prob, lm)
        print(''.join(compressed))
