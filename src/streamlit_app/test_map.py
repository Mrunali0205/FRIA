import streamlit as st
import folium
from streamlit_folium import st_folium

st.write("Test Map")

m = folium.Map(location=[41.88, -87.63], zoom_start=12)
st_folium(m)