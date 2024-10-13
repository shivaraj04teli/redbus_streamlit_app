import streamlit as st
import mysql.connector
import pandas as pd

# Function to execute SQL query and return results as a DataFrame
def execute_query(query, params=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="AKSBRSt@2000",
        database="RED_BUS"
    )
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        results = cursor.fetchall()
        df = pd.DataFrame(results)
        return df
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

# Streamlit App Layout
st.set_page_config(page_title="Redbus Data Explorer", layout="wide")

# Set background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffcccc;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title("🚌 Redbus Data Explorer")
st.markdown("Explore bus routes with advanced filtering options.")

st.sidebar.header("MAKE YOUR SELECTION")

routes_query = "SELECT DISTINCT bus_routes_name FROM bus_details_3 ORDER BY bus_routes_name"
routes_df = execute_query(routes_query)
if not routes_df.empty and 'bus_routes_name' in routes_df.columns:
    routes = routes_df['bus_routes_name'].tolist()
    route = st.sidebar.selectbox('Select Route', ['All'] + routes)
else:
    st.error("Unable to fetch routes")
    route = 'All'


price_options = ['All', 'Below 500', '500 - 1000', '1000 - 2000', '2000 and above']
price_range = st.sidebar.selectbox('Select Price Range', price_options)


bus_types_query = "SELECT DISTINCT Bus_type FROM bus_details_3 ORDER BY Bus_type"
bus_types_df = execute_query(bus_types_query)
if not bus_types_df.empty and 'Bus_type' in bus_types_df.columns:
    bus_types = bus_types_df['Bus_type'].tolist()
    bus_type = st.sidebar.selectbox('Select Bus Type', ['All'] + bus_types)
else:
    st.error("Unable to fetch bus types")
    bus_type = 'All'

min_rating = st.sidebar.slider("Minimum Star Rating", 0.0, 5.0, 0.0, step=0.5)


seats_available = st.sidebar.checkbox("Show only buses with available seats")

if st.sidebar.button('Apply Filters'):
    query = """
    SELECT * FROM bus_details_3
    WHERE 1=1
    """
    params = {}
    if route != 'All':
        query += " AND bus_routes_name = %(route)s"
        params['route'] = route
    if price_range != 'All':
        if price_range == 'Below 500':
            query += " AND Price < 500"
        elif price_range == '500 - 1000':
            query += " AND Price BETWEEN 500 AND 1000"
        elif price_range == '1000 - 2000':
            query += " AND Price BETWEEN 1000 AND 2000"
        elif price_range == '2000 and above':
            query += " AND Price > 2000"
    if bus_type != 'All':
        query += " AND Bus_type = %(bus_type)s"
        params['bus_type'] = bus_type
    if min_rating > 0:
        query += " AND Star_Rating >= %(min_rating)s"
        params['min_rating'] = min_rating
    if seats_available:
        query += " AND Seats_Available != '0 Seats available'"
    query += " ORDER BY Price DESC"
    df = execute_query(query, params)

    if not df.empty:
        st.subheader("Filtered Bus Data")
        st.dataframe(df)

        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Buses", len(df))
        with col2:
            if 'Price' in df.columns:
                st.metric("Average Price", f"₹{df['Price'].mean():.2f}")
            else:
                st.error("Price column not found")
        with col3:
            if 'Star_Rating' in df.columns:
                st.metric("Average Rating", f"{df['Star_Rating'].mean():.2f} ⭐")
            else:
                st.error("Star_Rating column not found")
    else:
        st.warning("No data found for the selected filters")

else:
    st.info("Use the sidebar to set filters and click 'Apply Filters' to see results.")

st.markdown("---")
st.markdown("Created with ❤️ using Streamlit and MySQL")