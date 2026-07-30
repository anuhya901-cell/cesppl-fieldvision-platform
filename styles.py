"""Shared visual styling for the CESPPL FieldVision Platform."""

import streamlit as st


def apply_custom_styles() -> None:
    """Apply the professional green-and-white application theme."""

    st.markdown(
        """
        <style>
        :root {
            --fieldvision-green: #15803D;
            --fieldvision-green-dark: #166534;
            --fieldvision-green-soft: #DCFCE7;
            --fieldvision-background: #F6F8F7;
            --fieldvision-surface: #FFFFFF;
            --fieldvision-border: #E2E8E5;
            --fieldvision-text: #17211B;
            --fieldvision-muted: #647067;
            --fieldvision-shadow: 0 8px 24px rgba(21, 128, 61, 0.08);
        }

        html,
        body,
        [class*="css"] {
            font-family: "Segoe UI", Inter, Arial, sans-serif;
        }

        .stApp {
            background: var(--fieldvision-background);
            color: var(--fieldvision-text);
        }

        [data-testid="stAppViewContainer"] > .main {
            background: var(--fieldvision-background);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 2.3rem;
            padding-bottom: 3rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
        }

        h1, h2, h3 {
            color: var(--fieldvision-text);
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.15rem !important;
            font-weight: 750 !important;
            margin-bottom: 0.35rem !important;
        }

        h2 {
            font-weight: 700 !important;
        }

        h3 {
            font-weight: 650 !important;
        }

        p, label, .stCaption {
            color: var(--fieldvision-muted);
        }

        /* Keep the Streamlit header available for the sidebar control. */
        [data-testid="stHeader"] {
            background: rgba(246, 248, 247, 0.94);
            border-bottom: 1px solid rgba(226, 232, 229, 0.75);
        }

        /* Streamlit 1.60: small white hamburger with green lines */

        /* Expanded sidebar control */
        div[data-testid="stSidebarCollapseButton"] {
            position: absolute !important;
            top: 6px !important;
            right: 8px !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            align-items: center !important;
            justify-content: center !important;
            width: 28px !important;
            height: 28px !important;
            min-width: 28px !important;
            min-height: 28px !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #FFFFFF !important;
            border: 1px solid rgba(21, 128, 61, 0.10) !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            overflow: visible !important;
            z-index: 1000000 !important;
        }

        div[data-testid="stSidebarCollapseButton"] > button[kind="headerNoPadding"] {
            position: absolute !important;
            inset: 0 !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            align-items: center !important;
            justify-content: center !important;
            width: 28px !important;
            height: 28px !important;
            min-width: 28px !important;
            min-height: 28px !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #FFFFFF !important;
            border: 0 !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }

        /* Collapsed sidebar control */
        button[data-testid="stExpandSidebarButton"][kind="headerNoPadding"] {
            position: fixed !important;
            top: 6px !important;
            left: 8px !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            align-items: center !important;
            justify-content: center !important;
            width: 28px !important;
            height: 28px !important;
            min-width: 28px !important;
            min-height: 28px !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #FFFFFF !important;
            border: 1px solid rgba(21, 128, 61, 0.10) !important;
            border-radius: 6px !important;
            box-shadow: none !important;
            cursor: pointer !important;
            transform: none !important;
            overflow: hidden !important;
            z-index: 2147483647 !important;
        }

        /* Remove Streamlit's built-in arrow icon completely. */
        div[data-testid="stSidebarCollapseButton"] > button[kind="headerNoPadding"] > span,
        button[data-testid="stExpandSidebarButton"][kind="headerNoPadding"] > span,
        div[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
        button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            min-width: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        /* Three thin green lines, drawn directly with CSS. */
        div[data-testid="stSidebarCollapseButton"] > button[kind="headerNoPadding"]::before,
        button[data-testid="stExpandSidebarButton"][kind="headerNoPadding"]::before {
            content: "" !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 15px !important;
            height: 1.5px !important;
            background: var(--fieldvision-green) !important;
            border-radius: 2px !important;
            box-shadow:
                0 -4.5px 0 var(--fieldvision-green),
                0 4.5px 0 var(--fieldvision-green) !important;
            transform: translateY(0.25px) !important;
            pointer-events: none !important;
        }

        div[data-testid="stSidebarCollapseButton"]:hover,
        div[data-testid="stSidebarCollapseButton"] > button[kind="headerNoPadding"]:hover,
        button[data-testid="stExpandSidebarButton"][kind="headerNoPadding"]:hover {
            background: #F7FFF9 !important;
            border-color: rgba(21, 128, 61, 0.22) !important;
            box-shadow: none !important;
        }

        [data-testid="stToolbar"] {
            overflow: visible !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: var(--fieldvision-surface);
            border-right: 1px solid var(--fieldvision-border);
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.15rem;
        }

        .sidebar-brand {
            padding: 0.85rem 0.75rem 1rem;
            margin-bottom: 0.55rem;
            border-bottom: 1px solid var(--fieldvision-border);
        }

        .sidebar-brand__eyebrow {
            margin: 0 0 0.25rem;
            color: var(--fieldvision-green);
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.14em;
        }

        .sidebar-brand__title {
            margin: 0;
            color: var(--fieldvision-text);
            font-size: 1.18rem;
            font-weight: 760;
            line-height: 1.25;
        }

        .sidebar-brand__subtitle {
            margin: 0.35rem 0 0;
            color: var(--fieldvision-muted);
            font-size: 0.79rem;
            line-height: 1.4;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] > label {
            display: none;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
            gap: 0.42rem;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            min-height: 46px;
            padding: 0.72rem 0.8rem;
            border-radius: 10px;
            border: 1px solid transparent;
            transition: background 0.18s ease, border-color 0.18s ease,
                        transform 0.18s ease;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: #F0FDF4;
            border-color: #BBF7D0;
            transform: translateX(2px);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: var(--fieldvision-green-soft);
            border-color: #86EFAC;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
            color: var(--fieldvision-green-dark) !important;
            font-weight: 700;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        .sidebar-footer {
            margin-top: 1.1rem;
            padding: 0.9rem 0.75rem;
            border-radius: 10px;
            background: #F8FAF9;
            border: 1px solid var(--fieldvision-border);
            color: var(--fieldvision-muted);
            font-size: 0.75rem;
            line-height: 1.45;
        }

        /* White content panels */
        [data-testid="stFileUploader"],
        [data-testid="stDataFrame"],
        [data-testid="stExpander"],
        [data-testid="stAlert"],
        [data-testid="stPlotlyChart"],
        [data-testid="stImage"] {
            border-radius: 14px;
        }

        [data-testid="stFileUploader"] {
            padding: 1rem;
            background: var(--fieldvision-surface);
            border: 1.5px dashed #86EFAC;
            box-shadow: var(--fieldvision-shadow);
        }

        [data-testid="stFileUploaderDropzone"] {
            background: #F7FFF9;
            border: none;
            border-radius: 10px;
        }

        [data-testid="stMetric"] {
            min-height: 126px;
            padding: 1.05rem 1.15rem;
            background: var(--fieldvision-surface);
            border: 1px solid var(--fieldvision-border);
            border-top: 4px solid var(--fieldvision-green);
            border-radius: 14px;
            box-shadow: var(--fieldvision-shadow);
        }

        [data-testid="stMetricLabel"] {
            color: var(--fieldvision-muted);
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            color: var(--fieldvision-text);
            font-weight: 760;
        }

        [data-testid="stDataFrame"],
        [data-testid="stExpander"] {
            background: var(--fieldvision-surface);
            border: 1px solid var(--fieldvision-border);
            box-shadow: 0 4px 16px rgba(23, 33, 27, 0.04);
            overflow: hidden;
        }

        hr {
            border-color: var(--fieldvision-border) !important;
            margin-top: 1.7rem !important;
            margin-bottom: 1.7rem !important;
        }

        /* Buttons */
        .stButton > button,
        .stDownloadButton > button {
            min-height: 44px;
            border-radius: 10px;
            font-weight: 700;
            transition: transform 0.16s ease, box-shadow 0.16s ease,
                        background 0.16s ease;
        }

        .stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"],
        .stDownloadButton > button {
            background: #15803D !important;
            border: 1px solid #15803D !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }
        .stButton > button[kind="primary"] *,
        button[data-testid="stBaseButton-primary"] *,
        .stDownloadButton > button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            opacity: 1 !important;
        }

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button:hover {
            color: #FFFFFF;
            background: var(--fieldvision-green-dark);
            border-color: var(--fieldvision-green-dark);
            box-shadow: 0 7px 16px rgba(21, 128, 61, 0.2);
            transform: translateY(-1px);
        }

        .stButton > button:not([kind="primary"]) {
            color: var(--fieldvision-green-dark);
            background: #FFFFFF;
            border: 1px solid #86EFAC;
        }

        .stButton > button:not([kind="primary"]):hover {
            color: var(--fieldvision-green-dark);
            background: #F0FDF4;
            border-color: var(--fieldvision-green);
        }

        /* Form controls */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div {
            border-radius: 10px !important;
            border-color: var(--fieldvision-border) !important;
            background: #FFFFFF !important;
        }

        [data-baseweb="select"] > div:focus-within,
        [data-baseweb="input"] > div:focus-within {
            border-color: var(--fieldvision-green) !important;
            box-shadow: 0 0 0 2px rgba(21, 128, 61, 0.12) !important;
        }

        /* Alerts */
        [data-testid="stAlert"] {
            border: 1px solid var(--fieldvision-border);
        }

        /* Hide default Streamlit branding while preserving the header. */
        #MainMenu,
        footer {
            visibility: hidden;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.5rem;
            }

            h1 {
                font-size: 1.72rem !important;
            }

            [data-testid="stMetric"] {
                min-height: 105px;
            }
        }
        /* ---------------------------------------------------------
        Force visible text inside Streamlit date input
        --------------------------------------------------------- */

        [data-testid="stDateInput"] input,
        [data-testid="stDateInput"] input[value],
        [data-testid="stDateInput"] div[data-baseweb="input"] input {
            color: #4B5563 !important;
            -webkit-text-fill-color: #4B5563 !important;
            opacity: 1 !important;
        }

        [data-testid="stDateInput"] input::placeholder {
            color: #6B7280 !important;
            -webkit-text-fill-color: #6B7280 !important;
            opacity: 1 !important;
        }

        [data-testid="stDateInput"] div[data-baseweb="input"] {
            background: #FFFFFF !important;
        }

        [data-testid="stDateInput"] svg {
            fill: #4B5563 !important;
            color: #4B5563 !important;
        }


        /* ---------------------------------------------------------
        FINAL GREEN OVERRIDE — remove red from the entire application
        --------------------------------------------------------- */

        /* All normal, secondary, form, and download buttons */
        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button,
        button[data-testid="stBaseButton-primary"],
        button[data-testid="stBaseButton-secondary"],
        button[kind="primary"],
        button[kind="secondary"] {
            background: #15803D !important;
            border: 1px solid #15803D !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            box-shadow: none !important;
        }

        .stButton > button *,
        .stDownloadButton > button *,
        div[data-testid="stFormSubmitButton"] > button *,
        button[data-testid="stBaseButton-primary"] *,
        button[data-testid="stBaseButton-secondary"] *,
        button[kind="primary"] *,
        button[kind="secondary"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover,
        button[data-testid="stBaseButton-primary"]:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover {
            background: #166534 !important;
            border-color: #166534 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            box-shadow: 0 7px 16px rgba(21, 128, 61, 0.20) !important;
        }

        /* Radio-button indicators */
        [data-baseweb="radio"] input:checked + div,
        [data-testid="stRadio"] input:checked + div {
            background-color: #15803D !important;
            border-color: #15803D !important;
        }

        [data-testid="stRadio"] label:has(input:checked) {
            color: #166534 !important;
        }

        /* Checkboxes and toggles */
        [data-testid="stCheckbox"] input:checked + div,
        [data-testid="stToggle"] input:checked + div {
            background-color: #15803D !important;
            border-color: #15803D !important;
        }

        /* Sliders and progress indicators */
        [data-testid="stSlider"] [role="slider"] {
            background-color: #15803D !important;
            border-color: #15803D !important;
        }

        [data-testid="stProgress"] > div > div > div {
            background-color: #15803D !important;
        }

        /* Links and focus accents */
        a {
            color: #15803D !important;
        }

        *:focus-visible {
            outline-color: #15803D !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )