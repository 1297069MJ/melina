]from __future__ import annotations

import ast
import io
import math
import re
from datetime import date
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import streamlit as st
import sympy as sp

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
)

st.set_page_config(page_title="Hispanic Heritage Historical Data Explorer",
                   page_icon="📊", layout="wide")

# Local, built-in theme choices: no image files or external assets are required.
FONT_OPTIONS = {
    "Nunito (soft + rounded)": ("Nunito", "Nunito:wght@400;600;700;800"),
    "Poppins (cute + modern)": ("Poppins", "Poppins:wght@400;500;600;700;800"),
    "Quicksand (playful)": ("Quicksand", "Quicksand:wght@400;500;600;700"),
    "Playfair Display (elegant)": ("Playfair Display", "Playfair+Display:wght@400;500;600;700"),
    "Lora (classic)": ("Lora", "Lora:wght@400;500;600;700"),
}
BACKGROUND_OPTIONS = {
    "Cotton candy": ("#fff0f6", "#f3e8ff", "#fff7ed", "#7c3aed"),
    "Sage garden": ("#edf7ef", "#e4f1e8", "#f7f8ed", "#28704a"),
    "Peach lemonade": ("#fff1e6", "#ffe8d6", "#fff8e7", "#b45309"),
    "Lavender sky": ("#f1edff", "#e9e7ff", "#f7f3ff", "#6d5bd0"),
    "Ocean breeze": ("#e8f6fb", "#e6f0ff", "#f3fbff", "#176b87"),
    "Clean paper": ("#f8fafc", "#f1f5f9", "#ffffff", "#475569"),
}

# Spanish-speaking sovereign countries (20), Puerto Rico as a territory,
# and Brazil as a non-Hispanic Latin American comparison.
COUNTRIES = {
    "Argentina": "ARG", "Bolivia": "BOL", "Chile": "CHL",
    "Colombia": "COL", "Costa Rica": "CRI", "Cuba": "CUB",
    "Dominican Republic": "DOM", "Ecuador": "ECU", "El Salvador": "SLV",
    "Equatorial Guinea": "GNQ", "Guatemala": "GTM", "Honduras": "HND",
    "Mexico": "MEX", "Nicaragua": "NIC", "Panama": "PAN",
    "Paraguay": "PRY", "Peru": "PER", "Spain": "ESP",
    "Uruguay": "URY", "Venezuela": "VEN",
    "Puerto Rico (territory)": "PRI",
    "Brazil (Latin American comparison; not Hispanic)": "BRA",
}

INDICATORS = {
    "Life expectancy at birth": ("SP.DYN.LE00.IN", "years", "Average number of years a newborn is expected to live if current age-specific mortality rates persist.", "nonnegative"),
    "Unemployment, national estimate": ("SL.UEM.TOTL.NE.ZS", "% of labor force", "Share of the labor force that is unemployed, using national estimates.", "percent"),
    "GDP per capita": ("NY.GDP.PCAP.CD", "current US$ per person", "Gross domestic product divided by midyear population. This is not average wealth or household income.", "nonnegative"),
    "Crude birth rate": ("SP.DYN.CBRT.IN", "births per 1,000 people per year", "Annual live births per 1,000 people; this is a rate, not a birth count.", "nonnegative"),
    "Net migration": ("SM.POP.NETM", "people", "Net number of migrants (immigrants minus emigrants) over the period; it is not an emigration count.", "any"),
    "Intentional homicide rate": ("VC.IHR.PSRC.P5", "per 100,000 people", "Intentional homicides per 100,000 people.", "nonnegative"),
    "Consumer price inflation": ("FP.CPI.TOTL.ZG", "% annual", "Annual percentage change in the consumer price index.", "any"),
    "Central government debt": ("GC.DOD.TOTL.GD.ZS", "% of GDP", "Central government debt as a percentage of GDP.", "nonnegative"),
    "Total reserves including gold": ("FI.RES.TOTL.CD", "current US$", "Total reserves including gold, in current US dollars.", "nonnegative"),
    "External balance on goods and services": ("NE.RSB.GNFS.ZS", "% of GDP", "External balance on goods and services as a percentage of GDP.", "any"),
}

CONTEXTS = {
    "Business": ("revenue", "dollars", "time", "years", "a business revenue model"),
    "Engineering": ("displacement", "meters", "time", "seconds", "an engineering motion model"),
    "Medical": ("concentration", "mg/L", "time", "hours", "a simplified concentration model (not medical advice)"),
    "Sports science": ("distance", "meters", "time", "seconds", "a sports performance model"),
    "Biology": ("population", "organisms", "time", "days", "a population model"),
    "Bioengineering": ("cell_count", "cells", "time", "hours", "a bioengineering model"),
    "Economic forecasting": ("index", "index points", "time", "years", "an economic indicator model"),
    "Weather": ("temperature", "°C", "time", "days", "a weather trend model"),
    "Custom": ("y", "units", "x", "units", "a custom model"),
}
SUGGESTED_FUNCTIONS = {
    "Business": "a*x**2 + b*x + c",
    "Engineering": "a*sin(b*x) + c",
    "Medical": "a*exp(-b*x) + c",
    "Sports science": "a*x + b",
    "Biology": "a*exp(b*x)",
    "Bioengineering": "a*x**2 + b*x + c",
    "Economic forecasting": "a*x**2 + b*x + c",
    "Weather": "a*sin(b*x) + c",
    "Custom": "a*x + b",
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_world_bank(country_code: str, indicator_code: str, start_year: int, end_year: int) -> pd.DataFrame:
    """Retrieve World Bank annual observations. Empty results remain empty; no synthetic data."""
