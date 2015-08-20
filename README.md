## What's this

Python3で書かれた日本語用の文短縮アルゴリズムです。
アルゴリズムとして	Global Inference for Sentence Compression An Integer Linear Programming Approach (James Clarke, Mirella Lapata, 2008)で提案されている１つめのアルゴリズムを使いました。
ただしまだ実装途中で現状ではおよそ文とは言えない短縮文しか出力しません…

日本語形態素解析器JUMANと線形計画問題ソルバーのPython用インターフェースpulpに依存しています。

http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN
https://pypi.python.org/pypi/PuLP


## Usage

main.py: 標準入力から入力文を受け取り標準出力に短縮文を出力するスクリプト
usag: python3 main.py --lm trigram.pickle --start start-mrphs.pickle 

model.sh: プレーンテキストの文章からcompress.py向けの言語モデルを生成するシェルスクリプト
usage: ./model.sh trigram.pickle start-mrphs.pickle

## TODO

* 整数計画問題の言語的成約を追加
* SRILMへの移行
