
from flask import Flask, flash, render_template, request, redirect, url_for 
import re 
import warnings
warnings.filterwarnings("ignore")
from model import cold_start_top5, get_top5, get_users_list #importing the functions from model.py

app = Flask(__name__)  # intitialize the flaks app  # common 
app.secret_key = 'c-4@z5K;G2U0p/o.iaw[{?'

#Defining the main function under home page endpoint
@app.route('/',methods=['POST','GET'])
def home():
    output1=cold_start_top5()     #getting list of recommendations for a cold start situation when user is not in database
    all_users=get_users_list()  #list of all users in database
    if request.method == 'POST':
        input1=request.form['username'] #fetching username input from app
        input1=input1.lower() #converting input to lowercase
        if re.search('[^\s]',input1) is None: #checking if anything has been input or not
            flash('No username entered! Please enter a username & click "Submit".')
        elif input1 in all_users: #checking if entered username is in database
            output1=get_top5(input1) #processing input to get top 5 recommendations
        else:
            flash('Username "{}" not found! Please try again.'.format(input1))
        return render_template('index.html', placeholder_text=output1, last_search=input1)
    if request.method == 'GET':
        return render_template('index.html', placeholder_text=output1)

if __name__ == '__main__' :
    app.run(debug=True)
