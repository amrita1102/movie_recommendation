import requests
import streamlit as st


API_URL = "http://localhost:8000"


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

    response = requests.get(
        f"{API_URL}/recommend/user/{user_id}"
    )

    if response.status_code == 200:

        data = response.json()

        st.session_state.recommendations = (
            data.get(
                "recommendations",
                []
            )
        )

    else:

        st.error(
            f"Error: {response.text}"
        )


# --------------------------------
# Recommendations
# --------------------------------

if st.session_state.recommendations is not None:

    st.subheader("Recommended Movies")

    for movie in st.session_state.recommendations:

        col1, col2 = st.columns(
            [4, 1]
        )

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

                    # Remove the watched movie
                    # immediately from the current UI
                    st.session_state.recommendations = [
                        m
                        for m in st.session_state.recommendations
                        if m["movieId"] != movie["movieId"]
                    ]

                    st.success(
                        "Watch recorded!"
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