
# The following code loads the requisite pickles and defines the function to apply the sentiment model
# and the recommendation system

import pickle, pandas as pd
from collections import Counter

import warnings
warnings.filterwarnings("ignore")

#loading the pickled files for the app to execute
clean_data = pickle.load(open("pickle/clean_data.pickle", "rb")) #the dataframe holding processed database
item_prediction = pickle.load(open("pickle/item_prediction.pickle", "rb")) #the item-based recommendation matrix
sentiment_model = pickle.load(open("pickle/sentiment_model.pickle", "rb")) #the ML model for sentiment prediction
review_vec_dict = pickle.load(open("pickle/item_review_vec_dict.pickle", "rb")) #Dictionary of item:vectorized reviews
overall_top5 = pickle.load(open("pickle/overall_top5.pickle", "rb")) #overall top 5 items by poplarity & sentiment

def cold_start_output(): #for cold start cases when input username is not in database, i recommend overall top 5 items by poplarity & sentiment
    output_cs=['For first time user with no purchase history in database, please find below the overall top 5 items recommended by sentiment & popularity from database:']
    output_cs.extend(['{}. {}'.format(i+1,overall_top5[i]) for i in range(5)])
    return output_cs

def get_users_list():
    return list(clean_data.reviews_username.unique()) #list of all unique users in database

def get_top5(input1):
    #Generate top 20 recommended products from item-based recommendation system for this user
    #Top 20 items for input_user
    pred20=pd.DataFrame(item_prediction.loc[:,input1].sort_values(ascending=False)[0:20]).reset_index()
    pos_frac=[] #positive fraction for these 20 items
    for item_name in pred20.item: #predict sentiment and calculate positive sentiment fraction for each of these 20 items
        sentiments=[sentiment_model.predict(review_vec)[0] for review_vec in review_vec_dict.get(item_name)]
        new_counter=Counter(sentiments)
        pos_frac.append(round(new_counter.get('Positive')/sum(list(new_counter.values())),3)) #positive sentiment review fraction
    pred20['pos_frac']=pos_frac
    output=list(pred20.sort_values(by='pos_frac').head().item) #getting top 5 items by positive sentiment fraction
    output_text=['The top 5 items recommended for user "{}" are:'.format(input1)]
    for number in range(5):
        output_text.append('{}. {}'.format(number+1,output[number]))
    return output_text
