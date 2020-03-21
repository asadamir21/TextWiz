
from collections import defaultdict
import json
import pandas as pd

import requests

YOUTUBE_COMMENT_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

def openURL(URL, params):
    r = requests.get(URL + "?", params=params)
    return r.text

class VideoComment:
    def __init__(self, maxResults, videoId, key):
        self.comments = []
        self.replies = defaultdict(list)
        self.params = {
                    'part': 'snippet,replies',
                    'maxResults': maxResults,
                    'videoId': videoId,
                    'textFormat': 'plainText',
                    'key': key
                }

        self.get_video_comments()


    def load_comments(self, mat):
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            #self.comments["id"].append(comment["id"])
            row = []
            row.append(comment["snippet"]["textDisplay"])
            row.append(comment["snippet"]["authorDisplayName"])
            row.append(comment["snippet"]["likeCount"])
            row.append(comment["snippet"]["publishedAt"])

            self.comments.append(row)
            # if 'replies' in item.keys():
            #     for reply in item['replies']['comments']:
            #         self.replies["parentId"].append(reply["snippet"]["parentId"])
            #         self.replies["authorDisplayName"].append(reply['snippet']['authorDisplayName'])
            #         self.replies["replyComment"].append(reply["snippet"]["textDisplay"])
            #         self.replies["publishedAt"].append(reply["snippet"]["publishedAt"])
            #         self.replies["likeCount"].append(reply["snippet"]["likeCount"])

    def get_video_comments(self):
        url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
        nextPageToken = url_response.get("nextPageToken")
        self.load_comments(url_response)

        while nextPageToken:
            self.params.update({'pageToken': nextPageToken})
            url_response = json.loads(openURL(YOUTUBE_COMMENT_URL, self.params))
            nextPageToken = url_response.get("nextPageToken")
            self.load_comments(url_response)




