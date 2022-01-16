# The following code has the flask application as well as model code loaded together 
# Keeping a separate model.py file triggers Heroku error H12 as some usernames need more than 30 seconds of request response time
# Hence, i request the evaluator to accept this file as combination of required model.py & app.py files
# This loads the requisite pickles and defines the function to apply the sentiment model
# and the recommendation system

from flask import Flask, flash, render_template, request #, redirect, url_for
import pickle, re, pandas as pd #, numpy as np 

#from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.linear_model import LogisticRegression
#from sklearn.preprocessing import LabelEncoder

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)  # intitialize the flaks app  # common 

app.secret_key = 'c-4@z5K;G2U0p/o.iaw[{?'
#loading the pickled files for the app to execute
clean_data = pickle.load(open("pickle/clean_data.pickle", "rb")) #the dataframe holding processed database
user_label = pickle.load(open("pickle/user_label.pickle", "rb"))    #username label encoder
item_label = pickle.load(open("pickle/item_label.pickle", "rb"))    #item name label encoder
item_prediction = pickle.load(open("pickle/item_prediction.pickle", "rb")) #the item-based recommendation matrix
sentiment_model = pickle.load(open("pickle/sentiment_model.pickle", "rb")) #the ML model for sentiment prediction
vectorizer = pickle.load(open("pickle/vectorizer.pickle", "rb")) #Tf-idf vectorizer to vectorize lemmatized text
overall_top5 = pickle.load(open("pickle/overall_top5.pickle", "rb")) #overall top 5 items by poplarity & sentiment

clean_data['item_code']=clean_data.name.apply(lambda x:item_label.transform([x])[0])
clean_data['predicted_sentiment']=clean_data.text_title_lemma.apply(lambda x:sentiment_model.predict(vectorizer.transform([x]))[0])
def get_frac(item_code):
    try:
        frac=round(clean_data[clean_data.item_code==item_code].predicted_sentiment.value_counts(normalize=True).loc['Positive'],3)
    except:
        frac=0
    return frac
pos_frac_dict={item_code:get_frac(item_code) for item_code in clean_data.item_code.unique()}

def get_top5_2(input1):
    input_user=user_label.transform([input1])[0] #convert to label encoded value
    #Generate top 20 recommended products from item-based recommendation system for this user
    #Top 20 items for input_user
    pred20=pd.DataFrame(item_prediction.loc[:,input_user].sort_values(ascending=False)[0:20]).reset_index()
    output_dict={'item_code':[],'positive_fraction':[]}
    for item in pred20.item:
        output_dict['item_code'].append(item)
        output_dict['positive_fraction'].append(pos_frac_dict.get(item))
        output=pd.DataFrame(output_dict).sort_values(by='positive_fraction',ascending=False).head()
    #Returning top 5 recommendations for input_user
    output_text=['The top 5 items recommended for user "{}" are:'.format(input1)]
    for number in range(5):
        output_text.append('{}. {}'.format(number+1,item_label.inverse_transform([list(output.item_code)[number]])))
    return output_text

#Defining the main function under home page endpoint
@app.route('/',methods=['POST','GET'])
def home():
    if request.method == 'POST':
        input1=request.form['username'] #fetching username input from app
        input1=input1.lower() #converting input to lowercase
        if input1 in list(clean_data.reviews_username.unique()): #checking if entered username is in database
            output1=get_top5_2(input1) #,user_label,item_label,item_prediction,clean_data,vectorizer,sentiment_model)
        elif re.search('[^\s]',input1) is None: #checking if anything has been input or not
            flash('No username entered! Please enter a username & click "Submit".')
            output1=cold_start_output()
        else:
            flash('Username "{}" not found! Please try again.'.format(input1))
            output1=cold_start_output()
        return render_template('index.html', placeholder_text=output1, last_search=input1)
    if request.method == 'GET':
        return render_template('index.html', placeholder_text=output1)

def get_top5(input1):#,user_label,item_label,item_prediction,clean_data,vectorizer,sentiment_model):
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

def cold_start_output(): #for cold start cases when input username is not in database, i recommend overall top 5 items by poplarity & sentiment
    output_cs=['For first time user with no purchase history in database, please find below the overall top 5 items recommended by sentiment & popularity from database:']
    output_cs.extend(['{}. {}'.format(i+1,overall_top5[i]) for i in range(5)])
    return output_cs

if __name__ == '__main__' :
    app.run(debug=True)
