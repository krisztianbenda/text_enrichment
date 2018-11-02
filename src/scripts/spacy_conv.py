import pandas as pd

import sys

model_name = sys.argv[1]

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

df = pd.read_csv("../../datasets/TrainNER_Pred_{}".format(model_name), sep=';',encoding='utf-8')

df['Prediction'] = df.apply (lambda row: NE[row['OriginalPrediction']],axis=1)

results = {
    "Size": df.shape[0],
    "CorrectPredictionsWithO": df.loc[df['Category'] == df['Prediction']].shape[0],
    "CorrectEntity": df.loc[(df['Category'] != "O") & (df['Category'] == df['Prediction'])].shape[0],
    "AllEntities": df.loc[df['Category'] != "O"].shape[0],
    "AllPredictions": df.loc[df['Prediction'] != "O"].shape[0]
}
print(results)
print("Absoulte accuracy: {0:.2f}%".format(results["CorrectPredictionsWithO"] / results["Size"] * 100))
print("Entity based accuracy: {0:.2f}%".format(results["CorrectEntity"] / results["AllEntities"] * 100))
print("Predicted entity based accuracy: {0:.2f}%".format(results["CorrectEntity"] / results["AllPredictions"] * 100))
