
import pandas as pd
import warnings
import streamlit as st
import numpy as np

warnings.filterwarnings("ignore")

# Load data and perform initial cleaning
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/allipl.csv")
        df["match_date"] = pd.to_datetime(df["start_date"])
        df["year"] = df["match_date"].dt.year
        df = df.sort_values(by=["match_id", "innings", "ball"])
        df["ball"] = df["ball"].astype(str)
        df[["overs", "balls"]] = df["ball"].str.split(".", expand=True)
        df["overs"] = df["overs"].astype(int)
        df["balls"] = df["balls"].astype(int)
        df = df[(df["innings"] == 1) | (df["innings"] == 2)]

        def phase(x):
            if x <= 6:
                return "powerplay"
            elif x <= 15:
                return "middle"
            else:
                return "death"

        df["phase"] = df["overs"].apply(lambda x: phase(x))
        df1 = df[["match_id", "year", "striker", "bowler", "runs_off_bat", "balls", "overs", "phase", "player_dismissed"]]
        df1 = df1.replace(np.nan, 0)
        return df1
    except FileNotFoundError:
        
        st.stop()

df1 = load_data()

# Streamlit UI
st.title("🏏 Cricket Matchup Analysis")

# Sidebar for user inputs
st.sidebar.header("Filters")

# First, select the Batsman
all_batsmen = sorted(df1["striker"].unique())
selected_batsman = st.sidebar.selectbox(
    "Select Batsman:",
    options=all_batsmen,
    index=None,
    placeholder="Choose a batsman..."
)

# Conditionally populate the bowler list
if selected_batsman:
    # Get all bowlers faced by the selected batsman
    bowlers_faced_df = df1[df1["striker"] == selected_batsman]
    all_bowlers = sorted(bowlers_faced_df["bowler"].unique())
    selected_bowler = st.sidebar.selectbox(
        "Select Bowler:",
        options=all_bowlers,
        index=None,
        placeholder="Choose a bowler..."
    )
else:
    # If no batsman is selected, show an empty or placeholder list for bowlers
    selected_bowler = st.sidebar.selectbox(
        "Select Bowler:",
        options=[],
        disabled=True,
        placeholder="Select a batsman first..."
    )

all_phases = ["allphase", "powerplay", "middle", "death"]
selected_phase = st.sidebar.selectbox("Select Phase:", options=all_phases, index=0)

min_year = int(df1["year"].min())
max_year = int(df1["year"].max())
year_range = st.sidebar.slider("Select Year Range:", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Your original matchups function
def matchups(yearstart, yearend, batter, bowler, phase):
    if phase not in ["powerplay", "middle", "death"]:
        df3 = df1[(df1["year"] >= yearstart) & (df1["year"] <= yearend) & (df1["bowler"] == bowler)]
    else:
        df3 = df1[(df1["year"] >= yearstart) & (df1["year"] <= yearend) & (df1["bowler"] == bowler) & (df1["phase"] == phase)]
    
    if len(df3) > 0:
        batsman = df3["striker"].unique()
        # print(batsman) # Streamlit doesn't use print for output
        if batter in batsman:
            d = {}
            striker = []
            runs = []
            balls = []
            sr = []
            outs = []
            rpi = []
            avg = []
            six = []
            
            for i in batsman:
                df4 = df3[(df3["striker"] == i)]
                striker.append(i)
                runs.append(df4["runs_off_bat"].sum())
                balls.append(df4["balls"].count())
                sr.append(((df4["runs_off_bat"].sum()) / (df4["balls"].count())) * 100)
                outs.append(len(df4[(df4.player_dismissed == i)]))
                rpi.append((df4["runs_off_bat"].sum()) / (len(df4["match_id"].unique())))
                avg.append((df4["runs_off_bat"].sum()) / (len(df4[(df4.player_dismissed == i)])))
                six.append((df4["runs_off_bat"].apply(lambda x: 1 if x == 6 else 0).sum()))

            d["Striker"] = striker
            d["Runs"] = runs
            d["Balls"] = balls
            d["SR"] = sr
            d["6s"] = six
            d["Outs"] = outs
            d["Rpi"] = rpi
            d["Avg"] = avg
            
            dfn = pd.DataFrame(d)
            
            meansr = dfn["SR"].mean()
            stdsr = dfn["SR"].std()
            dfn["zscore_sr"] = (dfn["SR"] - meansr) / stdsr
            dfn["zscore_rpi"] = (dfn["Rpi"] - (dfn["Rpi"].mean())) / (dfn["Rpi"].std())
            dfn["matchup_score"] = dfn["zscore_sr"] + dfn["zscore_rpi"]
            dfn["matchup_score"] = (dfn["matchup_score"] - dfn["matchup_score"].mean()) / (dfn["matchup_score"].std())
            dfn['Percentile Rank'] = dfn['matchup_score'].rank(pct=True)
            dfn = dfn.sort_values(by=["Percentile Rank"], ascending=False).reset_index(drop=True, inplace=False)
            
            # Display results in Streamlit
            st.header("Matchup Results")
            st.subheader(f"Analyzing: {batter} vs. {bowler} (Phase: {phase})")
            
            # Find and display the specific row for the selected batsman
            result_df = dfn[dfn["Striker"] == batter].copy()
            
            if not result_df.empty:
                st.dataframe(result_df)
            else:
                st.info("No data available/ Sample Size is too small")
        else:
            st.info("No data available/ Sample Size is too small")
    else:
        st.info("Bowler has not played")

# Conditional check to run the analysis
if selected_batsman and selected_bowler:
    matchups(year_range[0], year_range[1], selected_batsman, selected_bowler, selected_phase)
else:
    st.info("Please select a Batsman and a Bowler from the sidebar to view the matchup analysis.")

import pandas as pd
import warnings
import streamlit as st
import numpy as np

warnings.filterwarnings("ignore")

# Load data and perform initial cleaning
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(r"allipl.csv")
        df["match_date"] = pd.to_datetime(df["start_date"])
        df["year"] = df["match_date"].dt.year
        df = df.sort_values(by=["match_id", "innings", "ball"])
        df["ball"] = df["ball"].astype(str)
        df[["overs", "balls"]] = df["ball"].str.split(".", expand=True)
        df["overs"] = df["overs"].astype(int)
        df["balls"] = df["balls"].astype(int)
        df = df[(df["innings"] == 1) | (df["innings"] == 2)]

        def phase(x):
            if x <= 6:
                return "powerplay"
            elif x <= 15:
                return "middle"
            else:
                return "death"

        df["phase"] = df["overs"].apply(lambda x: phase(x))
        df1 = df[["match_id", "year", "striker", "bowler", "runs_off_bat", "balls", "overs", "phase", "player_dismissed"]]
        df1 = df1.replace(np.nan, 0)
        return df1
    except FileNotFoundError:
        st.error("Error: The CSV file 'allipl.csv' was not found. Please check the file path.")
        st.stop()

df1 = load_data()

# Streamlit UI
st.title("🏏 Cricket Matchup Analysis")

# Sidebar for user inputs
st.sidebar.header("Filters")

# First, select the Batsman
all_batsmen = sorted(df1["striker"].unique())
selected_batsman = st.sidebar.selectbox(
    "Select Batsman:",
    options=all_batsmen,
    index=None,
    placeholder="Choose a batsman..."
)

# Conditionally populate the bowler list
if selected_batsman:
    # Get all bowlers faced by the selected batsman
    bowlers_faced_df = df1[df1["striker"] == selected_batsman]
    all_bowlers = sorted(bowlers_faced_df["bowler"].unique())
    selected_bowler = st.sidebar.selectbox(
        "Select Bowler:",
        options=all_bowlers,
        index=None,
        placeholder="Choose a bowler..."
    )
else:
    # If no batsman is selected, show an empty or placeholder list for bowlers
    selected_bowler = st.sidebar.selectbox(
        "Select Bowler:",
        options=[],
        disabled=True,
        placeholder="Select a batsman first..."
    )

all_phases = ["allphase", "powerplay", "middle", "death"]
selected_phase = st.sidebar.selectbox("Select Phase:", options=all_phases, index=0)

min_year = int(df1["year"].min())
max_year = int(df1["year"].max())
year_range = st.sidebar.slider("Select Year Range:", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Your original matchups function
def matchups(yearstart, yearend, batter, bowler, phase):
    if phase not in ["powerplay", "middle", "death"]:
        df3 = df1[(df1["year"] >= yearstart) & (df1["year"] <= yearend) & (df1["bowler"] == bowler)]
    else:
        df3 = df1[(df1["year"] >= yearstart) & (df1["year"] <= yearend) & (df1["bowler"] == bowler) & (df1["phase"] == phase)]
    
    if len(df3) > 0:
        batsman = df3["striker"].unique()
        # print(batsman) # Streamlit doesn't use print for output
        if batter in batsman:
            d = {}
            striker = []
            runs = []
            balls = []
            sr = []
            outs = []
            rpi = []
            avg = []
            six = []
            
            for i in batsman:
                df4 = df3[(df3["striker"] == i)]
                striker.append(i)
                runs.append(df4["runs_off_bat"].sum())
                balls.append(df4["balls"].count())
                sr.append(((df4["runs_off_bat"].sum()) / (df4["balls"].count())) * 100)
                outs.append(len(df4[(df4.player_dismissed == i)]))
                rpi.append((df4["runs_off_bat"].sum()) / (len(df4["match_id"].unique())))
                avg.append((df4["runs_off_bat"].sum()) / (len(df4[(df4.player_dismissed == i)])))
                six.append((df4["runs_off_bat"].apply(lambda x: 1 if x == 6 else 0).sum()))

            d["Striker"] = striker
            d["Runs"] = runs
            d["Balls"] = balls
            d["SR"] = sr
            d["6s"] = six
            d["Outs"] = outs
            d["Rpi"] = rpi
            d["Avg"] = avg
            
            dfn = pd.DataFrame(d)
            
            meansr = dfn["SR"].mean()
            stdsr = dfn["SR"].std()
            dfn["zscore_sr"] = (dfn["SR"] - meansr) / stdsr
            dfn["zscore_rpi"] = (dfn["Rpi"] - (dfn["Rpi"].mean())) / (dfn["Rpi"].std())
            dfn["matchup_score"] = dfn["zscore_sr"] + dfn["zscore_rpi"]
            dfn["matchup_score"] = (dfn["matchup_score"] - dfn["matchup_score"].mean()) / (dfn["matchup_score"].std())
            dfn['Percentile Rank'] = dfn['matchup_score'].rank(pct=True)
            dfn = dfn.sort_values(by=["Percentile Rank"], ascending=False).reset_index(drop=True, inplace=False)
            
            # Display results in Streamlit
            st.header("Matchup Results")
            st.subheader(f"Analyzing: {batter} vs. {bowler} (Phase: {phase})")
            
            # Find and display the specific row for the selected batsman
            result_df = dfn[dfn["Striker"] == batter].copy()
            
            if not result_df.empty:
                st.dataframe(result_df)
            else:
                st.info("No data available/ Sample Size is too small")
        else:
            st.info("No data available/ Sample Size is too small")
    else:
        st.info("Bowler has not played")

# Conditional check to run the analysis
if selected_batsman and selected_bowler:
    matchups(year_range[0], year_range[1], selected_batsman, selected_bowler, selected_phase)
else:
    st.info("Please select a Batsman and a Bowler from the sidebar to view the matchup analysis.")
