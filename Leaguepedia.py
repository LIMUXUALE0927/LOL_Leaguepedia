import streamlit as st
import pandas as pd
import mwclient

st.title('Leaguepedia数据查询程序')

site = mwclient.Site('lol.fandom.com', path='/')

response = site.api('cargoquery',
    limit = 'max',
    tables = "ScoreboardGames=SG",
    fields = "SG.Tournament, SG.DateTime_UTC, SG.Patch ,SG.Team1, SG.Team2, SG.WinTeam ,SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, SG.Team2Picks, SG.GameId",
    where = "SG.Tournament='LPL 2021 Summer'"
)

SG_data = response['cargoquery']

SG = pd.DataFrame(SG_data[i]['title'] for i in range(len(SG_data)))

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
    limit = 'max',
    tables = "PicksAndBansS7=BP",
    fields = columns,
    where = "BP.OverviewPage='LPL/2021 Season/Summer Season'"
)

BP_data = response['cargoquery']

BP = pd.DataFrame(BP_data[i]['title'] for i in range(len(BP_data)))

data = SG.merge(BP, on='GameId')

st.dataframe(data)
