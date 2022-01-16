
# This is basically the heart of my flask 

from flask import Flask, flash, render_template, request, redirect, url_for
import pickle, re, pandas as pd, numpy as np 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)  # intitialize the flaks app  # common 
app.secret_key = 'c-4@z5K;G2U0p/o.iaw[{?'
#loading the pickled files for the app to execute
clean_data = pickle.load(open("pickle/clean_data.pickle", "rb"))
user_label = pickle.load(open("pickle/user_label.pickle", "rb"))
item_label = pickle.load(open("pickle/item_label.pickle", "rb"))
item_prediction = pickle.load(open("pickle/item_prediction.pickle", "rb"))
sentiment_model = pickle.load(open("pickle/sentiment_model.pickle", "rb"))
vectorizer = pickle.load(open("pickle/vectorizer.pickle", "rb"))
overall_top5 = pickle.load(open("pickle/overall_top5.pickle", "rb"))

#Defining the main function under home page endpoint
@app.route('/',methods=['POST','GET'])
def home():
    output1=['For first time user with no purchase history in database, please find below the overall top 5 items recommended by sentiment & popularity from database:']
    output1.extend(['{}. {}'.format(i+1,overall_top5[i]) for i in range(5)])
    if request.method == 'POST':
        input1=request.form['username']
        input1=input1.lower() #converting input to lowercase
        if re.search('[^\s]',input1) is None:
            flash('No username entered! Please enter a username & click "Submit".')
        elif input1 in list(clean_data.reviews_username):
            output1=get_top5(input1,user_label,item_label,item_prediction,clean_data,vectorizer,sentiment_model)
        else:
            flash('Username "{}" not found! Please try again.'.format(input1))
        return render_template('index.html', placeholder_text=output1, last_search=input1)
    if request.method == 'GET':
        return render_template('index.html', placeholder_text=output1)

def get_top5(input1,user_label,item_label,item_prediction,clean_data,vectorizer,sentiment_model):
    input_user=user_label.transform([input1])[0] #convert to label encoded value
    #Generate top 20 recommended products from item-based recommendation system for this user
    #Top 20 items for input_user
    pred20=pd.DataFrame(item_prediction.loc[:,input_user].sort_values(ascending=False)[0:20]).rename(columns={input_user:'scoring'}).reset_index()
    pred20['item_name']=pred20.item.apply(lambda x:item_label.inverse_transform([x])[0])
    #Processing the top 20 recommended items' reviews for sentiment
    output_dict={'item_name':[],'total_reviews':[],'positive_fraction':[]}
    for item in pred20.item_name:
        positive_count=0
        total_reviews=0
        for review in clean_data[clean_data.name==item].text_title_lemma: #fetching processed reviews for item
            total_reviews+=1
            review_vec=vectorizer.transform([review]) #vectorizing
            if sentiment_model.predict(review_vec)[0]=='Positive': #counting predictions of positive sentiment
                positive_count+=1
        output_dict['item_name'].append(item)
        output_dict['total_reviews'].append(total_reviews)
        output_dict['positive_fraction'].append(round(positive_count/total_reviews,3)) #calculating positive fraction of all reviews for item
    output=pd.DataFrame(output_dict).sort_values(by='positive_fraction',ascending=False)
    #Returning top 5 recommendations for input_user
    output_text=['The top 5 items recommended for user "{}" are:'.format(user_label.inverse_transform([input_user])[0])]
    for number in range(5):
        output_text.append('{}. {}'.format(number+1,list(output.item_name)[number]))
    return output_text

if __name__ == '__main__' :
    app.run(debug=True)
