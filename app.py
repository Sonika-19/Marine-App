# app.py
import streamlit as st
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import pandas as pd
import os

# ---------- CONFIG ----------
DB_USER = "root"
DB_PASSWORD = "Password"   # kept from original snippet
DB_HOST = "localhost"
DB_NAME = "marine_db"

# Path provided by you (Windows). If you keep SQL in another path, change this.
DEFAULT_SQL_PATH = r"C:\Users\klson\OneDrive\Desktop\marine_new\marine_species_project.sql"
# Also keep fallback to uploaded file location used during development/testing
FALLBACK_SQL_PATH = "/mnt/data/marine_species_project.sql"

# ---------- DB CONNECTION ----------
def get_db_connection(database=DB_NAME):
    """Return a MySQL connection to `database`. If database is None connect to server only"""
    try:
        conn_kwargs = {
            "host": DB_HOST,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }
        if database:
            conn_kwargs["database"] = database
        conn = mysql.connector.connect(**conn_kwargs)
        return conn
    except mysql.connector.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# ---------- SQL FILE EXECUTOR (handles DELIMITER // blocks) ----------
def execute_sql_file(conn, sql_file_path):
    """
    Execute SQL script with basic support for DELIMITER blocks.
    This attempts to parse the file and execute statements in order.
    """
    if not os.path.exists(sql_file_path):
        return False, f"SQL file not found at: {sql_file_path}"
    try:
        cursor = conn.cursor()
        with open(sql_file_path, "r", encoding="utf-8") as f:
            script = f.read()
    except Exception as e:
        return False, f"Failed to read SQL file: {e}"

    # Basic parser: supports changing delimiter (e.g., DELIMITER // ... //)
    current_delim = ";"
    statement = ""
    lines = script.splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line and not statement:
            continue

        # Handle delimiter change lines
        if line.upper().startswith("DELIMITER"):
            parts = line.split()
            if len(parts) >= 2:
                current_delim = parts[1]
            else:
                current_delim = ";"
            continue

        # Append line to running statement
        statement += raw_line + "\n"

        # If current delimiter appears at end of the statement, split and execute
        if current_delim != ";":
            # check if statement ends with delimiter on its own (after strip)
            if statement.rstrip().endswith(current_delim):
                exec_stmt = statement.rstrip()[:-len(current_delim)].strip()
                if exec_stmt:
                    try:
                        cursor.execute(exec_stmt)
                    except mysql.connector.Error as e:
                        # Continue on error but return message at end
                        conn.rollback()
                        cursor.close()
                        return False, f"Error executing statement: {e}\nStatement:\n{exec_stmt[:500]}"
                statement = ""
        else:
            # default delimiter ';' — execute when a semicolon appears at the end
            if statement.strip().endswith(";"):
                exec_stmt = statement.strip()[:-1].strip()
                if exec_stmt:
                    try:
                        cursor.execute(exec_stmt)
                    except mysql.connector.Error as e:
                        conn.rollback()
                        cursor.close()
                        return False, f"Error executing statement: {e}\nStatement:\n{exec_stmt[:500]}"
                statement = ""

    # in case any trailing statement remains (no delimiter)
    if statement.strip():
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            conn.rollback()
            cursor.close()
            return False, f"Error executing final statement: {e}\nStatement:\n{statement[:500]}"

    conn.commit()
    cursor.close()
    return True, "SQL file executed successfully"

# ---------- DB INIT FUNCTION ----------
def ensure_database_initialized(sql_path=None):
    """
    Ensures marine_db exists and, if not present, tries to create it by executing the SQL file.
    Returns (success: bool, message: str)
    """
    # first try to connect to the database
    conn = get_db_connection(database=DB_NAME)
    if conn:
        conn.close()
        return True, f"Database '{DB_NAME}' exists and is reachable"
    # If not, connect to server without specifying database and run SQL
    server_conn = get_db_connection(database=None)
    if not server_conn:
        return False, "Could not connect to MySQL server to initialize database"

    # Choose SQL path: user-specified or fallback
    if sql_path and os.path.exists(sql_path):
        use_path = sql_path
    elif os.path.exists(DEFAULT_SQL_PATH):
        use_path = DEFAULT_SQL_PATH
    elif os.path.exists(FALLBACK_SQL_PATH):
        use_path = FALLBACK_SQL_PATH
    else:
        server_conn.close()
        return False, ("SQL file not found. Please ensure the SQL file is placed at:\n"
                       f"{DEFAULT_SQL_PATH}\nor\n{FALLBACK_SQL_PATH}\n"
                       "Or update the path in the app settings")

    success, msg = execute_sql_file(server_conn, use_path)
    server_conn.close()
    return success, msg

# ---------- DATA ACCESS HELPERS ----------
def fetch_all_species():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT species_id, common_name, scientific_name, conservation_status FROM Species")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_all_locations():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT location_id, location_name, region, water_type FROM Location")
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_all_observers():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT observer_id, name, organization, contact FROM Observer")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_species(common_name, scientific_name, conservation_status):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Species (common_name, scientific_name, conservation_status) VALUES (%s, %s, %s)",
            (common_name, scientific_name, conservation_status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Species added"
    except mysql.connector.Error as e:
        return False, str(e)

def add_observer(name, organization, contact):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Observer (name, organization, contact) VALUES (%s, %s, %s)",
            (name, organization, contact)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Observer added"
    except mysql.connector.Error as e:
        return False, str(e)

def add_water_quality(location_id, temperature, pH, salinity, pollution_index):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Water_Quality (location_id, temperature, pH, salinity, pollution_index) VALUES (%s, %s, %s, %s, %s)",
            (location_id, temperature, pH, salinity, pollution_index)
        )
        wq_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return True, wq_id
    except mysql.connector.Error as e:
        return False, str(e)

def add_observation(species_id, location_id, observer_id, quality_id, obs_date, count_observed, remarks):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Observation (species_id, location_id, observer_id, quality_id, obs_date, count_observed, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (species_id, location_id, observer_id, quality_id, obs_date, count_observed, remarks)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Observation logged"
    except mysql.connector.Error as e:
        return False, str(e)

def search_species_by_name(name):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    like = f"%{name}%"
    cursor.execute("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM Observation o WHERE o.species_id = s.species_id) AS total_observations
        FROM Species s
        WHERE s.common_name LIKE %s OR s.scientific_name LIKE %s
    """, (like, like))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_actions_for_species(species_id):
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT action_id, action_type, description, start_date, end_date
        FROM Conservation_Action
        WHERE species_id = %s
    """, (species_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_recent_observations(limit=10):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.obs_id, s.common_name, l.location_name, o.obs_date, o.count_observed, o.remarks
        FROM Observation o
        LEFT JOIN Species s ON o.species_id = s.species_id
        LEFT JOIN Location l ON o.location_id = l.location_id
        ORDER BY o.obs_date DESC
        LIMIT %s
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame(rows)

# ---------- STREAMLIT UI ----------
def main():
    st.set_page_config(page_title="Marine Species Conservation", page_icon="🐟", layout="wide")

    st.sidebar.title("Marine Conservation")
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("Navigation", [
        "Dashboard", "Add Observation", "Add Species/Observer", "Search Species", "Conservation Actions", "DB Init"
    ])

    # ---------- DB INIT ----------
    if menu == "DB Init":
        st.title("Database Initialization")
        st.markdown("Use this page to initialize the `marine_db` from your SQL file path")

        st.info(f"Default SQL path set to: {DEFAULT_SQL_PATH}")
        sql_path = st.text_input("SQL file path", value=DEFAULT_SQL_PATH)
        if st.button("Initialize Database"):
            with st.spinner("Initializing database. This may take a few seconds"):
                success, msg = ensure_database_initialized(sql_path=sql_path)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    st.write("If the automatic initialization failed, please run this SQL file manually using mysql client:")
                    st.code(f'mysql -u {DB_USER} -p < "{sql_path}"')

    # ---------- DASHBOARD ----------
    elif menu == "Dashboard":
        st.title("🐠 Marine Conservation Dashboard")
        conn = get_db_connection()
        if not conn:
            st.error("Cannot connect to database. Use DB Init to create the DB or check credentials")
            return

        cursor = conn.cursor(dictionary=True)

        # Metrics
        cursor.execute("SELECT COUNT(*) as count FROM Species")
        total_species = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Location")
        total_locations = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Observation")
        total_observations = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM Conservation_Action")
        total_actions = cursor.fetchone()['count']

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Species", total_species)
        col2.metric("Locations", total_locations)
        col3.metric("Observations", total_observations)
        col4.metric("Conservation Actions", total_actions)

        st.markdown("---")

        # Species by conservation status
        cursor.execute("""
            SELECT conservation_status, COUNT(*) as count
            FROM Species
            GROUP BY conservation_status
        """)
        species_status = pd.DataFrame(cursor.fetchall())
        if not species_status.empty:
            st.subheader("Species by Conservation Status")
            st.bar_chart(species_status.set_index('conservation_status'))

        # Pollution by region
        cursor.execute("""
            SELECT l.region, AVG(wq.pollution_index) as avg_pollution
            FROM Water_Quality wq
            JOIN Location l ON wq.location_id = l.location_id
            GROUP BY l.region
        """)
        pollution_df = pd.DataFrame(cursor.fetchall())
        if not pollution_df.empty:
            st.subheader("Average Pollution Index by Region")
            st.line_chart(pollution_df.set_index('region'))

        st.markdown("---")
        st.subheader("Recent Observations")
        recent = fetch_recent_observations(limit=8)
        if not recent.empty:
            st.dataframe(recent, use_container_width=True)
        else:
            st.info("No observations yet")

        conn.close()

    # ---------- ADD OBSERVATION ----------
    elif menu == "Add Observation":
        st.title("Log New Observation")
        st.markdown("Record sightings and water quality measurements")

        species = fetch_all_species()
        locations = fetch_all_locations()
        observers = fetch_all_observers()

        if not species:
            st.warning("No species found in DB. Add species first or run DB Init")
        col1, col2 = st.columns(2)
        with col1:
            selected_species = st.selectbox("Species", options=[f"{s['common_name']} ({s['scientific_name']})" for s in species] if species else ["-"])
            species_map = {f"{s['common_name']} ({s['scientific_name']})": s['species_id'] for s in species}
            obs_date = st.date_input("Observation Date", value=datetime.now().date())
            obs_time = st.time_input("Observation Time", value=datetime.now().time())
            count_observed = st.number_input("Count Observed", min_value=0, step=1, value=1)

        with col2:
            selected_location = st.selectbox("Location", options=[f"{l['location_name']} - {l['region']}" for l in locations] if locations else ["-"])
            location_map = {f"{l['location_name']} - {l['region']}": l['location_id'] for l in locations}
            observer_choice = st.selectbox("Observer", options=[f"{o['name']} ({o['organization']})" for o in observers] if observers else ["-"])
            observer_map = {f"{o['name']} ({o['organization']})": o['observer_id'] for o in observers}
            remarks = st.text_area("Remarks", placeholder="Optional notes")

        st.markdown("### Water Quality (optional)")
        wcol1, wcol2, wcol3 = st.columns(3)
        with wcol1:
            temperature = st.number_input("Temperature (°C)", format="%.2f", value=25.0)
            pH = st.number_input("pH", format="%.2f", value=8.0)
        with wcol2:
            salinity = st.number_input("Salinity (ppt)", format="%.2f", value=35.0)
            pollution_index = st.number_input("Pollution Index (0-100)", format="%.2f", value=10.0)
        with wcol3:
            add_new_observer = st.checkbox("Add new observer")
            if add_new_observer:
                new_obs_name = st.text_input("Observer Name")
                new_obs_org = st.text_input("Organization")
                new_obs_contact = st.text_input("Contact email/phone")

        if st.button("Submit Observation"):
            if not species or selected_species == "-" or selected_location == "-" or observer_choice == "-":
                st.error("Ensure species, location and observer are available or add them first")
            else:
                sp_id = species_map[selected_species]
                loc_id = location_map[selected_location]
                if add_new_observer:
                    ok, res = add_observer(new_obs_name, new_obs_org, new_obs_contact)
                    if not ok:
                        st.error(f"Failed to add observer: {res}")
                        return
                    # fetch observers again to get id
                    observers = fetch_all_observers()
                    observer_map = {f"{o['name']} ({o['organization']})": o['observer_id'] for o in observers}
                    observer_choice = f"{new_obs_name} ({new_obs_org})"
                obs_id_val = observer_map[observer_choice]

                # Add water quality row first (optional)
                ok_wq, wq_res = add_water_quality(loc_id, temperature, pH, salinity, pollution_index)
                if not ok_wq:
                    st.error(f"Failed to add water quality: {wq_res}")
                    return
                quality_id = wq_res  # lastrowid returned

                obs_dt = datetime.combine(obs_date, obs_time)
                ok_obs, obs_msg = add_observation(sp_id, loc_id, obs_id_val, quality_id, obs_dt, int(count_observed), remarks)
                if ok_obs:
                    st.success("Observation logged")
                else:
                    st.error(f"Failed to log observation: {obs_msg}")

    # ---------- ADD SPECIES / OBSERVER ----------
    elif menu == "Add Species/Observer":
        st.title("Add Species or Observer")
        st.markdown("Add new species to track or new observers")

        tab1, tab2 = st.tabs(["Add Species", "Add Observer"])

        with tab1:
            st.subheader("Add Species")
            s_common = st.text_input("Common Name")
            s_scientific = st.text_input("Scientific Name")
            s_status = st.selectbox("Conservation Status", ["Least Concern", "Near Threatened", "Vulnerable", "Endangered", "Critically Endangered"])

            if st.button("Add Species"):
                if not s_common:
                    st.error("Common name is required")
                else:
                    ok, msg = add_species(s_common, s_scientific, s_status)
                    if ok:
                        st.success("Species added")
                    else:
                        st.error(f"Failed to add species: {msg}")

        with tab2:
            st.subheader("Add Observer")
            o_name = st.text_input("Name")
            o_org = st.text_input("Organization")
            o_contact = st.text_input("Contact")

            if st.button("Add Observer", key="add_obs_btn"):
                if not o_name:
                    st.error("Observer name is required")
                else:
                    ok, msg = add_observer(o_name, o_org, o_contact)
                    if ok:
                        st.success("Observer added")
                    else:
                        st.error(f"Failed to add observer: {msg}")

    # ---------- SEARCH SPECIES ----------
    elif menu == "Search Species":
        st.title("Search Species")
        q = st.text_input("Enter species common or scientific name")
        if st.button("Search"):
            if not q:
                st.error("Please enter a search term")
            else:
                results = search_species_by_name(q)
                if results:
                    st.success(f"Found {len(results)} row(s)")
                    for r in results:
                        with st.expander(f"{r['common_name']} ({r.get('scientific_name','')})"):
                            st.write(f"Conservation Status: {r.get('conservation_status')}")
                            st.write(f"Total Observations: {r.get('total_observations')}")
                            st.markdown("### Conservation Actions")
                            actions = fetch_actions_for_species(r['species_id'])
                            if actions:
                                st.table(pd.DataFrame(actions))
                            else:
                                st.info("No actions recorded for this species")
                else:
                    st.warning("No species found")

    # ---------- CONSERVATION ACTIONS ----------
    elif menu == "Conservation Actions":
        st.title("Conservation Actions")
        conn = get_db_connection()
        if not conn:
            st.error("Cannot connect to DB")
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ca.action_id, s.common_name, ca.action_type, ca.description, ca.start_date, ca.end_date
            FROM Conservation_Action ca
            JOIN Species s ON ca.species_id = s.species_id
            ORDER BY ca.start_date DESC
        """)
        actions = pd.DataFrame(cursor.fetchall())
        if not actions.empty:
            st.dataframe(actions, use_container_width=True)
        else:
            st.info("No conservation actions recorded")
        conn.close()

if __name__ == "__main__":
    main()
