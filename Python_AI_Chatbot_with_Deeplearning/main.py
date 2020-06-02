import nltk 
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
import tensorflow as tf
import random
import json
import pickle

with open("intents.json") as file:
    data = json.load(file)

try:
    with open('data.pickle', "rb") as f:
        words, labels, training, output = pickle.load()
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for question in intent["questions"]:
            wrds = nltk.word_tokenize(question)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])
            
            if intent["tag"] not in labels:
                labels.append(intent["tag"])
                
    # preprocessing data
    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    # bag of words 
    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]
        
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
                
        outpout_row = out_empty[:]
        outpout_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(outpout_row)
        
    training = np.array(training)
    output = np.array(output)

    with open('data.pickle', "wb") as f:
        pickle.dump((words, labels, training, output), f)

# training the model
tf.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")

# predictions
def bag_of_xords(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    
    return np.array(bag)


def chat():
    print("Start talking with the bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break
        
        results = model.predict([bag_of_xords(inp, words)])
        results_index = np.argmax(results)
        tag = labels[results_index]
        
        for tg in data['intents']:
            if tg["tag"] == tag:
                responses = tg["reponses"]
        print(random.choice(responses))

chat()
