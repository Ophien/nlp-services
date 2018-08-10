### Basic summarizer to directly use untokenized text. Since apparently that's too hard to provide as an example.
import subprocess
import os
import argparse
import sys

sys.path.insert(0, './text-summarization/opennmt-py')

import torch
from onmt.translate.translator import build_translator
import onmt.opts

def stanford_tokenizer(text):
    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer', '-preserveLines']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    out = p.communicate(input=text.encode())[0]
    return out.decode()

def summary(tokenized):
    parser = argparse.ArgumentParser()
    onmt.opts.translate_opts(parser)

    prec_argv = sys.argv
    sys.argv = sys.argv[:1]

    opt = {
        'batch_size': 1,
        'beam_size': 15,
        'min_length': 35,
        'verbose': True,
        'stepwise_penalty': True,
        'coverage_penalty': 'summary',
        'beta': 5,
        'length_penalty': 'wu',
        'alpha': 0.9,
        'verbose': True, 
        'block_ngram_repeat': 3,
        'ignore_when_blocking': "." "</t>" "<t>",
        'replace_unk': True,
        'gpu': 0
    }
    opt['model'] = os.path.join('text-summarization/models/sum_transformer_model_acc_57.25_ppl_9.22_e16.pt')
    opt['src'] = "dummy_src"

    for (k, v) in opt.items():
        if type(v) == bool:
            sys.argv += ['-%s' % k]
        else:
            sys.argv += ['-%s' % k, str(v)]

    opt = parser.parse_args()
    opt.cuda = opt.gpu > -1
    sys.argv = prec_argv

    translator = build_translator(opt, report_score=False, out_file=open(os.devnull, "w"))

    scores = []
    predictions = []
    print("translating...")
    scores, predictions = translator.translate(src_data_iter=[tokenized], batch_size=1)
    print("done translating")
    for s, p in zip(scores, predictions):
        print(s, p[0].replace('<t> ', '').replace('</t>', ''))

if __name__ == "__main__":
    text = """Senior National MP Judith Collins is standing by her tweet of a fake news story because she says "the body" of the article is true.
Despite party leader Simon Bridges saying she had got her "sourcing" wrong, Collins refused to describe the article as fake on Tuesday morning, insisting it simply had some details wrong.
The article, which claimed France was abandoning age-based sex laws when it is in fact strengthening them, came from a website that has featured other false stories - including one on pop singer Katy Perry purportedly endorsing cannibalism and another reporting the FBI had admitted "aliens from other dimensions" had visited New Zealand. It has been cited as a fake news website several times.
Collins tweeted out the story on Monday and challenged Prime Minister Jacinda Ardern to repudiate France over the law change.
"Some of the information is correct, and some not quite, but plenty of other stories [in publications] like The Independent, The Guardian, The Washington Post, and The Daily Telegraph have run similar stories on the same thing, " Collins said.
Sign up for our weekly politics newsletter: Politically Correct
While there are stories covering the law change in other outlets, they do not suggest that France was actively loosening its laws or that liberal activists trying to normalise paedophilia were behind it.
The YourNewsWire article Collins posted to Twitter claimed in its opening paragraph that France was loosening its child sex laws "to give in to pressure from an international network of liberal activists determined to normalise paedophilia and decriminalise sex with children across the world."
France is actually strengthening its laws around sex with minors, and making it easier to prosecute adults who have sex with children under 15 years old with rape. There is no "abandonment" of an age of consent as reported in the article - France, like New Zealand, has a legal age whereby any adult who has sex with a child under that age is committing an offence, but not necessarily "rape".
Legislators in France had considered further strengthening this law but had been warned it might be unconstitutional - a result that has sparked backlash from some corners of French society.
"I thought it was an interesting story. I don't censor everything that I retweet, and I retweet lots of things," Collins said.
She would not clarify whether or not she had read the whole article before tweeting it out.
"Just because I retweet, doesn't mean to say its an endorsement," Collins said. (Collins did not retweet the article - she tweeted it herself.) 
"I don't believe in censorship based on people's ideas," Collins said.
"It's not necessarily the source that I'd choose again. But having said that the sentiment around paedophilia and just how dangerous it is is something I stand by."
Collins said she didn't call people out for "fake news" herself.
"I've never used the term to people and I've never used it about websites."
Collins called a Newshub story "total fake news" on Twitter in February.
Asked if she had discussed the tweet with party leader Bridges, Collins said no. Bridges, speaking at the same time to reporters around the National Party caucus corridor, said he had talked to Collins about the issue.
Bridges later clarified that Collins believed media had asked her if she had been told off by Bridges, not if she had talked to him about it at all.
Collins rejected any notion that she had tweeted the most inflammatory version of an article on the topic to make a point.
"I can be very inflammatory all by myself."
"""
    tokens = stanford_tokenizer(text)
    summary(tokens)