#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 20:45:43 2021

@author: jenny
"""

import streamlit as st 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

@st.cache(allow_output_mutation=True)  
def get_data():
	return pd.read_csv('Main Dataset V2.csv')
main_data = get_data()

all_ind = sorted(list(set(main_data['Stock Name'])))

Ticker = st.selectbox("Select a Company",all_ind)

bloom_dtd_grouped = main_data.groupby(['Stock Name', 'Date'], sort = False).mean().reset_index()

# Select the most recent day for each unique stock
recent_day_7 = bloom_dtd_grouped.groupby('Stock Name').first().reset_index()


# select the 7th most recent day for each unique stock
prior_week_7 = bloom_dtd_grouped.groupby('Stock Name').nth(6).reset_index()

# create a new dataframe with the difference of DTD between the most recent day and the 7th most recent day
new_df_7 = recent_day_7.merge(prior_week_7, on = 'Stock Name')

# Kepp only the columns we need
new_df_7 = new_df_7[['Stock Name','Date_x', 'Date_y', 'DTD_x', 'DTD_y']]

# Create a new column with the percent change in DTD between the most recent day and the 7th most recent day
new_df_7['DTD Change'] = (new_df_7['DTD_x']-new_df_7['DTD_y'])

recent_day_1 = bloom_dtd_grouped.groupby('Stock Name').first().reset_index()

# select the 7th most recent day for each unique stock
prior_year = bloom_dtd_grouped.groupby('Stock Name').nth(260).reset_index()

# create a new dataframe with the difference of DTD between the most recent day and the 7th most recent day
new_df_1 = recent_day_1.merge(prior_year, on = 'Stock Name')

# Kepp only the columns we need
new_df_1 = new_df_1[['Stock Name','Date_x', 'Date_y', 'DTD_x', 'DTD_y']]

# Create a new column with the percent change in DTD between the most recent day and the 7th most recent day
new_df_1['DTD Change'] = (new_df_1['DTD_x']-new_df_1['DTD_y'])

 



col1, col2, col3, col4 = st.columns(4)



col2.metric('Current DTD', new_df_7[new_df_7['Stock Name'] == Ticker]['DTD_x'].iloc[0].round(2))
col3.metric('7D DTD Change', new_df_7[new_df_7['Stock Name'] == Ticker]['DTD Change'].iloc[0].round(2))
col4.metric('1Y DTD Change', new_df_1[new_df_1['Stock Name'] == Ticker]['DTD Change'].iloc[0].round(2))



subset = main_data.loc[main_data['Stock Name']==Ticker]

subset['Date'] = pd.to_datetime(subset['Date'])
no_null = subset[subset['mov_avg'].notna()]
most_recent = no_null.loc[no_null['Date']==no_null['Date'].max()]



info = go.Figure(data=[go.Table(
    header=dict(values=['',''],
                line_color='rgba(0,0,0,0)',
                fill_color='rgba(0,0,0,0)',
                align='center',
                font=dict(color='white', size=15),
                height=25),
    cells=dict(values=[['Industry','Current Market Capital (Millions)','30 Day Volatility (%)','90 Day Volatility (%)','260 Day Volatility (%)','Total Debt (Millions)','Price to Earnings Ratio','Price to Book Ratio'],
                       [most_recent['Sector'],most_recent['Current Market Cap'],most_recent['Volatility 30 Day'],most_recent['Volatility 90 Day'],most_recent['Volatility 260 Day'],most_recent['Short and Long Term Debt'],most_recent['Price Earnings Ratio (P/E)'],most_recent['Price to Book Ratio']]],
               line_color='white',
               fill_color=[['white','gainsboro','white','gainsboro','white','gainsboro','white','gainsboro','white']*2],
               align='center',
               font=dict(color='dimgrey', size=15),
               height=25))
    ])

info.update_layout(
    margin=dict(t=10)
)

st.subheader(Ticker + ' Financials')
st.plotly_chart(info,use_container_width=True, config=dict(displayModeBar=False))

#Ticker2 = st.selectbox("Select Company to Compare to",all_ind,index=all_ind.index(Ticker))

#subset_2 = main_data.loc[main_data['Stock']==Ticker2]
#subset_2['Date'] = pd.to_datetime(subset['Date'])

#merged = pd.merge(subset[['Date','Stock','Last Price','DTD']],subset_2[['Date','Stock','Last Price','DTD']],on='Date',how='outer')
st.subheader('Share Price and Distance to Default Over Time')
col1, col2 = st.columns(2)

fig1 = px.line(subset,x='Date',y='Last Price',  title="Share Price Over Time", labels={
                     "Last Price": "Share Price"})
fig2 = px.line(subset,x='Date',y='mov_avg', title="20 Day DTD Moving Average", labels={
                     "mov_avg": "DTD Moving Average"})



fig1.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

fig2.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)


col1.plotly_chart(fig1,use_container_width=True, config=dict(displayModeBar=False))
col2.plotly_chart(fig2,use_container_width=True, config=dict(displayModeBar=False))

#col1.plotly_chart(name)
#col1.plotly_chart(info)
#col2.plotly_chart(fig1)
#col2.plotly_chart(fig2)

bloom_dtd_grouped = main_data.groupby(['Stock Name', 'Sector'], sort = False).mean().reset_index()


# Normalise the 'Last Price', 'Current Market Cap', 'Volatility 30 Day', 'Long Term Debt', 'Short Term Debt' columns
bloom_dtd_grouped[['Last Price', 'Current Market Cap', 'Volatility 30 Day', 'Long Term Debt', 'Short Term Debt']] = bloom_dtd_grouped[['Last Price', 'Current Market Cap', 'Volatility 30 Day', 'Long Term Debt', 'Short Term Debt']].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

# Make sure that all columns, including 'Stock' and 'Sector' are still callable in the dataframe
bloom_dtd_grouped = bloom_dtd_grouped[['Stock Name', 'Sector', 'Last Price', 'Current Market Cap', 'Volatility 30 Day', 'Long Term Debt', 'Short Term Debt']]


stock_frame = bloom_dtd_grouped[bloom_dtd_grouped['Stock Name'] == Ticker]


# Get all the tickers from the same sector
stock_sector = bloom_dtd_grouped.loc[bloom_dtd_grouped['Sector'] == stock_frame['Sector'].iloc[0]]

# Drop row from sector_tickers where 'Stock' is 'WOW AU'
sector_tickers = stock_sector[stock_sector['Stock Name'] != Ticker]
    
# Randomly select 4 stocks that are in the same sector
tickers = sector_tickers.sample(3)


categories = ['Stock Price','Market Cap','Volatility',
              'Long Term Debt', 'Short Term Debt']

pol_fig1 = go.Figure()
pol_fig1.add_trace(go.Scatterpolar(
      r=stock_frame.iloc[0],
      theta=categories,
      fill='toself',
    ))
 

pol_fig1.update_layout(
            polar=dict(
    radialaxis=dict(
      visible=False
    )),
  showlegend=False,
     paper_bgcolor='rgba(0,0,0,0)', title_text = Ticker, title={
        'y':1,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    plot_bgcolor='rgba(0,0,0,0)', height = 250,
    margin=dict(t=20,l=30,b=20,r=30)
)
st.subheader(Ticker + ' Make up vs. Sector Competitors')



pol_fig2 = go.Figure()
pol_fig2.add_trace(go.Scatterpolar(
      r=tickers.iloc[0],
      theta=categories,
      fill='toself',
      subplot="polar"
    ))

pol_fig2.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=False
    )), 
  showlegend=False, title_text = tickers['Stock Name'].iloc[0], title={
        'y':1,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
   paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', height = 250, 
   margin=dict(t=20,l=30,b=20,r=30)
)


pol_fig3 = go.Figure()
pol_fig3.add_trace(go.Scatterpolar(
      r=tickers.iloc[1],
      theta=categories,
      fill='toself',
      subplot="polar"
    ))

pol_fig3.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=False
    )),
  showlegend=False,
   paper_bgcolor='rgba(0,0,0,0)', title_text = tickers['Stock Name'].iloc[1], title={
        'y':1,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    plot_bgcolor='rgba(0,0,0,0)', height = 250, 
   margin=dict(t=20,l=30,b=20,r=30)
)

pol_fig4 = go.Figure()
pol_fig4.add_trace(go.Scatterpolar(
      r=tickers.iloc[2],
      theta=categories,
      fill='toself',
      subplot="polar"
    ))

pol_fig4.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=False
    )),
  showlegend=False,
   paper_bgcolor='rgba(0,0,0,0)', title_text = tickers['Stock Name'].iloc[2], title={
        'y':1,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    plot_bgcolor='rgba(0,0,0,0)', height = 250, 
   margin=dict(t=20,l=30,b=20,r=30)
)



col1, col2, = st.columns(2)

col1.plotly_chart(pol_fig1,use_container_width=True, config=dict(displayModeBar=False))
col2.plotly_chart(pol_fig2,use_container_width=True, config=dict(displayModeBar=False))

col1, col2, = st.columns(2)

col1.plotly_chart(pol_fig3,use_container_width=True, config=dict(displayModeBar=False))
col2.plotly_chart(pol_fig4,use_container_width=True, config=dict(displayModeBar=False))

bloom_fill = main_data.groupby(['Stock Name', 'Date'], sort = False).mean().reset_index()

fill_fig = go.Figure()
fill_fig.add_trace(go.Scatter(x=bloom_fill[bloom_fill['Stock Name'] == Ticker]['Date']
                         ,y=bloom_fill[bloom_fill['Stock Name'] == Ticker]['Price Earnings Ratio (P/E)'], fill='tozeroy', name = 'PE Ratio'),) 

fill_fig.add_trace(go.Scatter(x=bloom_fill[bloom_fill['Stock Name'] == Ticker]['Date']
                         ,y=bloom_fill[bloom_fill['Stock Name'] == Ticker]['Price to Book Ratio'], fill='tozeroy', name = 'PB Ratio')) 

fill_fig.update_layout(showlegend = True, height = 400, width = 500,
                       paper_bgcolor='rgba(0,0,0,0)',  xaxis_title="Date",
    plot_bgcolor='rgba(0,0,0,0)',margin=dict(t=10,l=10,b=10,r=10))

fill_fig.update_xaxes(nticks = 20)
st.subheader('Price to Earnings Ratio and Price to Book Ratio Over Time')

st.plotly_chart(fill_fig,use_container_width=True, config=dict(displayModeBar=False))

