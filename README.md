# SI 206 Final Project -- Measuring Post Popularity on Reddit

# Purpose of Project
Retrieve which posts gain the most traction on Reddit in general, but also specifically within Subreddits within a span of 24 hours.

# Accessing Data Sources
User will need to retrieve their own credentials from Reddit's app developer for the following:

client_id = ""

client_secret = ""

password = ""

username = ""

The above will require user to create an account and also to create a script-based application 

•	Data Source 1: Making a request to the Reddit API to access Subreddit data
      o	Make a request with limit 10 to get 10 records per the 45 popular subreddits that I specify in popular_subreddits
      o	Create a class, Post, to store the title, subreddit name, time created, permalink, gilded value (if any), and upvote score of 10           posts within a subreddit
      o	Populate Subreddits and Posts database tables from reddit.db database with above data
      o	get_reddit_auth() and get_token()
              ♣	Use CLIENT_ID and CLIENT_SECRET with requests.auth.HTTPBasicAuth
              ♣	Request to "https://www.reddit.com/api/v1/access_token" to get access 
              ♣	Save token response in a separate cache for credentials
      o	make_request(subreddit)
              ♣	“https://oauth.reddit.com/r/” + subreddit

•	Data Source 2: Scraping Reddit’s ‘top’ Posts Page
      o	Retrieve top-scoring links from past 24 hours
      o	make_request_using_cache(url)
              ♣	If the url for the request is not already in the cache after making a request, then write it to the cache
      o	I did not have to use authentication methods for this part but I did have to specify a User-Agent because at first the website             thought I was a bot 
              ♣	({"User-Agent": "Final Project by /u/" + USERNAME})

•	Running the Program
      1.	python3 final_project.py
              ♣ Running this will generate the prompt "Fetch new or cached data? new/cached: "
              ♣ If user has never ran the program before, will need to say "new" to populate reddits.db database and create cache
              ♣ "cached" will call functions to retrieve information for each popular subreddit that is already stored in cache.json
      2.	"new"
              a.	get_reddit_auth() – generating access token to make a request
              b.	search_populars – uses authorization to get data from popular subreddits and enters data into Subreddits and Posts
      3.	"cached"
              a.	check_cache() – assuming the user has already ran ‘new’ command once before and has a stored credentials cache, checks                 the cache and gets the access token it needs to carry out a reddit session and search the popular subs
      4.	"bar chart upvotes" 
          "bar chart gilded"
          "scatterplot upvotes"
          "scatterplot gilded"
              ♣ After user has entered data into database through above commands, can type commands to display data in two different                       modes, bar chart or scatterplot, based on upvotes or whether the subreddit has posts that have been gilded (if so, how                     many of them)            
              ♣ Connection and storage of data into the database is required for the visualization functions to work because they execute                 SQL queries that aggregate each post's upvote/gilded score and join the Subreddits and Posts tables on their foreign key                   (ID and subreddit_id), grouping the score by the name of the subreddit and ordering in descending or ascending order
              ♣ fetchall() generates a list of the aggregated upvote or gilded scores and the subreddit name associated. After unpacking                   the list, we then use Plotly to create a visual of the data collected.
      4.	"top posts"
              ♣	Retrieves top posts from the general Reddit ‘top’ links page, rather than a specific subreddit
              ♣	This will call get_top_posts() which will generate a bar chart to display a preview of the top post and its                               corresponding number of upvotes
      5.	The user response ‘help’ displays all of the possible commands from help.txt

•	SQLite Database
      o	FOREIGN KEY(Subreddit_ID) REFERENCES Subreddits(ID)
              ♣	Above allows tables to be JOINed on Subreddits ON Subreddits.Name = Posts.Subreddit_Name 
              
•	Caching with cache.json and creds.json
              ♣	I have two cache files, one to store the Reddit API responses and one to store credentials (i.e, access token)
              ♣	Reddit’s API allows you to retrieve a really nicely json-formatted response when you make a request to it, so                             CACHE_DICTION[subreddit] = response in the get_data() function makes a cache file with many attributes for each post,                     which made it relatively simple to make a Post class and then extract the necessary information from the json file to make                 instance variables. 

Overview of Elements/Functions:
reddit.db: Connect to database and create Subreddits and Posts Databases
      o	checkcache(): Open cache file and read it to see if contents need to be deleted before making a request
      o	make_request_using_cache(url): Make a request to popular subreddit URLs and write the json response to CACHE_DICTION
      o	get_token(): Check creds.json (credentials cache) to see if access token is already saved, if it is, return it
      o	get_reddit_auth(): If token is not already in credentials cache above, use requests.auth.HTTPBasicAuth to make a request to               https://www.reddit.com/api/v1/access_token and saves the resulting token to the credentials cache
      o	make_request(subreddit): Makes request to Reddit API for 10 records within a specific subreddit (https://oauth.reddit.com/r/" +           subreddit), sorted by ‘top’
      o	class Post(object): Organizes each post dictionary into a class instance
      o	get_data(subreddit): Returns data from each subreddit either from storage in cache or from making a new request and then saving           the response as the value for the subreddit in cache.json
      o	enter_data(subreddit): Inserts data into database tables by creating Post objects from the dictionary in the json response from           get_data(), making SQL queries, and using INSERT statements to populate reddit.db
      o	search_populars(): Searches each of specified 45 popular_subreddits, and for each item in the list, calls enter_data() to populate         reddit.db
      o	get_top_links(): Scrapes Reddit's top posts page to get top scoring links from past 24 hours, creates bar graph to display the             post previews with corresponding upvote count
      o	bar_chart(): Creates a popularity score based off of each subreddit's total accumulated score from Posts and plots data into bar           graph
      o bar_chart2(): If a subreddit has a gilded post in the database (Posts.Gilded > 0), creates bar chart displaying subreddit with             total gilded post value
      o	scatterplot(): Creates a popularity score based off of each subreddit's total accumulated score from Posts and plots data into             scatterplot
      o	scatterplot2(): If a subreddit has a gilded post in the database (Posts.Gilded > 0), creates bar chart displaying subreddit with           total gilded post value
      o	get_top_links(): Retrieves top posts from the general Reddit ‘top’ links page, rather than a specific subreddit,calls                     get_top_posts() which will generate a bar chart to display a preview of the top post and its corresponding number of upvotes
