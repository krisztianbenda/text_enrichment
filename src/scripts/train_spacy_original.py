import spacy
import pandas as pd
from spacy.util import minibatch, compounding
import random
import argparse
import os

IT_N = 100
SEN_N = 500
OUT_FILE = os.path.join(os.getcwd(), 'datasets', 'TrainingPrediction.csv')
GENERATE_SENTENCE_ID = False
parser = argparse.ArgumentParser(prog='Train SpaCy',
                                 description="This script can train a blank eng SpaCy model with a custom iteration on given number of sentences")
parser.add_argument('-i', '--iteration_number', type=int, default=IT_N,
                    help='Say how many iteration you would like to train the SpaCy. Default is: {}'.format(IT_N))
parser.add_argument('-s', '--sentence_number', type=int, default=SEN_N,
                    help='Say how many sentence you would like to use on training. Max is 9000, but default is: {}'.format(
                        SEN_N))
parser.add_argument('-o', '--output_file', type=str, default=OUT_FILE,
                    help='Where do you want to store your results. Default is: {}'.format(OUT_FILE))
parser.add_argument('-g', '--generate', type=bool, default=GENERATE_SENTENCE_ID,
                    help='In the case of true, the script regenerate sentence ids from TrainNER.csv. Default is: {}'.format(
                        GENERATE_SENTENCE_ID))


def add_SenteceID(df):
    for index, row in df.iterrows():
        if str(row['Sentence #']) != 'nan':
            current_sentence = int(row['Sentence #'].split(' ')[1])
        df.loc[index, 'SentenceID'] = current_sentence
        if index > 1 and index % 50000 == 0:
            print('\t' + str(index) + ' ID were added...')
    df.loc[len(df.index), 'Sentence #'] = 'Sentence ' + str(df.loc[len(df.index) - 1, 'SentenceID'] + 1)
    df.loc[len(df.index) - 1, 'SentenceID'] = df.loc[len(df.index) - 2, 'SentenceID'] + 1
    return df


def get_sentence(df, id):
    words = df[(df['SentenceID'] == id)]['Word'].values.tolist()
    return ' '.join(str(word) for word in words)


def get_sentence_entities(df, sentence):
    entities = {'entities': None}
    entity = []
    for word in sentence.split(' '):
        entity.append(
            (sentence.find(word), sentence.find(word) + len(word), str(df[df['Word'] == word]['Tag'].iloc[0])))
    entities['entities'] = entity
    return entities


def get_acc(df):
    tp = df.loc[(df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    return tp / (df[df['is_trained'] == False].shape[0] - 1) * 100


def get_recall(df):
    tp = df.loc[(df['Tag'] != 'O') & (df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    tp_fn = df.loc[(df['Tag'] != 'O') & (df['is_trained'] == False)].shape[0] - 1
    return tp / tp_fn * 100


def get_precision(df):
    tp = df.loc[(df['Tag'] != 'O') & (df['Tag'] == df['Prediction']) & (df['is_trained'] == False)].shape[0]
    tp_fp = df.loc[(df['Prediction'] != 'O') & (df['is_trained'] == False)].shape[0] - 1
    return tp / tp_fp * 1


def create_train_data(df, sample_num):
    rands = random.sample(df['Sentence #'].unique().tolist(), sample_num)
    rands = [int(x.split(' ')[1]) + 1 for x in rands]
    train_data = []
    counter = 0
    for num in rands:
        sent = get_sentence(df, num)
        entities = get_sentence_entities(df, sent)
        train_data.append((sent, entities))
        counter += 1
        if counter % 100 == 0:
            print(str(counter) + " training data have created")
    return train_data


def main():
    global IT_N, SEN_N, OUT_FILE, GENERATE_SENTENCE_ID
    args = parser.parse_args()
    SEN_N = args.sentence_number
    IT_N = args.iteration_number
    OUT_FILE = args.output_file
    GENERATE_SENTENCE_ID = args.generate
    print('sentence num: ' + str(SEN_N) + ' iteration num: ' + str(IT_N) + ' output: ' + OUT_FILE)

    if GENERATE_SENTENCE_ID:
        base_df = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'TrainNER.csv'), delimiter=';', encoding='cp1252')
        print('TrainNER.csv was read.')
        base_df = add_SenteceID(base_df)
        print('SentenceIDs were added to the Data Frame.')
        base_df.to_csv(os.path.join(os.getcwd(), 'datasets', 'TrainNER_sentenceID.csv'), sep=';', index=False)
        print('Train data has been created.')
    else:
        base_df = pd.read_csv(os.path.join(os.getcwd(), 'datasets', 'TrainNER_sentenceID.csv'), delimiter=';', encoding='cp1252')
        print('TrainNER_sentenceID.csv was read.')
    train_data = create_train_data(base_df, SEN_N)

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
            print(str(itn) + ' iteration with ' + str(losses))

    print("===========\nTraining is finished.\n===========\nStarting evaluation for the rest of the sentences.")
    predicted_df = base_df
    sentenceID = 1
    doc = nlp(get_sentence(predicted_df, sentenceID))
    is_train_data = False
    for index, row in predicted_df.iterrows():
        if sentenceID != row['SentenceID']:
            is_train_data = False
            sentenceID = row['SentenceID']
            sentence = get_sentence(predicted_df, sentenceID)
            doc = nlp(sentence)
            for data in train_data:
                if sentence == data[0]:
                    is_train_data = True
                    break

        # If nlp does not find a class for word we set it 'O' because it is the most likely
        predicted_df.loc[index, 'Prediction'] = 'O'
        # If there is a valid predicted class we change O
        for ent in doc.ents:
            if row['Word'] == str(ent):
                predicted_df.loc[index, 'Prediction'] = ent.label_
                break

        predicted_df.loc[index, 'is_trained'] = is_train_data
        if index % 10000 == 0:
            print('\t' + str(index) + ' rows predicted')

    predicted_df.to_csv(OUT_FILE, sep=';')
    print('==============')
    print("Acc: " + str(get_acc(predicted_df)))
    print("Recall: " + str(get_recall(predicted_df)))
    print("Precision: " + str(get_precision(predicted_df)))
    print('==============')


if __name__ == '__main__':
    main()
