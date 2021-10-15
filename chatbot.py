import random
import json
import pickle
import numpy as np
from datetime import datetime
import requests

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

def cleanSentence(sentence):
    '''
    Cleans the sentence of punctuation and lemmatizes the words
    '''
    sentence = sentence.lower()
    sentence = nltk.word_tokenize(sentence)
    sentence = [lemmatizer.lemmatize(word) for word in sentence]
    return sentence

def bagOfWords(sentence):
    '''
    Creates a bag of words from the sentence    
    '''
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
    results = [[i, r] for i, r in enumerate(res) if r > 0.25]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for result in results:
        return_list.append({"intent": classes[result[0]], "probability": str(result[1])})

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

def covid_info(state_name):
    res = requests.get("https://api.rootnet.in/covid19-in/stats/latest")
    data = res.json()
    all_states = data["data"]["regional"]
    # print("inside function----------")
    for state in all_states:
        if state["loc"].lower() == state_name.lower():
            return state

def extract_stateName(sentence):
    for i in sentence.split():
        for j in statesList:
            if i.capitalize() in j.split():
                return j

statesList = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal pradesh", "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Lakshadweep", "Puducherry"]

while True:
    sentence = input("You: ")
    results = predict(sentence)
    resp = response(results, intents)
    reply = random.choice(resp["responses"])
    if resp['tag'] == "time":
        reply += str(datetime.now().strftime("%X"))
    elif resp['tag'] == "date":
        reply += str(datetime.now().strftime("%d %b, %Y"))
    elif resp['tag'] == "covid":
        stateName = extract_stateName(sentence)
        state = covid_info(stateName)
        reply1 = '''
        Total Confirmed Cases: {},
        Total Deaths: {}'''.format(state["totalConfirmed"], state["deaths"])
        reply += stateName + ":" + reply1 
    print("CovidBOT: ", reply)
    if resp["tag"] == "goodbye":
        break


