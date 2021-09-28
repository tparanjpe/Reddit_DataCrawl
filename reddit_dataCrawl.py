#Tara Paranjpe
#CSE 472 - Project 1 
#reddit_dataCrawl.py

import requests
import json
import praw
import pandas as pd
import networkx as netx
import random
import matplotlib.pyplot as plt

# IMPORTANT INFORMATION ABOUT THE CODE below this to line 33!
# The code is adapted from https://gist.github.com/jamescalam/d7e6a7236e99369123237f0ba371da18#file-reddit-oauth-py!!
# This link was given in the Appendix of the Project 1 Guidelines and was taken to get the Reddit authorization token.

#this line gets the authorization based on the client id and client secret
#PLEASE PROVIDE CLIENTID AND SECRET, RESPECTIVELY BELOW!
#                           CLIENT ID  CLIENT SECRET
auth = requests.auth.HTTPBasicAuth('', '')


#here, we give the username and password for the reddit account. 
#PLEASE PROVIDE USERNAME AND PASSWORD RESPECTIVELY BELOW
data = {'grant_type': 'password',
        'username': '', # USERNAME
        'password': ''} #PASSWORD

#THIS IS THE USER-AGENT, CAN LEAVE AS IS OR PROVIDE DESIRED USERAGENT
headers = {'User-Agent': 'happyt27'}

#this line is responsible for the post request to get the authorization token. 
#it passes in the authorization, data, and headers.
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

print(res.json())

#get the token from the post request response
TOKEN = res.json()['access_token']
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# IMPORTANT INFORMATION ABOUT THE ABOVE CODE
# The code above this is adapted from https://gist.github.com/jamescalam/d7e6a7236e99369123237f0ba371da18#file-reddit-oauth-py!!
# This link was given in the Appendix of the Project 1 Guidelines and was taken to get the Reddit authorization token.

#this is a list that is responsible for storing all the JSON data
resList = []

#get request for JSON data for the ASU subreddit
try:
        res = requests.get('https://oauth.reddit.com/r/ASU/', headers=headers)
        resList.append(res.json())
except:
        print("Error getting ASU subreddit data")
        exit()

#dump the json data to the datacrawl file
with open("dataCrawl.json", "w") as f:
        json.dump(resList, f)


#this initializes the redditInstance
#PLEASE SPECIFY CLIENTID, CLIENTSECRET, USERNAME, PASSWORD, AND USER_AGENT TO GET ACCESS TO THIS INSTANCE.
myRedditInstance = praw.Reddit(client_id = "", 
                                client_secret = "",
                                usernme = "",
                                password = "",
                                user_agent = headers)

print("\nIf nothing prints in the terminal for ~3-5 min, please terminate script and re-run. Script tends to get hung. \n")

#get the data from the json body
myFile = open("dataCrawl.json",)
myData = json.load(myFile)
#initialize helper variables
relatedSubreddits = []
subredditDict = {}
numberOfNodes = 0
myEdgeValues = []

#iterate through the data and get each author, then each comment the author has made
for val in myData[0]['data']['children']:
        postAuthor = val['data']['author']
        specificRedditor = myRedditInstance.redditor(postAuthor)
        for comment in specificRedditor.comments.new(limit=10):
                targetSubreddit = comment.subreddit
                #tries to get 20 nodes here
                if numberOfNodes == 20:
                        break

                # makes sure that the subreddits added are unique 
                if subredditDict.get(targetSubreddit) == None and targetSubreddit != 'ASU':
                        relatedSubreddits.append(targetSubreddit)
                        subredditDict[targetSubreddit] = targetSubreddit
                        #add this data to the list of edges
                        myEdgeValues.append(['ASU', targetSubreddit])
                        numberOfNodes = numberOfNodes + 1

#for our benefit
print(relatedSubreddits)
                        
#loops through each subreddit, gets comments, and gets associated subreddits
for relatedSubred in relatedSubreddits:
        #random values for limit to get subreddits from comments
        capacity = random.randint(3, 8)
        commentsEvalulated = 0

        print(relatedSubred)

        #get request for the new subreddit
        try:
                postRequestString = 'https://oauth.reddit.com/r/' + str(relatedSubred) + '/'
                res = requests.get(postRequestString, headers=headers)
        
        except:
                print("Subreddit not found")
                break
        
        
        resList.append(res.json())
        
        with open("dataCrawl.json", "w") as f:
                json.dump(resList, f)
        

        myFile = open("dataCrawl.json",)
        myData = json.load(myFile) 

        #gets related comments and consequent subreddits
        for val in resList[-1]['data']['children']:
                postAuthor = val['data']['author']
                if commentsEvalulated == capacity:
                        break;   
                specificRedditor = myRedditInstance.redditor(postAuthor)
                try:
                        for comment in specificRedditor.comments.new(limit=1):
                                targetSubreddit = comment.subreddit

                                if subredditDict.get(targetSubreddit) == None and targetSubreddit != 'ASU':
                                        myEdgeValues.append([relatedSubred, targetSubreddit])
                                        commentsEvalulated = commentsEvalulated + 1
                                        subredditDict[targetSubreddit] = targetSubreddit
                                        numberOfNodes = numberOfNodes + 1
                except:
                        print("Subreddit not found")
                        break

                

#gets number of nodes, adds the edges to the dataframe for networkx
print("number of nodes" + str(numberOfNodes))
subredditDF = pd.DataFrame(myEdgeValues, columns=['Starting', 'endSubreddit'])
print(subredditDF)

#creates the graph and saves it in networkGraph.png
myGraph = netx.from_pandas_edgelist(subredditDF, source='Starting', target='endSubreddit')
netx.draw(myGraph, with_labels=True)
plt.savefig("networkGraph.png", format="PNG")
plt.show()

#plot degree distribution and save in histogram.png
myDegrees = [myGraph.degree(n) for n in myGraph.nodes()]
plt.hist(myDegrees)
plt.savefig("histogram.png", format="PNG")
plt.show()

#get the degree centrality, sort it and print it out nicely
myCentrality = netx.degree_centrality(myGraph)
print("Degree Centrality Analysis\n")
for value in sorted(myCentrality, key=myCentrality.get, reverse=True):
        print(value, myCentrality[value])

#get the betweenness centrality, sort it and print it out nicely
myBetweenness = netx.betweenness_centrality(myGraph)
print("Betweenness Centrality Analysis\n")
for value in sorted(myBetweenness, key=myBetweenness.get, reverse=True):
        print(value, myBetweenness[value])