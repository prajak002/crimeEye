import streamlit as st
import folium
import sqlite3
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_chat import message
import openai

def generate_bot_response(prompt):
    # API endpoint
    api_url = "https://api.openai.com/v1/chat/completions"

    with open("api_key.txt", "r") as file:
        openai.api_key = file.read().strip()
    
    model_engine = "text-curie-001"
    # Set the maximum number of tokens to generate in the response
    max_tokens = 1024

    # Generate a response
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message 


logo_image = Image.open("Logo.png")
st.image(logo_image, use_column_width=True)

selected = option_menu(
    menu_title=None,
    options=["Crime Mapper", "Safety Corner", "Safety Resources", "Location Info"],
    icons=["map", "search", "info", "location"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected == "Crime Mapper":
    # Create a SQLite database connection
    conn = sqlite3.connect("markers.db")
    c = conn.cursor()

    # Create a markers table if it doesn't exist
    c.execute(
        '''CREATE TABLE IF NOT EXISTS markers
                (latitude REAL, longitude REAL, popup TEXT, color TEXT)'''
    )

    # Create a map centered at latitude 40.7128 and longitude -74.0060 (New York City)
    m = folium.Map(location=[40.7128, -94.0060], zoom_start=4)

    # Retrieve markers data from the database
    c.execute("SELECT * FROM markers")
    marker_locations = c.fetchall()

    for marker in marker_locations:
        latitude, longitude, popup, color = marker
        folium.Marker(
            location=[latitude, longitude],
            popup=popup,
            icon=folium.Icon(color=color),
        ).add_to(m)

    # Display the map using folium_static with custom width and height
    folium_static(m, width=700, height=600)

    # Center the titles using CSS
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            margin-top: 20px;
            color: white; /* Foreground color */
            background-color: red; /* Background color */
            text-decoration: none;
            border-radius: 10px;
        }
        .form-container {
            border: 1px solid black;
            border-radius: 5px;
            margin-bottom: 20px;
            padding: 20px;
        }
        .search-button {
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Page for users to submit suspicious activity
    st.markdown('<p class="title">Report Suspicious Activity</p>', unsafe_allow_html=True)
    st.markdown("---")  # Add a horizontal line for separation

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            latitude = st.number_input("Latitude", value=0.0, step=0.0001)
    with col2:
        with st.container():
            longitude = st.number_input("Longitude", value=0.0, step=0.0001)

    with st.container():
        with st.container():
            description = st.text_area("Description")

    submitted = st.button("Submit")

    if submitted:
        # Insert the submitted suspicious activity into the database
        c.execute(
            "INSERT INTO markers VALUES (?, ?, ?, ?)",
            (latitude, longitude, description, "yellow"),
        )
        conn.commit()

        # Clear the existing map
        st.empty()


        # Retrieve markers data from the database
        c.execute("SELECT * FROM markers")
        marker_locations = c.fetchall()

        for marker in marker_locations:
            latitude, longitude, popup, color = marker
            folium.Marker(
                location=[latitude, longitude],
                popup=popup,
                icon=folium.Icon(color=color),
            ).add_to(m)



        # Reset the input values
        latitude = 0.0
        longitude = 0.0
        description = ""

    # Close the database connection
    conn.close()

elif selected == "Safety Corner":
    # Page title and description
    st.title("Safety Corner")
    st.write("Welcome to the Safety Corner! Here, you can get safety tips, resources, and educational materials to help you stay safe.")

    # Chatbot section
    st.header("Chat with our Safety Bot")
    
    # Example chatbot messages
    message("Hello! How can I assist you today?")
    message("I'm here to provide safety tips and answer any questions you have.")

    # User input
    user_input = st.text_input("Enter your message")
    if user_input:
        # Process user input and generate bot's response
        bot_response = generate_bot_response(user_input)  

        # Display bot's response
        message(bot_response, is_user=False)

elif selected == "Safety Resources":
    # Page title and description
    st.title("Safety Resources")
    st.write("Here are some relevant safety resources to help you stay informed and prepared.")

    # Resource 1
    st.header("Resource 1")
    st.write("Website: [National Safety Council](https://www.nsc.org/)")
    st.write("Description: The National Safety Council is a nonprofit organization that provides valuable safety information, resources, and training to promote safety at home, work, and in the community.")

    # Resource 2
    st.header("Resource 2")
    st.write("Website: [Ready.gov](https://www.ready.gov/)")
    st.write("Description: Ready.gov is a website by the Federal Emergency Management Agency (FEMA) that offers guidance on emergency preparedness and provides resources to help individuals and communities plan for various types of disasters.")

    # Resource 3
    st.header("Resource 3")
    st.write("Website: [CDC - Emergency Preparedness and Response](https://www.cdc.gov/phpr/index.htm)")
    st.write("Description: The Centers for Disease Control and Prevention (CDC) - Emergency Preparedness and Response website provides information and resources for public health emergencies and disasters, including guidance on emergency preparedness, response, and recovery.")

elif selected == "Location Info":
    # Page title and description
    st.title("Location Information")
    st.write("Enter a location to get more information about it.")

    location = st.text_input("Enter a location")
    if location:
        geolocator = Nominatim(user_agent="location-info")
        try:
            location = geolocator.geocode(location)
            if location:
                st.write("Latitude:", location.latitude)
                st.write("Longitude:", location.longitude)
                st.write("Address:", location.address)
                st.write("Country:", location.raw["display_name"].split(",")[-1].strip())
            else:
                st.warning("Location not found. Please enter a valid location.")
        except Exception as e:
            st.error("An error occurred while fetching the location information.")
            st.error(str(e))
