import requests
import streamlit as st


API_URL = "http://localhost:8000"


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬"
)

st.title("🎬 Movie Recommender")

user_id = st.number_input(
    "Enter User ID",
    min_value=1,
    value=101,
    step=1
)


if st.button("Get Recommendations"):

    response = requests.get(
        f"{API_URL}/recommend/user/{user_id}"
    )

    if response.status_code == 200:

        data = response.json()

        recommendations = data.get(
            "recommendations",
            []
        )

        st.subheader("Recommended Movies")

        for movie in recommendations:

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
                            "user_id": user_id,
                            "movie_id": movie["movieId"]
                        }
                    )

                    if watch_response.status_code == 200:

                        st.success(
                            "Watch recorded!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            watch_response.text
                        )

    else:

        st.error(
            f"Error: {response.text}"
        )