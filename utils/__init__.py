"""
ChristLift Utilities Package
"""
import inspect
import streamlit as st

WIDTH_STRETCH = {"width": "stretch"} if "width" in inspect.signature(st.dataframe).parameters else {"use_container_width": True}
CHART_CONFIG = {"displayModeBar": "hover", "displaylogo": False}
