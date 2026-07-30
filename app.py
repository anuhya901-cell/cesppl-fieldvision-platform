from __future__ import annotations

import hashlib
import zipfile
from datetime import date, datetime, timedelta
from io import BytesIO
from math import ceil
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError

from src import classifier
from src import db
from src import pipeline
import matplotlib.pyplot as plt

from styles import apply_custom_styles


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CESPPL FieldVision Platform",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_styles()

def apply_final_green_overrides() -> None:
    """Force Streamlit 1.60 native controls to use the project green theme."""
    st.markdown(
        """
        <style>
        /* Streamlit 1.60 buttons */
        button[data-testid^="stBaseButton-"],
        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button,
        [data-testid="stFileUploader"] button,
        [data-testid="stFormSubmitButton"] button {
            background-color: #15803D !important;
            border: 1px solid #15803D !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            box-shadow: none !important;
        }

        button[data-testid^="stBaseButton-"] *,
        [data-testid="stButton"] button *,
        [data-testid="stDownloadButton"] button *,
        [data-testid="stFileUploader"] button *,
        [data-testid="stFormSubmitButton"] button * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        button[data-testid^="stBaseButton-"]:hover,
        [data-testid="stButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover,
        [data-testid="stFileUploader"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            background-color: #166534 !important;
            border-color: #166534 !important;
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }

        /* Streamlit 1.60 radio indicators */
        [data-testid="stRadio"] input {
            accent-color: #15803D !important;
        }

        [data-testid="stRadio"] label:has(input:checked) > div:first-child {
            background-color: #15803D !important;
            border-color: #15803D !important;
        }

        [data-testid="stRadio"] label:has(input:checked) svg {
            fill: #15803D !important;
            color: #15803D !important;
        }

        /* Text and password input boxes */
        [data-testid="stTextInput"] div[data-baseweb="input"] > div {
            min-height: 48px !important;
            background: #FFFFFF !important;
            border: 1.5px solid #A7B8AE !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }

        [data-testid="stTextInput"] div[data-baseweb="input"] > div:hover,
        [data-testid="stTextInput"] div[data-baseweb="input"] > div:focus-within {
            border-color: #D1D5DB !important;
            box-shadow: none !important;
            outline: none !important;
        }

        [data-testid="stTextInput"] input {
            color: #17211B !important;
            -webkit-text-fill-color: #17211B !important;
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_final_green_overrides()
# ==========================================================
# Session Variables
# ==========================================================

DEFAULT_NOTIFICATIONS = [
    "System started successfully.",
    "Dashboard loaded successfully.",
    "Welcome to CESPPL FieldVision Platform."
]

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "notifications" not in st.session_state:
    st.session_state.notifications = DEFAULT_NOTIFICATIONS.copy()

if "user_role" not in st.session_state:
    st.session_state.user_role = "Admin"


# ---------------------------------------------------------
# Authentication configuration and helpers
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

# Save the company logo as either:
#   assets/logo.png
# or:
#   logo.png
LOGO_CANDIDATES = [
    PROJECT_ROOT / "assets" / "logo.png",
    PROJECT_ROOT / "logo.png",
]

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = (
    "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
)


def hash_password(password: str) -> str:
    """Return the SHA-256 hash of a password."""
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def initialize_login_state() -> None:
    """Create authentication session values when the app starts."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None


def authenticate_user(
    username: str,
    password: str,
) -> bool:
    """Validate the supplied username and password."""
    return (
        username.strip() == ADMIN_USERNAME
        and hash_password(password) == ADMIN_PASSWORD_HASH
    )


def find_logo_path() -> Path | None:
    """Return the first available company-logo path."""
    for logo_path in LOGO_CANDIDATES:
        if logo_path.exists():
            return logo_path

    return None


def show_login_page() -> None:
    """Display the CESPPL FieldVision sign-in page."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 520px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .login-title {
            text-align: center;
            color: #166534;
            font-size: 2rem;
            font-weight: 800;
            margin: 0.5rem 0 0.2rem 0;
        }

        .login-subtitle {
            text-align: center;
            color: #64756d;
            font-size: 1rem;
            line-height: 1.5;
            margin-bottom: 1.4rem;
        }

        .login-footer {
            text-align: center;
            color: #718078;
            font-size: 0.82rem;
            margin-top: 1.2rem;
        }

        /* Login card created with st.container(border=True), not st.form. */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF !important;
            border: 1px solid #DCE8E1 !important;
            border-radius: 18px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: 0 12px 34px rgba(22, 101, 52, 0.10) !important;
        }

        div[data-testid="stForm"] {
            background: #ffffff;
            border: 1px solid #dce8e1;
            border-radius: 18px;
            padding: 1.6rem;
            box-shadow: 0 12px 34px rgba(22, 101, 52, 0.10);
        }

        div[data-testid="stFormSubmitButton"] button {
            width:100%;
            min-height:50px;
            border-radius:10px;
            border:none;
            background:#15803d !important;
            color:#FFFFFF !important;
            -webkit-text-fill-color:#FFFFFF !important;
            font-size:18px;
            font-weight:700;
        }

        div[data-testid="stFormSubmitButton"] button *{
            color:#FFFFFF !important;
            -webkit-text-fill-color:#FFFFFF !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover{
            background:#166534 !important;
            color:#FFFFFF !important;
            -webkit-text-fill-color:#FFFFFF !important;
        }

        /* Login input boxes */
        div[data-baseweb="input"] > div,
        [data-testid="stTextInput"] div[data-baseweb="input"] > div {
            min-height: 48px !important;
            background: #FFFFFF !important;
            border: 1px solid #D1D5DB !important;
            border-radius: 10px !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Hover */
        div[data-baseweb="input"] > div:hover,
        [data-testid="stTextInput"] div[data-baseweb="input"] > div:hover {
            border: 1px solid #D1D5DB !important;
            box-shadow: none !important;
        }

        /* Focus (clicked) */
        div[data-baseweb="input"] > div:focus-within,
        [data-testid="stTextInput"] div[data-baseweb="input"] > div:focus-within {
            border: 1px solid #D1D5DB !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Input text */
        [data-testid="stTextInput"] input {
            color: #17211B !important;
            -webkit-text-fill-color: #17211B !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Placeholder */
        [data-testid="stTextInput"] input::placeholder {
            color: #9CA3AF !important;
        }
        /* Hide image fullscreen/expand button */
        button[title="View fullscreen"] {
            display: none !important;
        }

        [data-testid="StyledFullScreenButton"] {
            display: none !important;
        }

        [data-testid="stImage"] button {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_path = find_logo_path()

    if logo_path is not None:
        left_column, logo_column, right_column = st.columns(
            [1, 2.2, 1]
        )

        with logo_column:
            st.image(
                str(logo_path),
                use_container_width=True,
            )
    else:
        st.info(
            "Save the Chennai Enviro logo as assets/logo.png "
            "or logo.png to display it here."
        )

    st.markdown(
        """
        <div class="login-title">
            CESPPL FieldVision Platform
        </div>
        <div class="login-subtitle">
            Secure access for municipal field-operations
            classification and monitoring
        </div>
        """,
        unsafe_allow_html=True,
    )

    # A regular container is used here instead of st.form.
    # This removes Streamlit's "Press Enter to submit form" hint.
    with st.container(border=True):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
        )

        login_button = st.button(
            "Sign In",
            use_container_width=True,
            key="login_button",
        )
    if login_button:
        if not username.strip() or not password:
            st.warning(
                "Please enter both username and password."
            )

        elif authenticate_user(
            username,
            password,
        ):
            st.session_state.authenticated = True
            st.session_state.logged_in_user = (
                username.strip()
            )
            st.rerun()

        else:
            st.error(
                "Invalid username or password."
            )

    st.markdown(
        """
        <div class="login-footer">
            Chennai Enviro Solutions Private Limited<br>
            Secure FieldVision Access Portal
        </div>
        """,
        unsafe_allow_html=True,
    )
# ==========================================================
# Notification Helpers
# ==========================================================

def add_notification(message: str):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M")
    st.session_state.notifications.insert(
        0,
        f"{timestamp} - {message}"
    )

    if len(st.session_state.notifications) > 30:
        st.session_state.notifications = (
            st.session_state.notifications[:30]
        )


def show_notifications():

    with st.expander(
        f"🔔 Notifications ({len(st.session_state.notifications)})",
        expanded=False,
    ):

        if not st.session_state.notifications:
            st.info("No notifications.")
            return

        for item in st.session_state.notifications:
            st.write("•", item)

        if st.button(
            "Clear Notifications",
            key="clear_notifications"
        ):
            st.session_state.notifications = []
            st.rerun()


def logout_user() -> None:
    """Clear the current authenticated session."""
    st.session_state.authenticated = False
    st.session_state.logged_in_user = None
    st.rerun()


initialize_login_state()

if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# ---------------------------------------------------------
# Prevent duplicate processing
# ---------------------------------------------------------

if "processing_upload" not in st.session_state:
    st.session_state.processing_upload = False

if "last_saved_image_hash" not in st.session_state:
    st.session_state.last_saved_image_hash = None


# ---------------------------------------------------------
# Cached model loader
# ---------------------------------------------------------

@st.cache_resource
def load_classifier_resources():
    """
    Load the trained model and class names only once.
    """
    return classifier.load_model()


# ---------------------------------------------------------
# Shared database initialization
# ---------------------------------------------------------

db.init_db()

# ---------------------------------------------------------
# Upload page
# ---------------------------------------------------------

def show_upload_page():
    st.title("📤 Upload Field Image")

    st.write(
        "Classify and securely store a municipal field-operation image "
        "in the CESPPL FieldVision database."
    )

    try:
        load_classifier_resources()
    except Exception as error:
        st.error(
            "The trained model could not be loaded.\n\n"
            f"{error}"
        )
        return

    uploaded_file = st.file_uploader(
        "Upload a field image",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        key="field_image_uploader",
    )

    if uploaded_file is None:
        st.info(
            "Choose a JPG, JPEG, or PNG field image to begin."
        )
        return

    image_bytes = uploaded_file.getvalue()

    current_image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()

    try:
        preview_image = Image.open(
            BytesIO(image_bytes)
        )

        preview_image.load()

        st.image(
            preview_image,
            caption=(
                f"Uploaded image: "
                f"{uploaded_file.name}"
            ),
            use_container_width=True,
        )

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ):
        st.error(
            "This file has an image extension, but its contents "
            "are not a valid image. Please upload a proper JPG, "
            "JPEG, or PNG image."
        )
        return

    classify_button = st.button(
        "Classify and save",
        type="primary",
        use_container_width=True,
    )

    if classify_button:
        if (
            st.session_state.last_saved_image_hash
            == current_image_hash
        ):
            st.warning(
                "This image was already saved. "
                "It was not stored again."
            )
            return

        if st.session_state.processing_upload:
            st.stop()

        st.session_state.processing_upload = True
        try:
            with st.spinner(
                "Classifying and saving the image..."
            ):
                result = (
                    pipeline.classify_and_store(
                        image_bytes
                    )
                )

            st.session_state.last_saved_image_hash = (
                current_image_hash
            )

            st.success(
                "Image classified and saved successfully."
            )
            add_notification(
                f"New image uploaded : {result['filename']}"
            )

            result_column_1, result_column_2 = (
                st.columns(2)
            )

            with result_column_1:
                st.metric(
                    "Predicted class",
                    result["class_name"],
                )

            with result_column_2:
                st.metric(
                    "Confidence",
                    (
                        f"{result['confidence']:.2%}"
                    ),
                )

            st.write(
                "**Stored filename:** "
                f"`{result['filename']}`"
            )

            st.write(
                "**Uploaded at:** "
                f"`{result['uploaded_at']}`"
            )
        except pipeline.DuplicateImageError as error:
            st.warning(
                "This image was already saved, so it was not "
                "stored again.\n\n"
                f"{error}"
            )

        except pipeline.InvalidImageError as error:
            st.error(
                "The uploaded file is not a valid image.\n\n"
                f"{error}"
            )

        except Exception as error:
            st.error(
                "The image could not be classified or saved.\n\n"
                f"{type(error).__name__}: {error}"
            )
        finally:
            st.session_state.processing_upload = False


# ---------------------------------------------------------
# Dashboard page
# ---------------------------------------------------------

def show_dashboard_page():
    st.title("📊 Operations Dashboard")

    st.write(
        "Monitor uploads, activity coverage, and recent classification results "
        "across CESPPL field operations."
    )
    show_notifications()

    try:
        summary = db.dashboard_summary()
        counts = db.class_counts()
        recent_rows = db.recent_uploads(n=20)

    except Exception as error:
        st.error(
            "Dashboard data could not be loaded.\n\n"
            f"{type(error).__name__}: {error}"
        )
        return

    # -----------------------------------------------------
    # Top metrics
    # -----------------------------------------------------

    metric_column_1, metric_column_2, metric_column_3 = st.columns(3)
    with metric_column_1:
        st.metric(
            "Total uploads",
            summary["total_uploads"],
        )

    with metric_column_2:
        st.metric(
            "Classes with uploads",
            summary["active_classes"],
        )

    with metric_column_3:
        st.metric(
            "Uploads today",
            summary["uploads_today"],
        )

    st.divider()

    # -----------------------------------------------------
    # Bar Chart + Pie Chart
    # -----------------------------------------------------

    st.subheader("Activity Distribution")
    counts_dataframe = pd.DataFrame(
        {
            "Activity class": list(counts.keys()),
            "Upload count": list(counts.values()),
        }
    )

    counts_dataframe = counts_dataframe.set_index(
        "Activity class"
    )

    chart_column_1, chart_column_2 = st.columns([1.6, 1])

    chart_dataframe = counts_dataframe.reset_index()

    # --------------------------
    # LEFT : Horizontal Bar Chart
    # --------------------------

    with chart_column_1:

        figure_bar, axis_bar = plt.subplots(figsize=(6.8,5))

        axis_bar.barh(
            chart_dataframe["Activity class"],
            chart_dataframe["Upload count"],
        )
        # Set x-axis automatically
        import math

        max_uploads = chart_dataframe["Upload count"].max()
        x_limit = math.ceil(max_uploads / 10) * 10 + 10

        axis_bar.set_xlim(0, x_limit)

        axis_bar.set_title(
            "Uploads by Activity Class",
            fontsize=14,
        )

        axis_bar.set_xlabel("Uploads")

        axis_bar.grid(
            axis="x",
            linestyle="--",
            alpha=0.4,
        )

        for index, value in enumerate(
            chart_dataframe["Upload count"]
        ):
            axis_bar.text(
                value + 0.2,
                index,
                str(int(value)),
                va="center",
                fontsize=9,
            )

        figure_bar.tight_layout()

        st.pyplot(
            figure_bar,
            use_container_width=True,
        )

        plt.close(figure_bar)


    # --------------------------
    # RIGHT : Donut Chart
    # --------------------------

    with chart_column_2:

        figure_pie, axis_pie = plt.subplots(figsize=(6.8, 6.8))

        colors = plt.cm.Set3.colors

        wedges, texts, autotexts = axis_pie.pie(
            chart_dataframe["Upload count"],
            labels=chart_dataframe["Activity class"],
            colors=colors,
            startangle=90,
            autopct="%1.1f%%",
            pctdistance=0.78,
            labeldistance=1.10,
            radius=1.05,
            wedgeprops={
                "width": 0.42,
                "edgecolor": "white",
                "linewidth": 2,
            },
            textprops={
                "fontsize": 9,
            },
        )

        # Class names
        for text in texts:
            text.set_fontsize(9)
            text.set_fontweight("normal")

        # Percentage values
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")
            autotext.set_color("black")

        axis_pie.set_title(
            "Prediction Distribution",
            fontsize=14,
            fontweight="bold",
            pad=14,
        )

        axis_pie.axis("equal")

        figure_pie.tight_layout()

        st.pyplot(
            figure_pie,
            use_container_width=True,
        )

        plt.close(figure_pie)
    # -----------------------------------------------------
    # Recent uploads table
    # -----------------------------------------------------

    st.subheader("Recent uploads")

    if not recent_rows:
        st.info(
            "No uploaded images are currently stored."
        )
        return

    recent_dataframe = pd.DataFrame(
        recent_rows
    )

    recent_dataframe = recent_dataframe[
        [
            "filename",
            "class_name",
            "confidence",
            "uploaded_at",
        ]
    ].copy()

    # Convert decimal confidence (0.95) to percentage (95.00)
    recent_dataframe.loc[:, "confidence"] = (
        recent_dataframe["confidence"] * 100
    )

    recent_dataframe = recent_dataframe.rename(
        columns={
            "filename": "Filename",
            "class_name": "Class",
            "confidence": "Confidence",
            "uploaded_at": "Uploaded at",
        }
    )

    st.dataframe(
        recent_dataframe,
        column_config={
            "Filename": st.column_config.TextColumn(
                "Filename"
            ),
            "Class": st.column_config.TextColumn(
                "Class"
            ),
            "Confidence": (
                st.column_config.NumberColumn(
                    "Confidence",
                    format="%.2f%%",
                )
            ),
            "Uploaded at": (
                st.column_config.TextColumn(
                    "Uploaded at"
                )
            ),
        },
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Browse-page configuration
# ---------------------------------------------------------

IMAGES_PER_PAGE = 24
THUMBNAIL_SIZE = (300, 300)


# ---------------------------------------------------------
# Whole-class ZIP helper
# ---------------------------------------------------------

def build_class_zip(
    uploads: list[dict],
) -> bytes:
    """
    Build an in-memory ZIP file containing all images
    represented by the supplied upload metadata.

    Image BLOBs are fetched only when this function is called.
    """

    zip_buffer = BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zip_file:

        for upload in uploads:
            upload_id = int(upload["id"])
            filename = str(upload["filename"])

            image_bytes = db.get_image(
                upload_id
            )

            if image_bytes is None:
                continue

            zip_file.writestr(
                filename,
                image_bytes,
            )

    zip_buffer.seek(0)

    return zip_buffer.getvalue()


# ---------------------------------------------------------
# Browse page
# ---------------------------------------------------------

def show_browse_page():
    st.title("🏞️ Image Library")

    st.write(
        "Browse stored field images by activity class, review details, "
        "correct classifications, and download records."
    )

    # -----------------------------------------------------
    # Load class names and counts
    # -----------------------------------------------------

    try:
        counts = db.class_counts()

    except Exception as error:
        st.error(
            "The class list could not be loaded.\n\n"
            f"{type(error).__name__}: {error}"
        )
        return

    class_names = list(
        counts.keys()
    )

    selected_class = st.selectbox(
        "Select an activity class",
        options=class_names,
        key="browse_class_selector",
    )

    selected_class_count = int(
        counts.get(
            selected_class,
            0,
        )
    )

    # -----------------------------------------------------
    # Date filter
    # -----------------------------------------------------

    st.subheader("📅 Date Filter")

    date_filter = st.radio(
        "Select upload period",
        options=[
            "All",
            "Today",
            "Last 7 Days",
            "Last 30 Days",
            "Custom Range",
        ],
        horizontal=True,
        key="browse_date_filter",
    )

    today = date.today()

    start_date = None
    end_date = None

    if date_filter == "Today":
        start_date = today
        end_date = today

    elif date_filter == "Last 7 Days":
        start_date = today - timedelta(days=6)
        end_date = today

    elif date_filter == "Last 30 Days":
        start_date = today - timedelta(days=29)
        end_date = today

    elif date_filter == "Custom Range":

        from_column, to_column = st.columns(2)

        with from_column:
            start_date = st.date_input(
                "📅 From Date",
                value=today,
                max_value=today,
                key="browse_from_date",
            )

        with to_column:
            end_date = st.date_input(
                "📅 To Date",
                value=today,
                min_value=start_date,
                max_value=today,
                key="browse_to_date",
            )
    # -----------------------------------------------------
    # Load metadata only — no image BLOBs here
    # -----------------------------------------------------

    try:
        uploads = db.list_uploads(
            selected_class
        )

    except Exception as error:
        st.error(
            "The stored upload list could not be loaded.\n\n"
            f"{type(error).__name__}: {error}"
        )
        return

    # -----------------------------------------------------
    # Apply selected date filter
    # -----------------------------------------------------

    if start_date is not None and end_date is not None:
        filtered_uploads = []

        for upload in uploads:
            try:
                upload_date = datetime.fromisoformat(
                    str(upload["uploaded_at"])
                ).date()

                if start_date <= upload_date <= end_date:
                    filtered_uploads.append(
                        upload
                    )

            except (
                TypeError,
                ValueError,
            ):
                continue

        uploads = filtered_uploads

    # -----------------------------------------------------
    # Filter information
    # -----------------------------------------------------

    if date_filter == "All":
        filter_description = "all dates"

    elif start_date == end_date:
        filter_description = (
            start_date.strftime("%d %B %Y")
        )

    else:
        filter_description = (
            f"{start_date.strftime('%d %B %Y')} "
            f"to {end_date.strftime('%d %B %Y')}"
        )

    filtered_count = len(uploads)

    st.caption(
        f"Showing {filtered_count} of "
        f"{selected_class_count} uploaded image"
        f"{'' if selected_class_count == 1 else 's'} "
        f"in {selected_class} for {filter_description}."
    )

    # -----------------------------------------------------
    # Empty-filter handling
    # -----------------------------------------------------

    if not uploads:
        st.info(
            f"No {selected_class} images were uploaded "
            f"during {filter_description}."
        )
        return
    # -----------------------------------------------------
    # Whole-class download
    # -----------------------------------------------------

    class_filename = (
        selected_class
        .replace(" ", "_")
        .replace("/", "_")
    )

    current_date = datetime.now().strftime(
        "%Y-%m-%d"
    )

    zip_filename = (
        f"{class_filename}_{current_date}.zip"
    )

    st.subheader("Download complete class")

    st.caption(
        "Preparing the complete ZIP fetches all images in "
        "this class. Gallery browsing fetches only the visible page."
    )

    prepare_zip_button = st.button(
        (
            f"Prepare {selected_class} ZIP "
            f"({len(uploads)} images)"
        ),
        key=(
            f"prepare_zip_{class_filename}"
        ),
    )

    zip_state_key = (
        f"prepared_zip_{class_filename}"
    )

    if prepare_zip_button:
        try:
            with st.spinner(
                f"Preparing {len(uploads)} images..."
            ):
                st.session_state[
                    zip_state_key
                ] = build_class_zip(
                    uploads
                )

            st.success(
                "The class ZIP is ready."
            )

        except Exception as error:
            st.error(
                "The class ZIP could not be created.\n\n"
                f"{type(error).__name__}: {error}"
            )

    if zip_state_key in st.session_state:
        st.download_button(
            label=(
                f"Download {selected_class} "
                f"({len(uploads)} images)"
            ),
            data=st.session_state[
                zip_state_key
            ],
            file_name=zip_filename,
            mime="application/zip",
            key=(
                f"download_zip_{class_filename}"
            ),
            use_container_width=True,
        )

    st.divider()

    # -----------------------------------------------------
    # Pagination
    # -----------------------------------------------------

    total_uploads = len(uploads)

    total_pages = max(
        1,
        ceil(
            total_uploads
            / IMAGES_PER_PAGE
        ),
    )

    page_numbers = list(
        range(
            1,
            total_pages + 1,
        )
    )

    page_column, information_column = (
        st.columns(
            [1, 3]
        )
    )

    with page_column:
        selected_page = st.selectbox(
            "Page",
            options=page_numbers,
            index=0,
            key=(
                f"browse_page_{class_filename}"
            ),
        )

    start_index = (
        selected_page - 1
    ) * IMAGES_PER_PAGE

    end_index = min(
        start_index
        + IMAGES_PER_PAGE,
        total_uploads,
    )

    visible_uploads = uploads[
        start_index:end_index
    ]

    with information_column:
        st.write("")
        st.write(
            f"Showing images "
            f"**{start_index + 1}–{end_index}** "
            f"of **{total_uploads}**"
        )

    st.subheader(
        f"{selected_class} gallery"
    )

    # -----------------------------------------------------
    # Four-column thumbnail gallery
    # -----------------------------------------------------

    gallery_columns = st.columns(
        4
    )

    for position, upload in enumerate(
        visible_uploads
    ):
        upload_id = int(
            upload["id"]
        )

        filename = str(
            upload["filename"]
        )

        confidence = float(
            upload["confidence"]
        )

        uploaded_at = str(
            upload["uploaded_at"]
        )

        current_column = gallery_columns[
            position % 4
        ]

        with current_column:
            try:
                # Only visible-page image BLOBs are fetched.
                image_bytes = db.get_image(
                    upload_id
                )

                if image_bytes is None:
                    st.warning(
                        f"{filename} could not be found."
                    )
                    continue

                with Image.open(
                    BytesIO(image_bytes)
                ) as opened_image:

                    opened_image.load()

                    full_image = (
                        opened_image
                        .convert("RGB")
                        .copy()
                    )

                thumbnail_image = (
                    full_image.copy()
                )

                thumbnail_image.thumbnail(
                    THUMBNAIL_SIZE,
                    Image.Resampling.LANCZOS,
                )

                st.image(
                    thumbnail_image,
                    caption=filename,
                    use_container_width=True,
                )

                with st.expander(
                    "View full image and details"
                ):
                    st.image(
                        full_image,
                        caption=filename,
                        use_container_width=True,
                    )

                    st.write(
                        f"**Filename:** `{filename}`"
                    )

                    st.write(
                        f"**Confidence:** "
                        f"{confidence:.2%}"
                    )

                    st.write(
                        f"**Uploaded at:** "
                        f"`{uploaded_at}`"
                    )
                    st.markdown("---")

                st.write("### Wrong class?")

                st.caption(
                    "Select the correct activity class and reassign "
                    "this stored image."
                )

                available_classes = [
                    class_name
                    for class_name in class_names
                    if class_name != selected_class
                ]

                new_class = st.selectbox(
                    "Correct activity class",
                    options=available_classes,
                    key=f"reassign_class_{upload_id}",
                )

                reassign_button = st.button(
                    "Reassign image",
                    key=f"reassign_button_{upload_id}",
                    use_container_width=True,
                )

                if reassign_button:
                    try:
                        updated = db.reassign_upload(
                            upload_id=upload_id,
                            new_class_name=new_class,
                        )

                        if updated:
                            st.success(
                                f"Image reassigned from "
                                f"{selected_class} to {new_class}."
                            )

                            add_notification(
                                f"{filename} was reassigned from {selected_class} to {new_class}"
                            )

                            st.rerun()

                        else:
                            st.error(
                                "The selected image could not be found."
                            )
                    except Exception as error:
                        st.error(
                            "The image could not be reassigned.\n\n"
                            f"{type(error).__name__}: {error}"
                        )

                st.download_button(
                    label="Download image",
                    data=image_bytes,
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"download_image_{upload_id}",
                    use_container_width=True,
                )
            except (
                UnidentifiedImageError,
                OSError,
                ValueError,
            ) as error:
                st.error(
                    f"{filename} is not a readable image.\n\n"
                    f"{type(error).__name__}: {error}"
                )

            except Exception as error:
                st.error(
                    f"{filename} could not be displayed.\n\n"
                    f"{type(error).__name__}: {error}"
                )

    st.divider()

    st.caption(
        f"Page {selected_page} of {total_pages}"
    )

# ---------------------------------------------------------
# Application navigation
# ---------------------------------------------------------

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <p class="sidebar-brand__eyebrow">CESPPL</p>
        <p class="sidebar-brand__title">FieldVision Platform</p>
        <p class="sidebar-brand__subtitle">
            Municipal field operations classification and monitoring
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_page = st.sidebar.radio(
    "Navigation",
    options=[
        "📊  Dashboard",
        "📤  Upload",
        "🏞️  Browse",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

st.sidebar.caption(
    f"Signed in as: {st.session_state.logged_in_user}"
)

if st.sidebar.button(
    "↩ Logout",
    use_container_width=True,
    type="secondary",
):
    logout_user()

st.sidebar.markdown(
    """
    <div class="sidebar-footer">
        <strong>CESPPL FieldVision</strong><br>
        Image classification, tracking, correction, and activity reporting.
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style="width:100%; text-align:center; margin:0 0 1.8rem 0; padding:0.5rem 0 1rem 0; border-bottom:1px solid #E2E8E5;">
        <h1 style="margin:0; padding:0; text-align:center; color:#166534; font-size:2.3rem; font-weight:800; letter-spacing:-0.025em;">
            CESPPL FieldVision Platform
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)


if selected_page == "📤  Upload":
    show_upload_page()

elif selected_page == "📊  Dashboard":
    show_dashboard_page()

elif selected_page == "🏞️  Browse":
    show_browse_page()

# Re-apply as the final stylesheet in the page.
apply_final_green_overrides()
