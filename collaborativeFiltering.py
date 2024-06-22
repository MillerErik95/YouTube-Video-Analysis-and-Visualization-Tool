from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import networkx as nx
import matplotlib.pyplot as plt
import os
import pickle
from sklearn.neighbors import NearestNeighbors
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
                'client_secret.json', scopes=scopes)
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
        maxResults=20  # Adjust as needed
    )
    playlist_response = playlist_request.execute()

    # Fetch details and statistics for each video
    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
    video_request = youtube.videos().list(
        part="snippet,statistics",
        id=','.join(video_ids)
    )
    video_response = video_request.execute()

    videos = []
    for item in video_response['items']:
        stats = item['statistics']
        video = {
            'id': item['id'],
            'title': item['snippet']['title'],
            'viewCount': int(stats.get('viewCount', 0)),
            'likeCount': int(stats.get('likeCount', 0)),
            'commentCount': int(stats.get('commentCount', 0)),
        }
        videos.append(video)

    return videos

def create_and_visualize_graph(videos, model, feature_matrix):
    # Create the graph
    G = nx.Graph()
    for video in videos:
        G.add_node(video['id'], label=video['title'])

    # Use the NearestNeighbors model to find edges between similar videos
    for i, _ in enumerate(videos):
        distances, indices = model.kneighbors(feature_matrix[i].reshape(1, -1), n_neighbors=5)
        for j in indices.flatten()[1:]:  # The first index is the video itself
            if i != j:  # Make sure not to connect the video to itself
                G.add_edge(videos[i]['id'], videos[j]['id'])

    # Visualize the graph
    plt.figure(figsize=(24, 24))  # Increase figure size
    pos = nx.spring_layout(G, k=0.75, iterations=100)  # May need to adjust k for optimal spacing

    nx.draw_networkx_nodes(G, pos, node_size=100, node_color="lightblue", alpha=0.7)
    # Draw only edges without weights for simplicity
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='blue', width=1)
    
    # Draw labels
    labels = {node: G.nodes[node]['label'] for node in G.nodes()}
    label_options = {
        'font_size': 8,
        'alpha': 0.7,
        'bbox': {'boxstyle': 'round,pad=0.5', 'fc': 'white', 'ec': 'black', 'alpha': 0.5}
    }
    nx.draw_networkx_labels(G, pos, labels, **label_options)

    plt.axis('off')
    plt.show()
    
def collaborative_filtering(videos):
    # Create a feature matrix using view, like, and comment counts
    feature_matrix = np.array([[video['viewCount'], video['likeCount'], video['commentCount']] for video in videos])
    
    # Normalize the feature matrix
    feature_matrix_normalized = feature_matrix / np.linalg.norm(feature_matrix, axis=0)
    
    # Apply NearestNeighbors for item-based collaborative filtering
    model = NearestNeighbors(n_neighbors=5, metric='cosine', algorithm='brute')
    model.fit(feature_matrix_normalized)
    
    return model, feature_matrix_normalized

if __name__ == "__main__":
    videos = main()
    model, feature_matrix_normalized = collaborative_filtering(videos)
    create_and_visualize_graph(videos, model, feature_matrix_normalized)

    # Example of finding similar videos for the first video in the list
    distances, indices = model.kneighbors(feature_matrix_normalized[0].reshape(1, -1))
    similar_video_indices = indices.flatten()[1:]  # Exclude the first index which is the video itself

    print(f"Videos similar to '{videos[0]['title']}':")
    for idx in similar_video_indices:
        print(f"{videos[idx]['title']} - Views: {videos[idx]['viewCount']}, Likes: {videos[idx]['likeCount']}, Comments: {videos[idx]['commentCount']}")

    # Create and visualize the graph
    create_and_visualize_graph(videos, feature_matrix_normalized)