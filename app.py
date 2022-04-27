import streamlit as st
import pandas as pd
import pickle
from pathlib import Path
from zipfile import ZipFile

st.set_page_config(
    page_title="Player Recommender",
    page_icon=":soccer:"
)


@st.cache(show_spinner=False)
def getData():
    # loading data

    player_df = pd.read_pickle(r'data/players.pkl')
  
    with open(r'data/player_ID.pickle', 'rb') as file:
        player_ID = pickle.load(file)

    with ZipFile("data/engine.pickle.zip", 'r') as zip:
        with zip.open('engine.pickle') as myfile:
            engine = pickle.load(myfile)


    return [player_df, player_ID, engine]
    

outfield_data = getData()


header = st.container()
data_info1 = st.container()
params = st.container()
result = st.container()


with header:
    st.title('Project Mbappe')

with params:
    st.text(' \n')
    st.text(' \n')
    st.header('Tweak the parameters')


    df, player_ID, engine = outfield_data
   
    players = sorted(list(player_ID.keys()))
    age_default = (min(df['Age']), max(df['Age']))

    

    col1, col2, col3, col4 = st.columns([0.7, 1, 1, 1])
    with col1:
        
        res, val, step = (5, 20), 10, 5
        count = st.slider('Number of results', min_value=res[0], max_value=res[1], value=val, step=step)

    with col2:
        comp = st.selectbox('League', ['All', 'Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'],
            help='Leagues to get recommendations from. \'All\' leagues by default.')

    with col3:
        comparison = st.selectbox('Comparison with', ['All positions', 'Same position'],
            help='Whether to compare the selected player with all positions or just the same defined position in the dataset. \'All \
            positions\' by default.')
    with col4:
        age = st.slider("Age", min_value=age_default[0],max_value=age_default[1],value=25)


    query = st.selectbox('Player name', players, 
        help='Type without deleting a character. To search from a specific team, just type in the club\'s name.')
    

    st.markdown('_showing recommendations for_ **{}**'.format(query))
    with result:
        st.text(' \n')
        st.text(' \n')
        st.text(' \n')
        

        def getRecommendations(metric, league='All', comparison='All positions', age=age_default, count=val):
            
            df_res = df.iloc[:, [1, 3, 5, 6, 11]].copy()
            df_res['Player'] = list(player_ID.keys())
            df_res.insert(1, 'Similarity', metric)
            df_res = df_res.sort_values(by=['Similarity'], ascending=False)
            metric = [str(num) + '%' for num in df_res['Similarity']]
            df_res['Similarity'] = metric
            df_res = df_res.iloc[1:, :]


            
            if comparison == 'Same position':
                q_pos = list(df[df['Player']==query.split(':')[0]].Pos)[0]
                df_res = df_res[df_res['Pos']==q_pos]


            if league=='All':
                pass
            else:
                
                if(league=="Premier League"):
                    league = "Premier"
                if(league=="La Liga"):
                    league = "La"
                if(league=="Seria A"):
                    league = "Serie"
                if(league=="Ligue 1"):
                    league = "Ligue"

                df_res = df_res[df_res['Comp']==league]

            
            if age!=age_default:
                df_res = df_res[(df_res['Age'] >= age_default[0]) & (df_res['Age'] <= age)]
            

            #data cleaning to present data better
            df_res = df_res.iloc[:count, :].reset_index(drop=True)
            df_res.index = df_res.index + 1
            mp90 = [str(round(num, 1)) for num in df_res['90s']]
            df_res['90s'] = mp90
            df_res.rename(columns={'Pos':'Position', 'Comp':'League'}, inplace=True)
            
            return df_res


    sims = engine[query]
    recoms = getRecommendations(sims, league=comp, comparison=comparison, age=age, count=count)
    st.table(recoms)
    
