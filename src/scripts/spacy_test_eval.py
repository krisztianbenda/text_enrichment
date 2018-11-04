import pandas as pd
import spacy

from tqdm import tqdm
import sys

model_name = 'en_core_web_lg'

print("Loading model: "+model_name)
nlp = spacy.load(model_name)

NE = {
    "B-EVENT": "B-event",
    "I-EVENT": "I-event",
    "B-LOC": "B-geo",
    "I-LOC": "I-geo",
    "B-GPE": "B-geo",
    "I-GPE": "I-geo",
    "B-PRODUCT": "B-obj",
    "I-PRODUCT": "I-obj",
    "B-WORK_OF_ART": "B-obj",
    "I-WORK_OF_ART": "I-obj",
    "B-ORG": "B-org",
    "I-ORG": "I-org",
    "B-PERSON": "B-per",
    "I-PERSON": "I-per",
    "B-TIME": "B-time",
    "I-TIME": "I-time",
    "B-DATE": "B-time",
    "I-DATE": "I-time",
    "B-NORP": "B-gpe",
    "I-NORP": "I-gpe",
    "B-FAC": "O",
    "I-FAC": "O",
    "B-LAW": "O",
    "I-LAW": "O",
    "B-LANGUAGE": "O",
    "I-LANGUAGE": "O",
    "B-PERCENT": "O",
    "I-PERCENT": "O",
    "B-MONEY": "O",
    "I-MONEY": "O",
    "B-QUANTITY": "O",
    "I-QUANTITY": "O",
    "B-ORDINAL": "O",
    "I-ORDINAL": "O",
    "B-CARDINAL": "O",
    "I-CARDINAL": "O",
    "O": "O"
}

df = pd.read_csv("../../datasets/Test2NER.csv", sep=';',encoding='cp1250', names=["Sentence","Word"])
df['OriginalPrediction'] = "O"

indexes = df[df['Sentence'].isnull() == False].index.values.tolist()
indexes.append(df.shape[0]-1)

for i in tqdm(range(len(indexes)-1)):
    start = indexes[i]
    end = indexes[i+1]
    init_tokens = df[(df.index >= start) & (df.index < end)]['Word'].values.tolist()
    s = ' '.join(init_tokens)
    doc = nlp(s)
    ents = []
    for ent in doc.ents:
        l = ent.text.split(' ')
        if len(l) == 1:
            ents.append([ent.text, 'B-' + ent.label_])
        else:
            ents.append([l[0], 'B-' + ent.label_])
            for i in range(1,len(l)):
                ents.append([l[i], 'I-' + ent.label_])
    i = 0
    for j in range(len(init_tokens)):
        if i < len(ents) and init_tokens[j] == ents[i][0]:
            df.loc[df.index == start+j, 'OriginalPrediction'] = ents[i][1]
            i += 1
        df.loc[df.index == start+j, 'SentenceID'] = i
    df[(df.index >= start) & (df.index < end)]

df['Prediction'] = df.apply (lambda row: NE[row['OriginalPrediction']],axis=1)

df.to_csv("../../datasets/Test2NERPred.csv", sep=';', encoding='cp1250', index=False, columns=["Sentence","Word","Prediction"])

