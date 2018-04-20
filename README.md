# SI206 Final Project: Demonstrating Post Popularity on Reddit

# Purpose of Project
Retrieve which posts gain the most traction on Reddit in general, but also specifically within Subreddits within a span of 24 hours.

# Accessing Data Sources
Users will need to retrieve their own credentials from Reddit's app developer for the following:

client_id = ""

client_secret = ""

password = ""

username = ""

The above will require users to create a Reddit account and also to create a script-based application here: https://www.reddit.com/prefs/apps/ 

# Data Source 1: Making a Request to Reddit API to Access Subreddit Data
- Make a request with limit 10 to get 10 records per the 45 popular subreddits that I specify in popular_subreddits

- Create a class, Post, to store the title, subreddit name, time created, permalink, gilded value (if any), and upvote score of 10           posts within a subreddit

- Populate Subreddits and Posts database tables from reddit.db database with above data: get_reddit_auth() and get_token()

- Use CLIENT_ID and CLIENT_SECRET with requests.auth.HTTPBasicAuth

- Request to "https://www.reddit.com/api/v1/access_token" to retrieve access token

- Save token response in a separate cache for credentials using make_request(subreddit) for “https://oauth.reddit.com/r/” + subreddit

# Data Source 2: Scraping Reddit’s ‘top’ Posts Page

- Retrieve top-scoring links from past 24 hours
- make_request_using_cache(url): If the url for the request is not already in the cache after making a request, then write it to the cache
- Did not have to use authentication methods for this part but I did have to specify a User-Agent because at first the website thought I was a bot: ({"User-Agent": "Final Project by /u/" + USERNAME})

# Running the Program
- python3 final_project.py: Running this will generate the prompt "Fetch new or cached data? new/cached: ". If user has never ran the program before, will need to say "new" to populate reddits.db database and create cache. "cached" will call functions to retrieve information for each popular subreddit that is already stored in cache.json.
- "new": get_reddit_auth() – generates access token to make a request; search_populars() – uses authorization to get data from popular subreddits and enters data into Subreddits and Posts
- "cached": check_cache() – assuming the user has already ran ‘new’ command once before and has a stored credentials cache, checks the cache and gets the access token it needs to carry out a reddit session and search the popular subs
- "bar chart upvotes", "bar chart gilded", "scatterplot upvotes", "scatterplot gilded": After user has entered data into database through above commands, can type commands to display data in two different modes, bar chart or scatterplot, based on upvotes or whether the subreddit has posts that have been gilded (if so, how many of them)
- Connection and storage of data into the database is required for the visualization functions to work because they execute                 SQL queries that aggregate each post's upvote/gilded score and join the Subreddits and Posts tables on their foreign key                   (ID and subreddit_id)
- "top posts": Retrieves top posts from the general Reddit ‘top’ links page, rather than a specific subreddit; Calls get_top_posts() which will generate a bar chart to display a preview of the top post and its corresponding number of upvotes
- "help": Displays all of the possible commands from help.txt
- "exit": Exits the program

# SQLite Database
- FOREIGN KEY(Subreddit_ID) REFERENCES Subreddits(ID): Allows tables to be JOINed on Subreddits ON Subreddits.Name = Posts.Subreddit_Name
- SET Subreddit_ID = (SELECT ID FROM Subreddits WHERE Subreddits.Name = Posts.Subreddit_Name)

              
# Caching
- Two cache files (cache.json and creds.json), one to store the Reddit API responses and one to store credentials (i.e., access token)
- Reddit’s API allows you to retrieve a nicely json-formatted response when you make a request to it
- CACHE_DICTION[subreddit] = response in the get_data() function makes a cache file with many attributes for each post, which made it relatively simple to make a Post class and then extract the necessary information from the json file to make instance variables

# Overview of Elements/Functions:
- reddit.db: Connect to database and create Subreddits and Posts Databases
- checkcache(): Open cache file and read it to see if contents need to be deleted before making a request
- make_request_using_cache(url): Make a request to popular subreddit URLs and write the json response to CACHE_DICTION
- get_token(): Check creds.json (credentials cache) to see if access token is already saved, if it is, return it
- get_reddit_auth(): If token is not already in credentials cache above, use requests.auth.HTTPBasicAuth to make a request to               https://www.reddit.com/api/v1/access_token and saves the resulting token to the credentials cache
- make_request(subreddit): Makes request to Reddit API for 10 records within a specific subreddit (https://oauth.reddit.com/r/" +           subreddit), sorted by ‘top’
- class Post(object): Organizes each post dictionary into a class instance
- get_data(subreddit): Returns data from each subreddit either from storage in cache or from making a new request and then saving           the response as the value for the subreddit in cache.json
- enter_data(subreddit): Inserts data into database tables by creating Post objects from the dictionary in the json response from           get_data(), making SQL queries, and using INSERT statements to populate reddit.db
- search_populars(): Searches each of specified 45 popular_subreddits, and for each item in the list, calls enter_data() to populate         reddit.db
- get_top_links(): Scrapes Reddit's top posts page to get top scoring links from past 24 hours, creates bar graph to display the             post previews with corresponding upvote count
- bar_chart(): Creates a popularity score based off of each subreddit's total accumulated score from Posts and plots data into bar           graph
- bar_chart2(): If a subreddit has a gilded post in the database (Posts.Gilded > 0), creates bar chart displaying subreddit with             total gilded post value
- scatterplot(): Creates a popularity score based off of each subreddit's total accumulated score from Posts and plots data into             scatterplot
- scatterplot2(): If a subreddit has a gilded post in the database (Posts.Gilded > 0), creates bar chart displaying subreddit with           total gilded post value
- get_top_posts(): Retrieves top posts from the general Reddit ‘top’ links page, rather than a specific subreddit, generates bar chart to display a preview of the top post and its corresponding number of upvotes
