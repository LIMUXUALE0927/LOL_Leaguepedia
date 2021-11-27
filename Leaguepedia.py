import streamlit as st
import pandas as pd
import mwclient

# 简介 --------------------------------------------------------------------------
st.title('英雄联盟联赛数据查询程序')

'''
### 简介：

「英雄联盟联赛数据查询程序」使用Leaguepedia的开发者api来获取全球各大联赛（LPL/LDL/LCK/LEC/LCS等）的职业联赛数据。数据包含每场比赛的各项详细数据。

本程序仍处于测试调试阶段，目前只含有查询各联赛各赛季比赛数据的功能。后续版本会更新更多可供赛训团队人员使用的数据分析功能。**该程序仅限BLG俱乐部内部使用。**

'''

# 联赛数据查询 --------------------------------------------------------------------------
st.markdown('### 联赛数据查询')

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
st.markdown('### 队伍数据查询')

tmp = pd.DataFrame(df[['Team1', 'Team2']].unstack())
teams = tmp[0].unique()

team = st.selectbox('请选择要分析的队伍',(teams))

team_data = df[(df['Team1']==team) | (df['Team2']==team)]
win_percent = str(round(len(team_data[team_data['WinTeam']==team])/len(team_data), 4) * 100)+'%'

col1, col2, col3 = st.columns(3)
col1.metric("队伍胜率", win_percent)
col2.metric("队伍胜场", "9 mph", "-8%")
col3.metric("队伍总场数", "86%", "4%")
