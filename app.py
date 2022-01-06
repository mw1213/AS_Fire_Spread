import streamlit as st
from src.symulation import animate_with_pltshow
import streamlit.components.v1 as components

wind_labels = {
    'South East': 0,
    'East': 1,
    'North East': 2,
    'North': 3,
    'North West': 4,
    'West': 5,
    'South West': 6,
    'South': 7,
    'No Wind': 8
}

st.sidebar.markdown('# Options')

interval = st.sidebar.slider('FPS', min_value=1, max_value=40, value=20)
frames = st.sidebar.slider('Frames', min_value=1, max_value=400, value=200)
wind_dir = st.sidebar.selectbox('Wind Direction', list(wind_labels.keys()))

if st.sidebar.button('Generate'):
    animation = animate_with_pltshow(frames=frames, wind_dir=wind_labels[wind_dir])
    components.html(animation.to_jshtml(fps=5), height=10000)
