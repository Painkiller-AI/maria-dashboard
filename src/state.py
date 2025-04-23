import streamlit as st

from shared.schemas.user_profile_schema import UserProfileSchema


class State:
    @property
    def user(self) -> UserProfileSchema | None:
        return st.session_state.user if "user" in st.session_state else None

    @user.setter
    def user(self, user: UserProfileSchema | None):
        st.session_state.user = user


app_state = State()
