import requests
import pandas as pd

# Function to get Spotify access token
def get_spotify_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_data = auth_response.json()
    return auth_data['access_token']

# Function to search for a track and get its ID
def search_track(track_name, artist_name, token):
    query = f"{track_name} artist:{artist_name}"
    url = f"https://api.spotify.com/v1/search?q={query}&type=track"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    try:
        first_result = json_data['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except (KeyError, IndexError):
        return None

# Function to get track details (album image URL)
def get_track_details(track_id, token):
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })
    json_data = response.json()
    try:
        image_url = json_data['album']['images'][0]['url']
        return image_url
    except (KeyError, IndexError):
        return 'Not found'

# Your Spotify API credentials
client_id = '029cfd80e0314cb28848a899c4e24c5e'
client_secret = '52b4d3a3cea44542891e441d983fff39'

# Get access token
access_token = get_spotify_token(client_id, client_secret)
print("✅ Access token obtained!")

# Read your DataFrame
df_spotify = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')

# Print out column names to confirm
print("✅ Available columns:", df_spotify.columns.tolist())

# Use correct column names based on your CSV
track_col = 'track_name'
artist_col = 'artist(s)_name'

# Add new column for image URLs if not present
if 'image_url' not in df_spotify.columns:
    df_spotify['image_url'] = ''

# Loop through rows to get track details
for i, row in df_spotify.iterrows():
    track_name = row[track_col]
    artist_name = row[artist_col]
    
    # Basic check to skip missing data
    if pd.isna(track_name) or pd.isna(artist_name):
        df_spotify.at[i, 'image_url'] = 'Missing data'
        continue
    
    track_id = search_track(track_name, artist_name, access_token)
    if track_id:
        image_url = get_track_details(track_id, access_token)
        df_spotify.at[i, 'image_url'] = image_url
    else:
        df_spotify.at[i, 'image_url'] = 'Not found'
    
    # Optional: show progress every 50 rows
    if (i + 1) % 50 == 0:
        print(f"✅ Processed {i + 1}/{len(df_spotify)} rows...")

# Save updated DataFrame
df_spotify.to_csv('updated_file.csv', index=False)
print("✅ Updated CSV saved as 'updated_file.csv'!")
