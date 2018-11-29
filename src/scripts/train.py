import spacy
from spacy.scorer import Scorer
from spacy.gold import GoldParse
import pandas as pd
from spacy.util import minibatch, compounding
import random 
import argparse
import os
from tqdm import tqdm
import simplejson as json

IT_N = 100
SEN_N = 500
OUT_FILE = os.path.join(os.getcwd(), 'datasets', 'TrainingPrediction.csv')
parser = argparse.ArgumentParser(prog='Train SpaCy', 
    description="This script can train a blank eng SpaCy model with a custom iteration on given number of sentences")
parser.add_argument('-i', '--iteration_number', type=int, default=IT_N,
                    help='Say how many iteration you would like to train the SpaCy. Default is: {}'.format(IT_N))
parser.add_argument('-s', '--sentence_number', type=int, default=SEN_N, 
                    help='Say how many sentence you would like to use on training. Max is 9000, but default is: {}'.format(SEN_N))
parser.add_argument('-o', '--output_file', type=str, default=OUT_FILE,
                    help='Where do you want to store your results. Default is: {}'.format(OUT_FILE))


def get_data(trainf, testf):
    with open(trainf, 'r') as f:
        traind = json.load(f)
    with open(testf, 'r') as f:
        testd = json.load(f)
    return (traind, testd)

def evaluate(ner_model, examples):
    scorer = Scorer()
    for input_, annot in examples:
        doc_gold_text = ner_model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot.get('entities'))
        pred_value = ner_model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores

def main():
    global IT_N, SEN_N, OUT_FILE
    args = parser.parse_args()
    SEN_N = args.sentence_number
    IT_N = args.iteration_number
    OUT_FILE = args.output_file
    print('sentence num: ' + str(SEN_N)+ ' iteration num: ' + str(IT_N) + ' output: ' + OUT_FILE)

    train_data, test_data = get_data("train_data.json", "test_data.json")

    nlp = spacy.blank('en')
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

    for _, annotations in train_data:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for itn in range(IT_N):
            random.shuffle(train_data)
            losses = {}
            
            batches = minibatch(train_data, size=compounding(4., 32., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,
                    annotations,
                    drop=0.5,
                    sgd=optimizer,
                    losses=losses
                )
            if(itn % 50 == 0):
                print(str(itn) + ' iteration with ' + str(losses))
                scores = evaluate(nlp,test_data)
                print(scores)
                nlp.to_disk(OUT_FILE)

                # print("Accuracy {:0.4f}\tRight {:0.0f}\tWrong {:0.0f}\tUnknown {:0.0f}\tEntities {:0.0f}".format(scores['acc'], scores['right'],scores['wrong'],scores['unk'],scores['ents']))


    print(evaluate(nlp,test_data))
    nlp.to_disk(OUT_FILE)

if __name__ == '__main__':
    main()

