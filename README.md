Title:
YouTube Video Analysis and Visualization Tool

Summary:
This Python program leverages the YouTube Data API to analyze videos from a user's channel. It performs collaborative filtering to find similar videos based on view counts, like counts, and comment counts. The program then visualizes these relationships using a graph.

Key Features:
Google API Authentication:

Uses OAuth 2.0 to authenticate with the YouTube Data API.
Saves and loads API credentials to and from a local file (token.pickle).
Data Fetching:

Retrieves the uploads playlist ID from the authenticated user's YouTube channel.
Fetches details and statistics for videos in the uploads playlist, including view counts, like counts, and comment counts.
Collaborative Filtering:

Constructs a feature matrix using video statistics.
Normalizes the feature matrix for consistent scaling.
Applies the NearestNeighbors model to find similar videos based on cosine similarity.
Graph Visualization:

Builds a graph using NetworkX where nodes represent videos and edges represent similarity based on the collaborative filtering model.
Visualizes the graph with Matplotlib, including video titles as labels and optimized layout for better clarity.
Usage:
Setup:

Ensure you have a client_secret.json file for Google API authentication.
Install required Python packages: google-auth-oauthlib, google-api-python-client, networkx, matplotlib, scikit-learn.
Run the Program:

Execute the script. It will prompt for Google authentication if necessary, fetch video data, perform collaborative filtering, and visualize the graph.
Output:

The program prints a list of videos similar to the first video in the list.
Displays a graph visualization of video similarities using NetworkX and Matplotlib.
Example:
bash
Copy code
$ python script.py
Output:

yaml
Copy code
Videos similar to 'Video Title 1':
Video Title 2 - Views: 123, Likes: 45, Comments: 6
Video Title 3 - Views: 456, Likes: 78, Comments: 9
...
A graph visualization window will open showing the relationships between similar videos.

This program is useful for YouTube content creators and analysts who want to explore and visualize the relationships between videos on their channel based on viewer engagement metrics.
