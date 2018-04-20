import json
import requests
import requests.auth
import secrets
import sqlite3
import plotly as py
import plotly.graph_objs as go
import webbrowser
from bs4 import BeautifulSoup

CLIENT_ID = secrets.client_id
CLIENT_SECRET = secrets.client_secret
PASSWORD = secrets.password
USERNAME = secrets.username

CACHE_FNAME = 'cache.json'
CACHE_CREDENTIALS = 'creds.json'
CACHE_DICTION = {}

DBNAME = 'reddit.db'

try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except Error as e:
    print(e)

cur.execute('DROP TABLE IF EXISTS "Subreddits"')

statement = """
    CREATE TABLE 'Subreddits'(
        'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT UNIQUE NOT NULL
        );
    """

cur.execute(statement)
conn.commit()

cur.execute('DROP TABLE IF EXISTS "Posts"')

statement2 = """
    CREATE TABLE 'Posts'(
        'Subreddit_ID' INTEGER,
        'Title' TEXT NOT NULL,
        'Score' INTEGER NOT NULL,
        'Created_Time' REAL,
        'Subreddit_Name' TEXT,
        'Gilded' INTEGER,
        'Permalink' TEXT,
        FOREIGN KEY(Subreddit_ID) REFERENCES Subreddits(ID)
        );
    """

cur.execute(statement2)
conn.commit()

def check_cache():
    global CACHE_DICTION
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_contents = cache_file.read()
        CACHE_DICTION = json.loads(cache_contents)
        cur.execute("DELETE FROM Posts")
        conn.commit()
        cache_file.close()
    except:
        CACHE_DICTION = {}

def make_request_using_cache(url):
    header = {"User-Agent": "Final Project by /u/" + USERNAME}
    unique_ident = url
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url, headers = header)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]

def save_cache():
    full_text = json.dumps(CACHE_DICTION)
    cache_file_ref = open(CACHE_FNAME,"w")
    cache_file_ref.write(full_text)
    cache_file_ref.close()

def get_token():
    with open(CACHE_CREDENTIALS, 'r') as credentials:
        token_json = credentials.read()
        token_dict = json.loads(token_json)
        return token_dict['access_token']

def save_token(token_dict):
    with open(CACHE_CREDENTIALS, 'w') as credentials:
        token_json = json.dumps(token_dict)
        credentials.write(token_json)

def get_reddit_auth():
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
    headers = {"User-Agent": "Final Project by /u/" + USERNAME}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth = auth, data = data, headers = headers) # uses post because HTTP
    cred = json.loads(response.text)
    save_token(cred)

def make_request(subreddit):
    try:
        token = get_token()
    except:
        get_reddit_auth()
        token = get_token()

    headers = {"Authorization": "bearer " + token, "User-Agent": "Final Project by /u/" + USERNAME}
    params = {}
    response = requests.get("https://oauth.reddit.com/r/" + subreddit, headers = headers, params = {
        'sort': 'top',
        'limit': 10})
    return json.loads(response.text)

class Post(object):
    def __init__(self, post_dict):
        self.title = post_dict['data']['title']
        self.subreddit = post_dict['data']['subreddit']
        self.time_created = post_dict['data']['created_utc']
        self.permalink = post_dict['data']['permalink']
        self.gilded = post_dict['data']['gilded']
        self.score = post_dict['data']['score']

def get_data(subreddit):
    if subreddit not in CACHE_DICTION:
        print("Fetching today's new data for " + subreddit + '...')
        response = make_request(subreddit)
        CACHE_DICTION[subreddit] = response
        save_cache()
    else:
        print('Fetching ' + subreddit + ' data from cache...')
        results = CACHE_DICTION
    return CACHE_DICTION[subreddit]

def enter_data(subreddit):
    response = get_data(subreddit)

    if response == None:
        print("Sorry, no subreddit found.")

    else:
        for post_dict in response['data']['children']:
            post_obj = Post(post_dict)
            cur.execute("""INSERT OR IGNORE INTO Subreddits(Name) VALUES(?) """, (post_obj.subreddit,))
            conn.commit()

            cur.execute("""INSERT INTO Posts(Subreddit_ID, Title, Score, Created_Time, Subreddit_Name, Gilded, Permalink) VALUES(?, ?, ?, ?, ?, ?, ?) """, (None, post_obj.title, post_obj.score, post_obj.time_created, post_obj.subreddit, post_obj.gilded, post_obj.permalink))
            conn.commit()

            statement3 = "UPDATE Posts "
            statement3 += "SET Subreddit_ID = (SELECT ID FROM Subreddits WHERE Subreddits.Name = Posts.Subreddit_Name) "

            cur.execute(statement3)
            conn.commit()

def search_populars():
    popular_subreddits = ['art', 'AskReddit', 'askscience', 'aww', 'blog', 'Books', 'creepy', 'dataisbeautiful', 'DIY', 'Documentaries',
    'EarthPorn', 'explainlikeimfive', 'food', 'funny', 'Futurology', 'gadgets', 'gaming', 'GetMotivated', 'gifs', 'history', 'IAmA',
    'InternetIsBeautiful', 'Jokes', 'LifeProTips', 'listentothis','mildlyinteresting', 'movies', 'Music', 'news', 'nosleep', 'nottheonion',
    'OldSchoolCool', 'personalfinance', 'philosophy', 'photoshopbattles', 'science', 'Showerthoughts', 'space', 'sports', 'television',
    'tifu', 'todayilearned','UpliftingNews', 'videos', 'worldnews']

    for subreddit in popular_subreddits:
        enter_data(subreddit)

def get_top_posts():
    posts = {}
    baseurl = 'https://www.reddit.com/top/'

    page_html = make_request_using_cache(baseurl)
    page_soup = BeautifulSoup(page_html, 'html.parser')
    content_div = page_soup.find(class_ = 'content')

    upvote_score = content_div.find_all(class_ = 'score unvoted')
    post_title = content_div.find_all('p', class_ = 'title')
    
    count = 0
    for c in post_title:
        upvote_count = 0
        for x in upvote_score:
            if upvote_count == count:
                posts[c.text.strip()] = float(x.text.strip()[0:-1])
                count += 1
                break
            else:
                upvote_count += 1

    # for x in posts.keys():
    #     print(str(posts[x]) + 'k UPVOTES: ' + x)

    post_titles = []
    upvote_counts = []
    new_upvotes = []

    for x in posts.keys():
        post_titles.append(x)
        upvote_counts.append(posts[x])

    for item in upvote_counts:
        new_item = int(item * 1000)
        new_upvotes.append(new_item)

    data = [go.Bar(
            x = post_titles,
            y = new_upvotes,
            marker = dict(
                color = 'rgb(0, 255, 148)',
                line = dict(
                    color = 'rgb(0, 0, 0)',
                    width = 1),
            ),
        )]

    layout = go.Layout(
            title = "Upvotes Counts for Reddit's 'Top' Page Posts",
            xaxis = dict(
                title = "Post Preview",
                tickangle = 45,
                tickfont = dict(
                    size = 10,
                    color = 'rgb(0, 0, 0)'
                )
            ),
            yaxis = dict(
                title = "Post's Upvote Count (Today)",
                titlefont = dict(
                    size = 14,
                    color = 'rgb(0, 0, 0)'
                ),
                tickfont = dict(
                    size = 12,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

    print('Generating Bar Chart...')
    display = go.Figure(data = data, layout = layout)
    py.offline.plot(display, filename = "topposts.html")

def bar_chart():
    subreddit_names = []
    sub_scores = []

    statement = "SELECT Subreddits.Name, sum(Posts.Score) FROM Posts INNER JOIN Subreddits ON Subreddits.Name = Posts.Subreddit_Name GROUP BY Subreddits.Name ORDER BY sum(Posts.score) DESC"

    cur.execute(statement)
    subdic = cur.fetchall()

    for subreddit in subdic:
        subreddit_names.append(subreddit[0])
        sub_scores.append(subreddit[1])

    data = [go.Bar(
            x = subreddit_names,
            y = sub_scores,
            marker = dict(
                color = 'rgb(0, 177, 255)',
                line = dict(
                    color = 'rgb(0, 0, 0)',
                    width = 1),
            ),
        )]

    layout = go.Layout(
            title = "Comparing Summed Upvotes Amongst Reddit's Most Popular Subreddits",
            xaxis = dict(
                title = "Subreddit Name",
                tickangle = 45,
                tickfont = dict(
                    size = 10,
                    color = 'rgb(0, 0, 0)'
                )
            ),
            yaxis = dict(
                title = "Today's Aggregated Popularity Score (Based on Upvote Score Values)",
                titlefont = dict(
                    size = 14,
                    color = 'rgb(0, 0, 0)'
                ),
                tickfont = dict(
                    size = 12,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

    print('Generating Bar Chart...')
    display = go.Figure(data = data, layout = layout)
    py.offline.plot(display, filename = "upvotebar.html")

def bar_chart2():
    subreddit_names = []
    gilded_subs = []

    statement = "SELECT Subreddits.Name, Posts.Gilded FROM Posts INNER JOIN Subreddits ON Subreddits.Name = Posts.Subreddit_Name WHERE Posts.Gilded > 0 GROUP BY Subreddits.Name ORDER BY Posts.Gilded ASC"

    cur.execute(statement)
    subdic = cur.fetchall()

    for subreddit in subdic:
        subreddit_names.append(subreddit[0])
        gilded_subs.append(subreddit[1])

    data = [go.Bar(
            x = subreddit_names,
            y = gilded_subs,
            marker = dict(
                color = 'rgb(148, 103, 189)',
                line = dict(
                    color = 'rgb(0, 0, 0)',
                    width = 1),
            ),
        )]

    layout = go.Layout(
            title = "Today's Popular Subreddits with Gilded Posts",
            xaxis = dict(
                title = "Subreddit Name",
                tickangle = 45,
                tickfont = dict(
                    size = 10,
                    color = 'rgb(0, 0, 0)'
                )
            ),
            yaxis = dict(
                title = "Today's Aggregated Popularity Score (Based on Gilded Values)",
                titlefont = dict(
                    size = 14,
                    color = 'rgb(0, 0, 0)'
                ),
                tickfont = dict(
                    size = 12,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

    print('Generating Bar Chart...')
    display = go.Figure(data = data, layout = layout)
    py.offline.plot(display, filename = "gildedbar.html")

def scatterplot():
    subreddit_names = []
    sub_scores = []

    statement = "SELECT Subreddits.Name, sum(Posts.Score) FROM Posts INNER JOIN Subreddits ON Subreddits.Name = Posts.Subreddit_Name GROUP BY Subreddits.Name ORDER BY sum(Posts.Score) DESC"

    cur.execute(statement)
    subdic = cur.fetchall()

    for subreddit in subdic:
        subreddit_names.append(subreddit[0])
        sub_scores.append(subreddit[1])

    data = [go.Scatter(
            x = subreddit_names,
            y = sub_scores,
            marker = dict(
                color = 'rgb(0, 177, 255)',
                size = 10
            ),
            line = dict(
                color = 'rgb(200, 200, 200)',
                width = 4
            ),
            mode = 'markers+lines'
        )]
    layout = go.Layout(
            title = "Comparing Summed Upvotes Amongst Reddit's Most Popular Subreddits",
            xaxis = dict(
                title = "Subreddit Name",
                tickangle = 45,
                tickfont = dict(
                    color = 'rgb(0, 0, 0)'
                )
            ),
            yaxis = dict(
                title = "Today's Aggregated Popularity Score (Based on Upvote Score Values)",
                titlefont = dict(
                    size = 14,
                    color = 'rgb(0, 0, 0)'
                ),
                tickfont = dict(
                    size = 12,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

    print('Generating Scatterplot...')
    display = go.Figure(data = data, layout = layout)
    py.offline.plot(display, filename = "upvotescatter.html")

def scatterplot2():
    subreddit_names = []
    gilded_subs = []

    statement = "SELECT Subreddits.Name, Posts.Gilded FROM Posts INNER JOIN Subreddits ON Subreddits.Name = Posts.Subreddit_Name WHERE Posts.Gilded > 0 GROUP BY Subreddits.Name ORDER BY Posts.Gilded ASC"

    cur.execute(statement)
    subdic = cur.fetchall()

    for subreddit in subdic:
        subreddit_names.append(subreddit[0])
        gilded_subs.append(subreddit[1])

    data = [go.Scatter(
            x = subreddit_names,
            y = gilded_subs,
            marker = dict(
                color = 'rgb(148, 103, 189)',
                size = 10
            ),
            line = dict(
                color = 'rgb(200, 200, 200)',
                width = 4
            ),
            mode = 'markers+lines'
        )]
    layout = go.Layout(
            title = "Today's Popular Subreddits with Gilded Posts",
            xaxis = dict(
                title = "Subreddit Name",
                tickangle = 45,
                tickfont = dict(
                    color = 'rgb(0, 0, 0)'
                )
            ),
            yaxis = dict(
                title = "Today's Aggregated Popularity Score (Based on Gilded Values)",
                titlefont = dict(
                    size = 14,
                    color = 'rgb(0, 0, 0)'
                ),
                tickfont = dict(
                    size = 12,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )
    print('Generating Scatterplot...')
    display = go.Figure(data = data, layout = layout)
    py.offline.plot(display, filename = "gildedscatter.html")

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = input("Fetch new or cached data? new/cached: ")

    if response == "new":
        get_reddit_auth()
        search_populars()

    elif response == "cached":
        check_cache()
        get_reddit_auth()
        search_populars()

    response1 = input("Enter command (or 'help' for options): ")

    while response1 != 'exit':

        if response1 == 'help':
            print(help_text)

        if response1 == 'top posts':
            get_top_posts()

        if response1 == 'bar chart upvotes':
            bar_chart()

        if response1 == 'bar chart gilded':
            bar_chart2()

        if response1 == 'scatterplot upvotes':
            scatterplot()

        if response1 == "scatterplot gilded":
            scatterplot2()
            
        if 'top' not in response1:
            if 'bar' not in response1:
                if 'scatterplot' not in response1:
                    print('Command not recognized. Please try again (or "help" for options): ')

        if response1 == 'exit':
            print('Bye!')
            break

        response1 = input("Enter command (or 'help' for options): ")

if __name__ == "__main__":
    interactive_prompt()
