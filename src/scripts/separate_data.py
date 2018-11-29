import spacy
import pandas as pd
import numpy as np
from spacy.util import minibatch, compounding
import random 
import argparse
import os
from tqdm import tqdm
import simplejson as json

OUT_FILE = os.path.join(os.getcwd(), 'datasets', 'all.json')
parser = argparse.ArgumentParser(prog='Train SpaCy', 
    description="This script can train a blank eng SpaCy model with a custom iteration on given number of sentences")
parser.add_argument('-o', '--output_file', type=str, default=OUT_FILE,
                    help='Where do you want to store your results. Default is: {}'.format(OUT_FILE))


def get_sentence_d(df, id, start, end):
    words = df[(df.index >= start) & (df.index < end)]['Word'].values.tolist()
    return ' '.join(str(word) for word in words)

def get_sentence_entities_n_o(df, sentence):
    entities = {'entities': None}
    entity = []
    for word in sentence.split(' '):
        if str(df[df['Word'] == word]['Tag'].iloc[0]) != 'O':
            entity.append((sentence.find(word), sentence.find(word)+len(word), str(df[df['Word'] == word]['Tag'].iloc[0])))
    entities['entities'] = entity
    return entities

def create_s_data(df):
    n = len(df[df['Sentence #'].isnull() == False].index.values.tolist())
    print(n)
    s_data = [None] * n
    counter = 0
    indexes = df[df['Sentence #'].isnull() == False].index.values.tolist()
    indexes.append(df.shape[0]-1)
    for num in tqdm(range(n)):
        start = indexes[num]
        end = indexes[num+1]
        sent = get_sentence_d(df, num, start, end)
        entities = get_sentence_entities_n_o(df, sent)
        s_data[counter] = (sent, entities)
        counter += 1
    return s_data

def dump_to_json(data_, filename):
    with open(filename, 'w') as f:
        json.dump(data_, f)

def main():
    global OUT_FILE
    args = parser.parse_args()
    OUT_FILE = args.output_file

    base_df = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'TrainNER.csv'), delimiter=';', encoding='cp1252')
    print('TrainNER.csv has read...')
    
    dump_to_json(create_s_data(base_df), OUT_FILE)

if __name__ == '__main__':
    main()

