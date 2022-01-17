
from flask import Flask, flash, render_template, request #, redirect, url_for
import re
from model import get_top5,get_users_list,cold_start_output


import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)  # intitialize the flaks app  # common 

app.secret_key = 'c-4@z5K;G2U0p/o.iaw[{?'

#Defining the main function under home page endpoint
@app.route('/',methods=['POST','GET'])
def home(): 
    if request.method == 'POST':
        input1=request.form['username'] #fetching username input from app
        input1=input1.lower() #converting input to lowercase
        if input1 in get_users_list(): #checking if entered username is in database
            output1=get_top5(input1)#,user_label,item_label,item_prediction,clean_data,vectorizer,sentiment_model)
        elif re.search('[^\s]',input1) is None: #checking if anything has been input or not
            flash('No username entered! Please enter a username & click "Submit".')
            output1=cold_start_output()
        else:
            flash('Username "{}" not found! Please try again.'.format(input1))
            output1=cold_start_output()
        return render_template('index.html', placeholder_text=output1, last_search=input1)
    if request.method == 'GET':
        return render_template('index.html', placeholder_text=cold_start_output())

if __name__ == '__main__' :
    app.run(debug=True)
