from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np

# Scopes required by your application
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# Saves API credentials
def save_credentials(credentials):
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)
        
# Loads API credentials
def load_credentials():
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            return pickle.load(token)
    return None

def main():
    credentials = load_credentials()
# Checks API credentials
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'c:/Users/Mille/OneDrive/Desktop/School/Social Networking and Infomatics/Final/client_secret.json', scopes=scopes)
            credentials = flow.run_local_server(port=0)
        save_credentials(credentials)

    # Build the service object
    youtube = build('youtube', 'v3', credentials=credentials)

    # Fetch the uploads playlist ID from your channel
    channel_request = youtube.channels().list(
        part="contentDetails",
        mine=True
    )
    channel_response = channel_request.execute()
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Fetch videos from the uploads playlist
    playlist_request = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part="snippet",
        maxResults=10  # Adjust as needed
    )
    playlist_response = playlist_request.execute()

     # Process and return the video data
    videos = []
    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]

    # Fetch details for each video
    video_request = youtube.videos().list(
        part="snippet",
        id=','.join(video_ids)
    )
    video_response = video_request.execute()

    for item in video_response['items']:
        video = {
            'id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'tags': ','.join(item['snippet'].get('tags', []))  # Tags are now included as a comma-separated string
        }
        videos.append(video)

    return videos

videos = main()

# Process text data and compute similarities
def compute_similarities(videos):
    # Combine title, tags, and description for each video into a single string
    corpus = [' '.join([v['title'], v['tags'], v['description']]) for v in videos]
    # Use TF-IDF vectorizer to convert text data into vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    # Compute cosine similarity between all video vectors
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

# Create and visualize a graph based on similarities
def create_and_visualize_graph(videos, similarity_matrix, threshold=0.2):
    G = nx.Graph()
    for i, video in enumerate(videos):
        G.add_node(video['id'], title=video['title'])

    # Add edges between videos with a similarity above the threshold
    for i in range(len(videos)):
        for j in range(i+1, len(videos)):
            if similarity_matrix[i, j] > threshold:
                G.add_edge(videos[i]['id'], videos[j]['id'], weight=similarity_matrix[i, j])

    # Visualize the graph
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'title')
    edge_weights = [G[u][v]['weight'] for u,v in G.edges()]
    
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=1000, node_color="lightblue",
            font_size=8, edge_color=edge_weights, edge_cmap=plt.cm.Blues, width=2)
    
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    videos = main()
    similarity_matrix = compute_similarities(videos)
    create_and_visualize_graph(videos, similarity_matrix)