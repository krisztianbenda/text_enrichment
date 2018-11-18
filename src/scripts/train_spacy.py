import spacy
import pandas as pd
import numpy as np
from spacy.util import minibatch, compounding
import random 
import argparse
import os
from tqdm import tqdm

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


def add_SenteceID(df):
    for index, row in df.iterrows():
        if str(row['Sentence #']) != 'nan':
            current_sentence = int(row['Sentence #'].split(' ')[1])
        df.loc[index, 'SentenceID'] = current_sentence
        if index > 1 and index % 50000 == 0:
            print('\t'+ str(index)+ ' ID were added...')
    df.loc[len(df.index), 'Sentence #'] = 'Sentence ' + str(df.loc[len(df.index) - 1, 'SentenceID'] + 1)
    df.loc[len(df.index) - 1, 'SentenceID'] = df.loc[len(df.index) - 2, 'SentenceID'] + 1
    return df

def get_sentence(df, id):
    indexes = df[df['Sentence #'].isnull() == False].index.values.tolist()
    indexes.append(df.shape[0]-1)
    start = indexes[id]
    end = indexes[id+1]
    words = df[(df.index >= start) & (df.index < end)]['Word'].values.tolist()
    return ' '.join(str(word) for word in words)

def get_sentence_entities(df, sentence):
    entities = {'entities': None}
    entity = []
    for word in sentence.split(' '):
        entity.append((sentence.find(word), sentence.find(word)+len(word), str(df[df['Word'] == word]['Tag'].iloc[0])))
    entities['entities'] = entity
    return entities

def get_acc(df):
    tp = df.loc[(df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    return tp / (df[df['is_trained'] == False].shape[0]-1) * 100

def get_recall(df):
    tp = df.loc[(df['Tag'] != 'O') & (df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    tp_fn = df.loc[(df['Tag'] != 'O') & (df['is_trained'] == False)].shape[0] - 1
    return tp / tp_fn * 100

def get_precision(df):
    tp = df.loc[(df['Tag'] != 'O') & (df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    tp_fp = df.loc[(df['Prediction'] != 'O') & (df['is_trained'] == False)].shape[0] - 1
    return tp / tp_fp * 100

def create_train_data(df, sample_num):
    n = len(df[df['Sentence #'].isnull() == False].index.values.tolist())
    rands = random.sample(np.arange(n).tolist(), sample_num)
    # rands = [int(x.split(' ')[1])+1 for x in rands]
    train_data = []
    counter = 0
    for num in rands:
        sent = get_sentence(df, num)
        entities = get_sentence_entities(df, sent)
        train_data.append((sent, entities))
        counter += 1
        if counter % 100 == 0:
            print(str(counter) + " training data have created\n")
    return train_data, rands

def main():
    global IT_N, SEN_N, OUT_FILE
    args = parser.parse_args()
    SEN_N = args.sentence_number
    IT_N = args.iteration_number
    OUT_FILE = args.output_file
    print('sentence num: ' + str(SEN_N)+ ' iteration num: ' + str(IT_N) + ' output: ' + OUT_FILE)

    base_df = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'TrainNER.csv'), delimiter=';', encoding='cp1252')
    print('TrainNER.csv has read...')
    # base_df = add_SenteceID(base_df)
    # print('SentenceIDs has added to the Data Frame...')
    train_data, train_ids = create_train_data(base_df, SEN_N)
    print('Train data has been created...')

    nlp = spacy.blank('en')
    ner = nlp.create_pipe('ner')
    nlp.add_pipe(ner, last=True)

    # nlp.to_disk('./model')
    # nlp = spacy.load('./model')

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
            print(str(itn) + ' iteration with ' + str(losses))

    print("===========\nTraining is finished.\n===========\nStarting evaluation for the rest of the sentences.")
    

    indexes = base_df[base_df['Sentence #'].isnull() == False].index.values.tolist()
    indexes.append(base_df.shape[0]-1)

    base_df['Prediction'] = "O"
    for k in tqdm(range(len(indexes)-1)):
    # for k in tqdm(range(500)):
        is_trained = k in train_ids
        start = indexes[k]
        end = indexes[k+1]
        init_tokens = base_df[(base_df.index >= start) & (base_df.index < end)]['Word'].values.tolist()
        s = ' '.join(init_tokens)
        doc = nlp(s)
        ents = []
        for ent in doc.ents:
            ents.append([ent.text, ent.label_])
        i = 0
        for j in range(len(init_tokens)):
            if i < len(ents) and init_tokens[j] == ents[i][0]:
                base_df.loc[base_df.index == start+j, 'Prediction'] = ents[i][1]
                i += 1
            # base_df.loc[base_df.index == start+j, 'SentenceID'] = k
            base_df.loc[base_df.index == start+j, 'is_trained'] = is_trained
        # df[(df.index >= start) & (df.index < end)]




    # predicted_df = base_df
    # sentenceID = 0
    # doc = nlp(get_sentence(predicted_df, sentenceID))
    # is_train_data = False
    # for index, row in predicted_df.iterrows():
    #     if sentenceID != row['SentenceID']:
    #         is_train_data = False
    #         sentenceID = row['SentenceID']
    #         sentence = get_sentence(predicted_df, sentenceID)
    #         doc = nlp(sentence)
    #         for data in train_data:
    #             if sentence == data[0]:
    #                 is_train_data = True
    #                 break

    #     #If nlp does not find a class for word we set it 'O' because it is the most likely
    #     predicted_df.loc[index,'Prediction'] = 'O'
    #     #If there is a valid predicted class we change O
    #     for ent in doc.ents:
    #         if row['Word'] == str(ent):
    #             predicted_df.loc[index,'Prediction'] = ent.label_
    #             break

    #     predicted_df.loc[index, 'is_trained'] = is_train_data
    #     if index % 10000 == 0:
    #         print('\t' + str(index) + ' rows predicted')

    predicted_df = base_df

    predicted_df.to_csv(OUT_FILE, sep=';')
    print('==============')
    print("Acc: " + str(get_acc(predicted_df)))
    print("Recall: " + str(get_recall(predicted_df)))
    print("Precision: " + str(get_precision(predicted_df)))
    print('==============')

if __name__ == '__main__':
    main()

