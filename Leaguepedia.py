import streamlit as st
import pandas as pd
import mwclient
import plotly.graph_objects as go

# 简介 --------------------------------------------------------------------------
st.title('英雄联盟联赛数据查询程序')

'''
### 简介：

「英雄联盟联赛数据查询程序」使用[Leaguepedia](https://lol.fandom.com/wiki/League_of_Legends_Esports_Wiki)的开发者api来获取全球各大联赛（LPL/LDL/LCK/LEC/LCS等）的职业联赛数据。数据包含每场比赛的各项详细数据。

本程序仍处于测试调试阶段，目前只含有查询各联赛各赛季比赛数据的功能。后续版本会更新更多可供赛训团队人员使用的数据分析功能。**该程序仅限BLG俱乐部内部使用。**

'''

# 联赛数据查询 --------------------------------------------------------------------------
st.header('联赛数据查询')

# 筛选条件
options = st.multiselect(
    '请选择联赛和赛季',
    ['LPL/2021 Season/Summer Season', 'LCK/2021 Season/Summer Season',
     'LPL/2021 Season/Spring Season', 'LCK/2021 Season/Spring Season', '2021 Season World Championship/Main Event'],
    ['LPL/2021 Season/Summer Season'])

where = ''
for i in options:
    where += 'SG.OverviewPage = {}'.format("'{}'".format(i)) + ' OR '

conditions_SG = where[:-4]


site = mwclient.Site('lol.fandom.com', path='/')

response = site.api('cargoquery',
                    limit='max',
                    tables="ScoreboardGames=SG",
                    fields="SG.OverviewPage, SG.Tournament, SG.DateTime_UTC, SG.Patch ,SG.Team1, SG.Team2, SG.WinTeam ,SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, SG.Team2Picks, SG.GameId",
                    where=conditions_SG
                    )

SG_data = response['cargoquery']

SG = pd.DataFrame(SG_data[i]['title'] for i in range(len(SG_data)))


# BP数据
# BP条件筛选
where = ''
for i in options:
    where += 'BP.OverviewPage = {}'.format("'{}'".format(i)) + ' OR '

conditions_BP = where[:-4]

columns = '''Team1Role1,
                Team1Role2,
                Team1Role3,
                Team1Role4,
                Team1Role5,
                Team2Role1,
                Team2Role2,
                Team2Role3,
                Team2Role4,
                Team2Role5,
                Team1Ban1,
                Team1Ban2,
                Team1Ban3,
                Team1Ban4,
                Team1Ban5,
                Team1Pick1,
                Team1Pick2,
                Team1Pick3,
                Team1Pick4,
                Team1Pick5,
                Team2Ban1,
                Team2Ban2,
                Team2Ban3,
                Team2Ban4,
                Team2Ban5,
                Team2Pick1,
                Team2Pick2,
                Team2Pick3,
                Team2Pick4,
                Team2Pick5,
                Winner,
                Team1Score,
                Team2Score,
                Team1PicksByRoleOrder,
                Team2PicksByRoleOrder,
                OverviewPage,
                Phase,
                UniqueLine,
                Tab,
                N_Page,
                N_TabInPage,
                N_MatchInPage,
                N_GameInPage,
                N_GameInMatch,
                N_MatchInTab,
                N_GameInTab,
                GameId,
                MatchId,
                GameID_Wiki'''

site = mwclient.Site('lol.fandom.com', path='/')

response = site.api('cargoquery',
                    limit='max',
                    tables="PicksAndBansS7=BP",
                    fields=columns,
                    where=conditions_BP
                    )

BP_data = response['cargoquery']

BP = pd.DataFrame(BP_data[i]['title'] for i in range(len(BP_data)))

data = SG.merge(BP, on='GameId')

df = data[['Tournament', 'Tab', 'DateTime UTC', 'Patch', 'Team1',
             'Team2', 'WinTeam', 'Team1Ban1', 'Team1Ban2', 'Team1Ban3', 'Team1Ban4', 'Team1Ban5',
             'Team2Ban1', 'Team2Ban2', 'Team2Ban3', 'Team2Ban4', 'Team2Ban5',
             'Team1Pick1', 'Team1Pick2', 'Team1Pick3', 'Team1Pick4', 'Team1Pick5',
             'Team2Pick1', 'Team2Pick2', 'Team2Pick3', 'Team2Pick4', 'Team2Pick5',
             'Team1PicksByRoleOrder', 'Team2PicksByRoleOrder']]

st.dataframe(df)


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


csv = convert_df(df)

st.download_button(
    label="下载数据",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',)


# 队伍数据查询 --------------------------------------------------------------------------
st.header('队伍数据查询')

tmp = pd.DataFrame(df[['Team1', 'Team2']].unstack())
teams = tmp[0].unique()

team = st.selectbox('请选择要分析的队伍',(teams))

team_data = df[(df['Team1']==team) | (df['Team2']==team)]
win_rate = str(round(len(team_data[team_data['WinTeam']==team])/len(team_data), 4) * 100)+'%'

team_dashboard_data = pd.DataFrame()
for i in teams:
    team_data_i = df[(df['Team1']==i) | (df['Team2']==i)]
    metrics_i = pd.DataFrame({'Team': [i],
                              'WinRate': [round(len(team_data_i[team_data_i['WinTeam']==i])/len(team_data_i) * 100 , 2)],
                              'Wins': [len(team_data_i[team_data_i['WinTeam']==i])],
                              'Total': [len(team_data_i)]})
    team_dashboard_data = team_dashboard_data.append(metrics_i, ignore_index=True)

team_dashboard_data = team_dashboard_data.set_index('Team')
team_dashboard_data['WinRate_rank'] = team_dashboard_data['WinRate'].rank(ascending=False).astype(int)

col1, col2, col3 = st.columns(3)
col1.metric("队伍胜率", str(team_dashboard_data.loc[team, 'WinRate'])+'%', '第{}名'.format(team_dashboard_data.loc[team, 'WinRate_rank']))
col2.metric("队伍胜场", str(team_dashboard_data.loc[team, 'Wins']))
col3.metric("队伍总场数", str(team_dashboard_data.loc[team, 'Total']))

st.subheader('队伍比赛数据')
st.dataframe(team_data)

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


csv_2 = convert_df(team_data)

st.download_button(
    label="下载数据",
    data=csv_2,
    file_name='large_df.csv',
    mime='text/csv',)

# 队伍BP数据
st.subheader('队伍BP数据')

# Ban数据
team_blue = team_data[team_data['Team1']==team]
team_red = team_data[team_data['Team2']==team]
team_blue_ban = pd.DataFrame(pd.DataFrame(team_blue[['Team1Ban1', 'Team1Ban2', 'Team1Ban3', 'Team1Ban4', 'Team1Ban5']].unstack())[0].value_counts()).reset_index()
team_red_ban = pd.DataFrame(pd.DataFrame(team_red[['Team2Ban1', 'Team2Ban2', 'Team2Ban3', 'Team2Ban4', 'Team2Ban5']].unstack())[0].value_counts()).reset_index()
team_blue_ban.columns = ['Champion', 'Count']
team_red_ban.columns = ['Champion', 'Count']

team_ban = team_blue_ban.merge(team_red_ban, how='outer')
team_ban = pd.DataFrame(team_ban.groupby(['Champion'])['Count'].sum()).sort_values(by='Count', ascending=False).reset_index()
team_ban.columns = ['Champion', 'Count']


col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write('总体Ban数据')
    st.dataframe(team_ban)


with col2:
    st.write('蓝色方Ban数据')
    st.dataframe(team_blue_ban)

with col3:
    st.write('红色方Ban数据')
    st.dataframe(team_red_ban)

with col4:
    fig = go.Figure(go.Bar(
                x=team_ban.head(10)['Count'],
                y=team_ban.head(10)['Champion'],
                marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(color='rgba(50, 171, 96, 1.0)', width=1),
            ),
                orientation='h'))
    st.plotly_chart(fig, use_container_width=True)

# Pick数据
team_blue = team_data[team_data['Team1']==team]
team_red = team_data[team_data['Team2']==team]
team_blue_pick = pd.DataFrame(pd.DataFrame(team_blue[['Team1Pick1', 'Team1Pick2', 'Team1Pick3', 'Team1Pick4', 'Team1Pick5']].unstack())[0].value_counts()).reset_index()
team_red_pick = pd.DataFrame(pd.DataFrame(team_red[['Team2Pick1', 'Team2Pick2', 'Team2Pick3', 'Team2Pick4', 'Team2Pick5']].unstack())[0].value_counts()).reset_index()
team_blue_pick.columns = ['Champion', 'Count']
team_red_pick.columns = ['Champion', 'Count']

team_pick = team_blue_pick.merge(team_red_pick, how='outer')
team_pick = pd.DataFrame(team_pick.groupby(['Champion'])['Count'].sum()).sort_values(by='Count', ascending=False).reset_index()
team_pick.columns = ['Champion', 'Count']


col1, col2, col3 = st.columns(3)
with col1:
    st.write('总体Pick数据')
    st.dataframe(team_pick)

with col2:
    st.write('蓝色方Pick数据')
    st.dataframe(team_blue_pick)

with col3:
    st.write('红色方Pick数据')
    st.dataframe(team_red_pick)
