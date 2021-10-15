import random
import json
import pickle
import numpy as np
from datetime import datetime

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

def cleanSentence(sentence):
    sentence = sentence.lower()
    sentence = nltk.word_tokenize(sentence)
    sentence = [lemmatizer.lemmatize(word) for word in sentence]
    return sentence

def bagOfWords(sentence):
    sentence = cleanSentence(sentence)
    bag = [0]*len(words)
    for s in sentence:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict(sentence):
    bag = bagOfWords(sentence)
    res = model.predict(np.array([bag]))[0]
    results = [[i,r] for i,r in enumerate(res) if r>0.25]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})

    return return_list

def response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = i
            break

    return result

print("CovidBOT is active")

while True:
    sentence = input("You: ")
    results = predict(sentence)
    resp = response(results, intents)
    reply = random.choice(resp["responses"])
    if resp['tag'] == "time":
        reply += str(datetime.now())
    print("CovidBOT: ", reply)
    if resp["tag"] == "goodbye":
        break