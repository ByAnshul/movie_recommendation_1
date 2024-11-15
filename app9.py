import streamlit as st
import requests
import random

# Set page configuration
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# CSS for custom styling
st.markdown("""
    <style>
    /* Center the main title */
    .title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #FF6347;
    }
    
    /* Style buttons with transitions */
    .stButton > button {
        background-color: red; /* Green */
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        transition-duration: 0.4s;
        cursor: pointer;
    }

    .stButton > button:hover {
        background-color: white;
        color: black;
        border: 2px solid #4CAF50;
    }

    /* Hover effect on all movie images */
    .movie-poster-container img:hover {
        transform: scale(1.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }

    /* Center content within columns */
    .column-content {
        text-align: center;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Display title
st.markdown('<div class="title">Movie Recommendation System</div>', unsafe_allow_html=True)

# API key placeholder (replace with your actual key)
api_key = "82efcebe55225281776f08ab5ee37fe2"

# Function to fetch a random movie
def fetch_random_movie():
    random_id = random.randint(1, 100000)  # Adjust the range as needed
    random_movie_url = f"https://api.themoviedb.org/3/movie/{random_id}?api_key={api_key}&append_to_response=videos"
    response = requests.get(random_movie_url)
    if response.status_code == 200:
        return response.json()
    return None

# Initialize session states
if 'selected_movie' not in st.session_state:
    st.session_state['selected_movie'] = None
if 'show_recommendations' not in st.session_state:
    st.session_state['show_recommendations'] = False

# Combined input box for movie search and selection
query = st.text_input("Enter or Select a Movie:", value="")
if query:
    # API call to search for the movie
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
    search_response = requests.get(search_url)

    if search_response.status_code == 200:
        movie_data = search_response.json().get('results', [])
    else:
        st.error("Error fetching movie data.")
        movie_data = []

    # Dropdown to select a movie from search results
    if movie_data:
        selected_title = st.selectbox("Select a movie", movie_data, format_func=lambda x: x['title'])
        st.session_state['selected_movie'] = selected_title

    # Random movie button
    if st.button("Random Movie"):
        random_movie = fetch_random_movie()
        if random_movie:
            st.session_state['selected_movie'] = random_movie
        else:
            st.error("Error fetching a random movie.")

# Display selected movie details
if st.session_state['selected_movie']:
    selected_movie = st.session_state['selected_movie']
    movie_id = selected_movie['id']
    movie_detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=videos"
    movie_detail_response = requests.get(movie_detail_url)

    if movie_detail_response.status_code == 200:
        movie_detail = movie_detail_response.json()

        # Display movie details
        st.subheader(movie_detail.get('title', 'Movie Title'))
        st.subheader(movie_detail.get('tagline', 'Movie Tagline'))

        # HTML container for image to apply hover effect
        poster_url = f"https://image.tmdb.org/t/p/w500{movie_detail.get('poster_path', '')}"
        st.markdown(f'<div class="movie-poster-container"><img src="{poster_url}" width="300" /></div>', unsafe_allow_html=True)

        st.write(f"**Overview:** {movie_detail.get('overview', 'Overview not available.')}")
        st.write(f"**Genres:** {', '.join([genre['name'] for genre in movie_detail.get('genres', [])])}")
        st.write(f"**Release Date:** {movie_detail.get('release_date', 'N/A')}")
        st.write(f"**Runtime:** {movie_detail.get('runtime', 'N/A')} minutes")
        st.write(f"**Vote Average:** {movie_detail.get('vote_average', 'N/A')} ({movie_detail.get('vote_count', 0)} votes)")

        # Videos section
        videos = movie_detail.get('videos', {}).get('results', [])
        if videos:
            st.write("**Videos/Trailers:**")
            for video in videos:
                video_link = f"https://www.youtube.com/watch?v={video['key']}"
                st.markdown(f"- [{video['name']}]({video_link})")
        else:
            st.write("No videos available for this movie.")

    # Recommendations button
    if st.button("Show Recommendations"):
        st.session_state['show_recommendations'] = True

    # Display recommendations
    if st.session_state['show_recommendations']:
        recommendations_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}"
        recommendations_response = requests.get(recommendations_url)

        if recommendations_response.status_code == 200:
            recommendations_data = recommendations_response.json().get('results', [])
        else:
            st.error("Error fetching recommendations.")
            recommendations_data = []

        if recommendations_data:
            st.write("### Movie Recommendations:")
            # Display in a 3-column layout
            cols = st.columns(3)
            for idx, movie in enumerate(recommendations_data):
                with cols[idx % 3]:
                    poster_url = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}"
                    st.markdown(f'<div class="movie-poster-container"><img src="{poster_url}" width="150" /></div>', unsafe_allow_html=True)
                    st.write(f"**{movie.get('title', 'N/A')}**")
                    st.write(f"Release Date: {movie.get('release_date', 'N/A')}")
                    st.write(f"Rating: {movie.get('vote_average', 'N/A')}")
                    st.write(f"Overview: {movie.get('overview', 'N/A')[:100]}...")

        else:
            st.write("No recommendations available.")
else:
    st.write("Please enter a movie name to search.")
