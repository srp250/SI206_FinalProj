import unittest
from final_project import *
import secrets
import json

class Test1(unittest.TestCase):
    def test_Credentials(self):
        self.assertNotEqual(CLIENT_ID, "", "Please fill in client_id in secrets file.")
        self.assertNotEqual(CLIENT_SECRET, "", "Please fill in client_secret in secrets file.")
        self.assertNotEqual(USERNAME, "", "Please fill in username in secrets file.")
        self.assertNotEqual(PASSWORD, "", "Please fill in client_secret in secrets file.")

class Test2(unittest.TestCase):
    def test_PostInstances(self):
        self.file = open("sample_post.json", "r")
        self.json = self.file.read()
        self.post_dict = json.loads(self.json)
        self.post_obj = Post(self.post_dict)
        self.file.close()

        self.assertIsInstance(self.post_obj.title, str)
        self.assertIsInstance(self.post_obj.score, int)
        self.assertIsInstance(self.post_obj.subreddit, str)
        self.assertIsInstance(self.post_obj.gilded, int)
        self.assertIsInstance(self.post_obj.time_created, float)
        self.file.close()

class Test3(unittest.TestCase):
    def test_RedditAuth(self):
        get_reddit_auth()
        self.request = make_request('art')
        self.post_dict = self.request['data']['children'][0]
        self.post_obj = Post(self.post_dict)
        self.assertEqual('Art', self.post_obj.subreddit)

    def test_TokenSave(self):
        self.token = open('creds.json')
        self.assertTrue(self.token.read())
        self.token.close()

class Test4(unittest.TestCase):
    def testPopulateDatabase(self):
        get_reddit_auth()
        response = get_data('art')
        self.assertNotEqual(response, None)

    def testScrapeTop(self):
        baseurl = 'https://www.reddit.com/top/'
        page_html = make_request_using_cache(baseurl)
        page_soup = BeautifulSoup(page_html, 'html.parser')
        content_div = page_soup.find(class_ = 'content')
        upvote_score = content_div.find_all(class_ = 'score unvoted')
        self.assertNotEqual(len(upvote_score), 0)

class Test5(unittest.TestCase):
    def test_UpvoteBar(self):
        self.file = open("upvotebar.html")
        self.read = self.file.read()
        self.assertTrue(self.read)
        self.file.close()

    def test_UpvoteScatter(self):
        self.file2 = open("upvotescatter.html")
        self.read = self.file2.read()
        self.assertTrue(self.read)
        self.file2.close()

    def test_GildedBar(self):
        self.file3 = open("gildedbar.html")
        self.read = self.file3.read()
        self.assertTrue(self.read)
        self.file3.close()

    def test_GildedScatter(self):
        self.file4 = open("gildedscatter.html")
        self.read = self.file4.read()
        self.assertTrue(self.read)
        self.file4.close()

    def test_TopPosts(self):
        self.file5 = open("topposts.html")
        self.read = self.file5.read()
        self.assertTrue(self.read)
        self.file5.close()

if __name__ == '__main__':
    unittest.main()
