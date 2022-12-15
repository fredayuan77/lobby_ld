from lobby_ld import lobby_ld

import os
import sys
import pytest 
import requests
import pandas as pd
import json 
import numpy as np

token = os.getenv('PRIVATE_API_KEY')

def test_get_file_summary():
    data = {'year_quarter': ['2021Q4', '2022Q1'], 'number_of_reports': [13, 5], 'total_expense': [746000.0, 0],
            'total_income': [245000.0, 0], 'number_of_clients': [3, 3], 'number_of_registrants': [10, 5]}
    df_expected = pd.DataFrame(data=data, index=[0, 1])
    df_expected.set_index(["year_quarter"], inplace=True)
    df_actual = lobby_ld.LobbyFile(token, '01/25/2022', '02/10/2022', 'NJ').get_file_summary()
    assert df_expected.equals(df_actual), 'returned dataframe is not equal to actual dataframe'

def test_get_issue_file():
    path = 'test_activity.csv'
    df_expected = pd.read_csv(path)
    df_actual = lobby_ld.LobbyIssue(token, 2022, 'education', 'NJ').get_issue_file()
    assert df_expected.equals(df_actual), 'error with getting the issue files'


def test_get_issue_description():
    expected = ['Environment/Superfund', 'Science/Technology', 'Health Issues']
    actual = lobby_ld.LobbyIssue(token, 2022, 'water quality', 'MA').get_issue_description()
    assert expected == actual, 'fail to return correct issue description'

def test_get_issue_lobbyist():
    path = 'test_issue_lobbyist.csv'
    df_expected = pd.read_csv(path)
    df_actual = lobby_ld.LobbyIssue(token, 2022, 'trade', 'MA').get_issue_lobbyist()
    assert df_expected.equals(df_actual), 'error with getting lobbyist information dataframe'

def test_get_lobbyists_count():
    expected = '180 unique lobbyists are hired by NJ clients to work on health issues in 2021.'
    actual = lobby_ld.LobbyIssue(token, 2021, 'health', 'NJ').get_lobbyists_count()
    assert expected == actual, 'fail to return correct lobbyist count'


def test_get_lobbyists_name():
    expected = ['JOHNIE BOATRIGHT', 'ROGER SZEMRAJ', 'PHILIP KARSTING',
                'JENNIFER CERVANTES', 'RYAN WESTON', 'VAN HIPP', 'ROBIN WALKER',
                'JOHN PROVENZANO', 'TODD WEISS', 'JOHN BREAUX', 'JASON GLEASON',
                'WALLY BURNETT', 'SALIM ALAMEDDIN', 'JOHN GREEN',
                'MATHEW LAPINSKI', 'STEWART HALL', 'HUNTER MOORHEAD',
                'MARK WARREN', 'EDWARD ROYCE', 'SAMANTHA CARL-YODER',
                'DANIEL JOSEPH', 'CARMENCITA WHONDER', 'DOUGLAS MAGUIRE',
                'RUSSELL SULLIVAN', 'HAROLD HANCOCK', 'JAMES DAVENPORT',
                'JOHN MONSIF', 'KYLE GILLEY', 'STEVE DANON', 'JODI BOCK DAVIDSON',
                'ALEX KRIGSTEIN', 'SARAH MATHIAS', 'ADAM GOODMAN', 'HENRY MENN',
                'BRENDA OTTERSON', 'HARRY GLENN', 'STEVEN GIULI', 'JOSE DIAZ',
                'BRIAN BALLARD', 'MARCKIA HAYES']

    actual = lobby_ld.LobbyIssue(token, 2022, 'food', 'FL').get_lobbyists_name()
    assert expected == actual, 'fail to return correct lobbyist names'


