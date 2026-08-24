import requests
import streamlit as st
import os

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000"
)


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬"
)

st.title("🎬 Movie Recommender")


# --------------------------------
# Session state
# --------------------------------

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# --------------------------------
# Helper: get recommendations
# --------------------------------

def load_recommendations(user_id):

    response = requests.get(
        f"{API_URL}/recommend/user/{user_id}"
    )

    if response.status_code == 200:

        data = response.json()

        st.session_state.recommendations = (
            data.get("recommendations", [])
        )

        st.session_state.current_user = user_id

        return True

    st.error(
        f"Recommendation error: {response.text}"
    )

    return False


# --------------------------------
# User
# --------------------------------

user_id = st.number_input(
    "Enter User ID",
    min_value=1,
    value=101,
    step=1
)


# --------------------------------
# Get recommendations
# --------------------------------

if st.button("Get Recommendations"):

    load_recommendations(
        int(user_id)
    )


# --------------------------------
# Recommendations
# --------------------------------

if (
    st.session_state.recommendations is not None
    and
    st.session_state.current_user == int(user_id)
):

    st.subheader("Recommended Movies")

    for movie in st.session_state.recommendations:

        col1, col2 = st.columns([4, 1])

        with col1:

            st.write(
                f"🎬 {movie['title']}"
            )

        with col2:

            if st.button(
                "Watched",
                key=f"watch_{movie['movieId']}"
            ):

                watch_response = requests.post(
                    f"{API_URL}/watch",
                    json={
                        "user_id": int(user_id),
                        "movie_id": int(
                            movie["movieId"]
                        )
                    }
                )

                if watch_response.status_code == 200:

                    st.success(
                        "Watch recorded!"
                    )

                    # --------------------------------
                    # IMPORTANT:
                    # Fetch completely fresh recommendations
                    # after MySQL + Redis have been updated.
                    # --------------------------------

                    load_recommendations(
                        int(user_id)
                    )

                    st.rerun()

                else:

                    st.error(
                        f"Watch failed: "
                        f"{watch_response.text}"
                    )


    # --------------------------------
    # Watch history
    # --------------------------------

    st.divider()

    st.subheader("📺 Watch History")

    history_response = requests.get(
        f"{API_URL}/users/{user_id}/history"
    )

    if history_response.status_code == 200:

        history = (
            history_response
            .json()
            .get("history", [])
        )

        if not history:

            st.info(
                "No watch history yet."
            )

        else:

            for event in history[:10]:

                st.write(
                    f"🎬 {event['title']} "
                    f"— {event['watchedAt'][:10]}"
                )

    else:

        st.error(
            history_response.text
        )