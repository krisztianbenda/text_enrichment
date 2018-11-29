import simplejson as json

with open("all_s.json", 'r') as f:
    data = json.load(f)

with open("train_data.json", 'w') as f:
    json.dump(data[:7200], f)

with open("test_data.json", 'w') as f:
    json.dump(data[7200:9000], f)
