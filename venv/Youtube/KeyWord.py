import os
import pickle

import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "Youtube/client_secret.json" #This is the name of your JSON file

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    credentials = None
    if os.path.exists('Youtube/token.pickle'):
        with open('Youtube/token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    #  Check if the credentials are invalid or do not exist
    if not credentials or not credentials.valid:
        # Check if the credentials have expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_console()

        # Save the credentials for the next run
        with open('Youtube/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
service = get_authenticated_service()


def retreiveComments(query):
    # =============================================================================
    # Search Query Initialisation
    # =============================================================================

    query_results = service.search().list(
            part = 'snippet',
            q = query,
            order = 'relevance', # You can consider using viewCount
            maxResults = 20,
            type = 'video', # Channels might appear in search results
            relevanceLanguage = 'en',
            safeSearch = 'moderate',
            ).execute()

    # =============================================================================
    # Get Video IDs
    # =============================================================================
    video_id = []
    channel = []
    video_title = []
    video_desc = []
    for item in query_results['items']:
        video_id.append(item['id']['videoId'])
        channel.append(item['snippet']['channelTitle'])
        video_title.append(item['snippet']['title'])
        video_desc.append(item['snippet']['description'])

    # =============================================================================
    # Get Comments of Top Videos
    # =============================================================================
    video_id_pop = []
    channel_pop = []
    video_title_pop = []
    video_desc_pop = []
    comments_pop = []
    comment_id_pop = []
    reply_count_pop = []
    like_count_pop = []

    from tqdm import tqdm

    for i, video in enumerate(tqdm(video_id, ncols=100)):
        response = service.commentThreads().list(
            part='snippet',
            videoId=video,
            maxResults=100,  # Only take top 100 comments...
            order='relevance',  # ... ranked on relevance
            textFormat='plainText',
        ).execute()

        comments_temp = []
        comment_id_temp = []
        reply_count_temp = []
        like_count_temp = []
        for item in response['items']:
            comments_temp.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            comment_id_temp.append(item['snippet']['topLevelComment']['id'])
            reply_count_temp.append(item['snippet']['totalReplyCount'])
            like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
        comments_pop.extend(comments_temp)
        comment_id_pop.extend(comment_id_temp)
        reply_count_pop.extend(reply_count_temp)
        like_count_pop.extend(like_count_temp)

        video_id_pop.extend([video_id[i]] * len(comments_temp))
        channel_pop.extend([channel[i]] * len(comments_temp))
        video_title_pop.extend([video_title[i]] * len(comments_temp))
        video_desc_pop.extend([video_desc[i]] * len(comments_temp))

    query_pop = [query] * len(video_id_pop)

    # =============================================================================
    # Populate to Dataframe
    # =============================================================================
    import pandas as pd

    output_dict = {
            #'Query': query_pop,
            'Comment': comments_pop,
            'Video Link': video_id_pop,
            'Video Title': video_title_pop,
            'Video Description': video_desc_pop,
            'Channel': channel_pop,
            'Replies': reply_count_pop,
            'Likes': like_count_pop,
            }
    output_df = pd.DataFrame(output_dict, columns = output_dict.keys())
    return output_df.values.tolist()


