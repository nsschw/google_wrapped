import pandas as pd
from dateutil import parser
import plotly.graph_objects as go
import numpy as np
import re

class DataProcessor:    
    def __init__(self, dataset_path, **kwargs):
        self.dataset_path = dataset_path
        self.language = kwargs.get("lang", "en")
        self.kwargs = kwargs        

        # read dataset
        self.df = pd.read_json(dataset_path)

        # prepare basic datasets
        self.df_preprocessed = self.basic_preprocess()
        self.df_searches = self.get_searches()


    def basic_preprocess(self) -> pd.DataFrame():
        preprocessed_df = self.df.copy()
        preprocessed_df['time'] = preprocessed_df['time'].apply(lambda x: parser.parse(x))
        preprocessed_df['time'] = preprocessed_df['time'].dt.tz_convert('Europe/Berlin')
        preprocessed_df['time'] = preprocessed_df['time'].dt.strftime('%Y-%m-%d %H:%M:%S') 

        # filter by date
        if self.kwargs.get("from_date"):
            preprocessed_df = preprocessed_df[preprocessed_df['time'] >= self.kwargs.get("from_date")]
        if self.kwargs.get("until_date"):
            preprocessed_df = preprocessed_df[preprocessed_df['time'] <= self.kwargs.get("until_date")]
        return preprocessed_df


    def get_searches(self) -> pd.DataFrame():
        df_searches = self.df_preprocessed.copy()

        if self.language == "de":
            df_searches = df_searches [df_searches['title'].str.contains('Gesucht nach')].reset_index(drop=True)
            df_searches["title"] = df_searches["title"].str.replace("Gesucht nach:", "")
        elif self.language == "en":
            df_searches = df_searches [df_searches['title'].str.contains('Searched for')].reset_index(drop=True)
            df_searches["title"] = df_searches["title"].str.replace("Searched for", "")
        return df_searches 


    def basic_facts(self) -> dict:      
        # total number of searches
        count_searches = len(self.df_searches)

        # day with most searches
        df = self.df_searches.copy()
        df['time'] = pd.to_datetime(df['time'])
        df['time'] = df['time'].dt.to_period("D")
        searches_per_day = df.groupby(["time"]).size().reset_index(name="count").sort_values(by="count", ascending=False).reset_index(drop=True)        
        
        date_most_searches = searches_per_day["time"][0]
        amount_most_searches = searches_per_day["count"][0], " searches"

        # longest search pause
        df = self.df_searches.copy()
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values(by="time", ascending=True).reset_index(drop=True)
        df["duration"] = df["time"].diff()

        longest_pause = df["duration"].max()

        # longest search term
        df = self.df_searches.copy()
        df["length"] = df["title"].str.len()
        df = df.sort_values(by="length", ascending=False).reset_index(drop=True)
        longest_search_term = df["title"][0]

        return {"count_searches": count_searches, "date_most_searches": date_most_searches, "amount_most_searches": amount_most_searches, "longest_pause": longest_pause, "longest_search_term": longest_search_term}


    def searches_heatmap(self, fill_nan: bool = False) -> go.Figure():
        df = self.df_searches.copy()
        df['time'] = pd.to_datetime(df['time'])
        df["day"] = df['time'].dt.day_name()
        df['time'] = df['time'].dt.to_period("H").apply(lambda r: r.start_time)        
        df["time"] = df['time'].dt.hour

        df = df.groupby(["day", "time"]).size().reset_index(name="count")
        df = df.pivot(index='time', columns='day', values='count')
        df = df.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], axis=1)
        df = df.reindex([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14, 15, 16, 17, 18, 19, 20, 21, 22, 23], axis=0)
        
        if fill_nan == True:
            df = df.replace(np.nan, 0)

        # plot heatmap so that the first hour is at the top
        order_of_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]      

        fig = go.Figure(data=go.Heatmap(
                    z=df.values,
                    x=df.columns,
                    y=df.index,
                    colorscale='Bluered',
                    hoverongaps=False))
        fig.update_layout(
            title="Searches per hour and day",
            yaxis={'title':'Hours','categoryarray': order_of_hours, 'autorange':'reversed', },
            xaxis={'title':'Day of Week'},
            margin=dict(l=5, r=5, t=35, b=5),
            paper_bgcolor="#F7F7F7",
            plot_bgcolor="#F7F7F7",
            xaxis_showgrid=False,
            yaxis_showgrid=False,            
            font_family="Arial",
            font_color="#333333",
            title_x=0.5,
            title_y=0.99,
            title_xanchor='center',
            title_yanchor='top',
            font_size=12,
        )

        return fig    


    def searched_most(self, n:int=20) -> go.Figure():
        df = self.df_searches.copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            orientation='h',  # Update orientation to vertical
            x=df['title'].value_counts().head(n).values[::-1],  # Reverse the order of values
            y=df['title'].value_counts().head(n).index[::-1],  # Reverse the order of index
            name='Most searched terms',
            marker=dict(
                color=df['title'].value_counts().head(n).values[::-1],
                colorscale='Bluered'
            )
            ))
        fig.update_layout(
            title="Most searched Terms",
            xaxis_title="Searches",
            yaxis_title="Term",
            margin=dict(l=5, r=5, t=35, b=5),
            paper_bgcolor="#F7F7F7",
            plot_bgcolor="#F7F7F7",
            xaxis_showgrid=False,
            yaxis_showgrid=False,            
            font_family="Arial",
            font_color="#333333",
            title_x=0.5,
            title_y=0.99,
            title_xanchor='center',
            title_yanchor='top',
            font_size=12,
        )
        return fig
    

    def searches_per_week(self) -> go.Figure():
        df = self.df_searches.copy()
        df['time'] = pd.to_datetime(df['time'])
        df["first_day_of_week"] = df['time'].dt.to_period('W').apply(lambda r: r.start_time)
        df = df.groupby(['first_day_of_week']).size().reset_index(name='count')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['first_day_of_week'], y=df['count'],
                            mode='lines',
                            name='lines',
                            fill='tozeroy'))
        fig.update_layout(
            title="Number of Searches per Week",
            xaxis_title="Week",
            yaxis_title="Searches",
            margin=dict(l=5, r=5, t=35, b=5),
            paper_bgcolor="#F7F7F7",
            plot_bgcolor="#F7F7F7",
            xaxis_showgrid=False,
            yaxis_showgrid=False,            
            font_family="Arial",
            font_color="#333333",
            title_x=0.5,
            title_y=0.99,
            title_xanchor='center',
            title_yanchor='top',
            font_size=12,
            
        )
        return fig


    def search_locations(self) -> go.Figure():
        df = self.df_searches.copy()
        df = df.dropna(subset=["locationInfos"]).reset_index(drop=True)

        pattern = r"center=([-+]?\d*\.\d+|\d+),([-+]?\d*\.\d+|\d+)"       

        for i in range(len(df["locationInfos"])):            
            if df["locationInfos"][i][0]["url"]:
                url = df["locationInfos"][i][0].get("url") 
                match = re.search(pattern, url)        
            if match:
                latitude, longitude = match.groups()
                df.loc[i, "latitude"] = latitude
                df.loc[i, "longitude"] = longitude
        
        df = df.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
        
        df["latitude"] = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)

        fig = go.Figure(go.Scattermapbox(
            lat=df["latitude"],
            lon=df["longitude"],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=df["title"],
        ))

        fig.update_layout(
            title="Searched from",
            margin=dict(l=5, r=5, t=35, b=5),
            paper_bgcolor="#F7F7F7",
            plot_bgcolor="#F7F7F7",
            xaxis_showgrid=False,
            yaxis_showgrid=False,            
            font_family="Arial",
            font_color="#333333",
            title_x=0.5,
            title_y=0.99,
            title_xanchor='center',
            title_yanchor='top',
            font_size=12,
            mapbox_style="open-street-map",
            mapbox=dict(
                center=go.layout.mapbox.Center(
                    lat=51.1657,
                    lon=10.4515
                ),
                zoom=4
            ),
        )
        return fig