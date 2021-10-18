import random
import json
import pickle
import numpy as np
from datetime import datetime
import requests
import re

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

# def extract_pincode_date(sentence):
#     for i in sentence.split():
#         pincode_i = re.search('^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$', i)
#         date_i = re.search(r'\d{2}-\d{2}-\d{4}', i)
#         date_output = datetime.strftime(date.group(),'%d-%m-%Y').date()
#         return i, date_output

def vaccination(pincode, date):
    api = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={}&date={}".format(pincode, date)
    response = requests.get(api)
    output = ''
    data = response.json()['sessions']
    for area in data:
        if area['available_capacity'] > 0:
            output+="\n"+"*"*30 + "Hospital Name: " + area['name'] + "*"*30 +"\n"
            output+=''' 
            Address: {}
            Pincode: {}
            State Name: {}
            District Name: {}
            Fee Type: {}
            Fee: {}
            available_capacity_dose1: {}
            available_capacity_dose2: {}
            available_capacity: {}
            min_age_limit: {}
            vaccine: {}
            Time Slots: {}
            '''.format(area['address'], area['pincode'], area['state_name'], area['district_name'], area['fee_type'], area['fee'], area['available_capacity_dose1'], area['available_capacity_dose2'], area['available_capacity'], area['min_age_limit'], area['vaccine'], str(area['slots'])[1:-1])
        elif area['available_capacity'] < 0:
            print("Currently no slots available for this area!")
            break
    return output

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
    elif resp['tag'] == "vaccination":
        pincode = int(input("Pincode: "))
        date = input("Date: ")
        reply2 = vaccination(pincode, date)
        reply += str(pincode) + " on " + date + ":" + reply2 
    print("CovidBOT: ", reply)
    if resp["tag"] == "goodbye":
        break


