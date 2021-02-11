#general imports
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import numpy as np # linear algebra
import seaborn as sns # plotting
import matplotlib.pyplot as plt # plotting
%matplotlib inline
import os # accessing directory structure


import re
import spacy
###Vader Sentiment
#To install vaderSentiment
#!pip install vaderSentiment 
from vaderSentiment import vaderSentiment
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

####Lemmatization
from nltk.stem import WordNetLemmatizer
# Lemmatize with POS Tag
from nltk.corpus import wordnet

def load_traindatafromdrive(INPUT_FILE):
  import pickle
  pickle_file = open(INPUT_FILE, "rb")
  while True:
      try:
          data = pickle.load(pickle_file)
      except EOFError:
          break
  pickle_file.close() 
  data['scaled_rating'] = data.apply(lambda x: x['rating']/10 if x['source']=='TA' else x['rating']/2,axis=1) 
  return data

def sentiment(text):
  sent_analyser = SentimentIntensityAnalyzer()
  return sent_analyser.polarity_scores(text)

def senti(data,cut_off = 0.05):
    if data['compound'] >= cut_off:
        val = "Positive"
    elif data['compound'] <= -cut_off:
        val = "Negative"
    else:
        val = "Neutral"
    return val

def append_predictions(data = data,output_sentiment=True,train = True):
  if not 'title' not in data.columns:
    if train:
      pred = (data["review"].astype(str)+data['title'].astype(str)).apply(sentiment)
    else: 
      pred = data['review'].astype(str).apply(sentiment)
  else: pred = (data["full_message"].astype(str)).apply(sentiment)
  data['neg'] = pred.apply(lambda x : x['neg'])
  data['neu'] = pred.apply(lambda x : x['neu'])
  data['pos'] = pred.apply(lambda x : x['pos'])
  data['compound'] = pred.apply(lambda x : x['compound'])
  if output_sentiment:
    data['Sentiment'] = data.apply(senti, axis=1)

  return data


def main(INPUT_FILE = "/content/drive/Shareddrives/Hackathon/Data/combined_data4.pkl" ,OUTPUT_FILE = 'final_master.csv'):
  data =  load_traindatafromdrive(INPUT_FILE)
  data = append_predictions()
  data.to_csv(OUTPUT_FILE)

def predict_on_test(INPUT_FILE ,OUTPUT_FILE = 'predictions.csv'):
  if INPUT_FILE.find('csv')>0:
    data =  pd.read_csv(INPUT_FILE)
  if INPUT_FILE.find('xl')>0:
    data =  pd.read_excel(INPUT_FILE)
  data = append_predictions(data=data,train = False)
  data.to_csv(OUTPUT_FILE)
  return data

#main()
#main()