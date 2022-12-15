import requests
import os
import pandas as pd
import json 
import numpy as np
import dateutil.parser as parser


token = os.getenv('PRIVATE_API_KEY')

class LobbyFile():
    
    def __init__(self, token, start_date, end_date, client_state):
        """Initialize a Lobby API. """
        self.ld_token = token
        self.start_date = start_date
        self.end_date = end_date
        self.client_ppb_state = client_state

    def get_file_summary(self):
        """
        Get summary statistics on selected lobbying files. 
        
        Output is aggregated by year and quarter. Summary infomation includes:
        number of reports filed during the requested period, 
        total expenses associated with these reports, 
        total income associated with these reports,
        number of unique clients filed reports during the period, 
        and number of unique registrants (lobbying companies or other individual organizations) filed reports during the period.

        Parameters
        ----------
        token : string.
            The token requested from Lobbying Disclosure Website. 
        start_date : string. 
            The start date for requested filing posted period. Date in the 'MM/DD/YYYY' format.
        end_date : string.
            The end date for requested filing posted period. Date in the 'MM/DD/YYYY' format.
        client_state: string.
            The U.S. state location of lobbying clients or organizations. State name is in two letter abbreviation format.

        Returns
        -------
        pandas.DataFrame
            A pandas dataframe indicates summary information of filtered lobbying files. Index is year_quarter, and columns are aggregated statistics. 

        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> lobby_api = lobby_lda.LobbyFile(token, '01/25/2022', '02/10/2022','NJ')
        >>> lobby_api.get_file_summary()

        ============= ================= ============= ============ ================= =====================
        year_quarter  number_of_reports	total_expense total_income number_of_clients number_of_registrants
        ============= ================= ============= ============ ================= =====================
        2021Q4	      13	            746000.0	  245000.0	   3	             10
        2022Q1	      5	                0.0	          0.0	       3	             5
        ============= ================= ============= ============ ================= =====================
        """

        session = requests.Session()
        session.params = {}
        session.params['api_key'] = self.ld_token

        # parse date entered into datetime python format 
        date1 = parser.parse(self.start_date)
        date2 = parser.parse(self.end_date)

        params = {
        "filing_dt_posted_after": date1,
        "filing_dt_posted_before" : date2,
        "client_ppb_state": self.client_ppb_state}

        r = session.get('https://lda.senate.gov/api/v1/filings/', params = params).json()
        results = r['results']
        # to obtain all results on all pages 
        while r['next']:
            r = requests.get(r['next']).json()
            results.extend(r['results'])
        #convert json to pd.DataFrame
        df = pd.json_normalize(results)


        # #create year_quarter
        dict = {'first_quarter': 'Q1', 'second_quarter' :'Q2', 'third_quarter':'Q3','fourth_quarter':'Q4',"mid_year":'Q2','year_end':'Q4'}
        # create new column year_quarter
        df['year_quarter'] = df['filing_year'].astype(str) + df['filing_period'].map(dict)

        #convert income and expense from string to int, used for calculation later
        df['expenses'].replace([None], 0, inplace=True)
        df['expenses'] = df['expenses'].astype(float)
        df['income'].replace([None], 0, inplace=True)
        df['income'] = df['income'].astype(float)

        # groupby year and quarter, show aggregated result
        df_summary = df.groupby(by = ['year_quarter']).agg({'filing_uuid': 'nunique', 'expenses': 'sum','income':'sum','client.client_id':'nunique','registrant.id':'nunique'})
        df_summary = df_summary.rename(columns = {'filing_uuid': "number_of_reports", 'expenses': 'total_expense', 'income':'total_income', 'client.client_id':'number_of_clients', 'registrant.id': 'number_of_registrants'})
        return df_summary




class LobbyIssue():
    token = os.getenv('PRIVATE_API_KEY')
    def __init__(self, token, filing_year,issue_search,client_state):
        """
        Initialize a LobbyIssue API request call. 

        Parameters 
        ----------
        token : string.
            The token requested from Lobbying Disclosure Website. 
        filing_year : int. 
            Any year ranges from 1998 to 2022.
        issue_search : string.
            Issue keywords used to query reports. 
        client_state: string.
            The U.S. state location of lobbying clients or organizations. State name is in two letter abbreviation format.
        
        """
        self.ld_token = token
        self.year = filing_year
        self.issue_search = issue_search
        self.client_ppb_state = client_state

    def get_issue_file(self):
        """
        Retrieve a dataframe of lobbying activities around the issue search result. 

        Users can search keywords in the issue search field. Any relevant reports under the 
        advanced text search will show up. 
        Information includes the standard code assigned by Lobbying Disclosure 
        Authority in both short and long version, and specific description on the issues 
        written by registrants. The dataframe also includes government entity information, if any. 

        Returns
        -------
        pandas.DataFrame
            A pandas dataframe indicates lobbying activites around the issue keywords. 
            This includes both the direct issues and indirect issues in the whole report history.

        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> issue_api = lobby_lda.LobbyIssue(token, 2022, 'water quality', 'MA')
        >>> issue_api.get_issue_file()

        ====== =================== ============================= ================================ ================================================= ===================================================
        index  general_issue_code  general_issue_code_display    description                      lobbyists	                                        government_entities
        ====== =================== ============================= ================================ ================================================= ===================================================
        0      ENV                 Environment/Superfund         Water Quality policies           [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 2, 'name': 'HOUSE OF REPRESENTATIVES'}...
        1      SCI                 Science/Technology            Proposals related to S.1260      [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 2, 'name': 'HOUSE OF REPRESENTATIVES'}...
        2      HCR                 Health Issues                 American Rescue Plan implementa  [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 34, 'name': 'Health & Human Services, ...
        3      ENV                 Environment/Superfund         Water Quality policies.          [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 2, 'name': 'HOUSE OF REPRESENTATIVES'}...
        4      SCI                 Science/Technology            Proposals related to S.1260      [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 2, 'name': 'HOUSE OF REPRESENTATIVES'}...
        5      HCR                 Health Issues                 American Rescue Plan implementa  [{'lobbyist': {'id': 93728, 'prefix': None, 'p..  [{'id': 34, 'name': 'Health & Human Services, ...
        ====== =================== ============================= ================================ ================================================= ===================================================
        """

        session = requests.Session()
        session.params = {}
        session.params['api_key'] = self.ld_token
       
        params = {
                'filing_year': self.year,
                "client_ppb_state": self.client_ppb_state,
                'filing_specific_lobbying_issues': self.issue_search
                }

        r = session.get('https://lda.senate.gov/api/v1/filings/', params = params).json()
        results = r['results']

        # to obtain all results on all pages 
        while r['next']:
            r = requests.get(r['next']).json()
            results.extend(r['results'])

        # convert Json to pandas Dataframe
        df_file = pd.json_normalize(results,record_path='lobbying_activities') 
        return df_file

    def get_issue_description(self):
        """
        Retrieve standard issue codes on searched issue keywords.
        Users can obtain a list of standard code on issue topics around the keywords. This also include the issue code of other lobbying activities filed within the same reports. 

        Returns
        -------
        numpy.array
            An array providing description around the issue keywords in search. This includes the standard issue code of relevant reports. 

        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> issue_api = lobby_lda.LobbyIssue(token, 2022, 'water quality', 'MA')
        >>> issue_api.get_issue_description()
        ['Environment/Superfund','Science/Technology','Health Issues']

        """
        df_file = self.get_issue_file()
        # get unique issue code from the dataframe
        issue = df_file["general_issue_code_display"].unique()
        return print(issue)

    def get_issue_lobbyist(self):
        """
        Retrieve a dataframe of lobbyists working on relevant issues. 

        This function gets the comprehensive information on lobbyists, based on the issues he/she lobbied during the year. Lobbyist information includes covered_position, lobbyist.id, lobbyist.prefix, lobbyist.first_name, lobbyist.nickname, lobbyist.middle_name, lobbyist.last_name, and lobbyist.suffix.

        Returns
        -------
        pandas.DataFrame
            A pandas dataframe containing information on lobbyists, filtered by the issues, year, and client state location. 
        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> issue_api = lobby_lda.LobbyIssue(token, 2022, 'oil', 'MA')
        >>> issue_api.get_issue_lobbyist()

        ===== ================ =========== ======================== =================== ================= ===================== ================== ========================
        index covered_position lobbyist.id lobbyist.prefix_display  lobbyist.first_name lobbyist.nickname lobbyist.middle_name  lobbyist.last_name lobbyist.suffix_display
        ===== ================ =========== ======================== =================== ================= ===================== ================== ========================
        0     None             45118       None                     MICHAEL             None              None                  BRADLEY            None
        1     None             139718      MR.                      THOMAS              None              None                  CURRY              None
        2     None             139529      MRS.                     HAYLEY              None              None                  BOOK               None
        ===== ================ =========== ======================== =================== ================= ===================== ================== ========================
        """

        session = requests.Session()
        session.params = {}
        session.params['api_key'] = self.ld_token
       
        params = {
                'filing_year': self.year,
                "client_ppb_state": self.client_ppb_state,
                'filing_specific_lobbying_issues': self.issue_search
                }

        r = session.get('https://lda.senate.gov/api/v1/filings/', params = params).json()
        results = r['results']

        while r['next']:
            r = requests.get(r['next']).json()
            results.extend(r['results'])
        # get lobbyists information only
        df_lobbyists = pd.json_normalize(results, record_path=['lobbying_activities','lobbyists']) 
        df_lobbyists = df_lobbyists.drop(columns=['new','lobbyist.prefix','lobbyist.suffix' ]).drop_duplicates() #drop unused columns

        return df_lobbyists

    def get_lobbyists_count(self):
        """
        Get number of unique lobbyists working on a broad issue topics. 
        Users can filter the result count by client state location, report year, and issue keywords in text.

        Returns
        -------
        string.
            Output is an one sentence string including the number of lobbyists, and its relevant filtering conditions.

        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> issue_api = lobby_lda.LobbyIssue(token, 2021, 'health','NJ')
        >>> issue_api.get_lobbyists_count()
        "180 unique lobbyists are hired by NJ clients to work on health issues in 2021."
        """

        df_lobbyists = self.get_issue_lobbyist() #obtain lobbyist information dataframe
        lob_count = df_lobbyists['lobbyist.id'].nunique() # count unique number of lobbyists in condition
        # return output in a string sentense
        return print(f'{lob_count} unique lobbyists are hired by {self.client_ppb_state} clients to work on {self.issue_search} issues in {self.year}.')
    
    def get_lobbyists_name(self):
        """
        Get full name for lobbyists who work on a broad issue topics.
        Lobbyist names are filtered by client state location, report year, and issue keywords in text.

        Returns
        -------
        numpy.array
            Output is an array including the full name of lobbyists, based on relevant filtering conditions.

        Examples
        --------
        >>> from lobby_lda import lobby_lda
        >>> issue_api = lobby_lda.LobbyIssue(token, 2022, 'food','FL')
        >>> issue_api.get_lobbyists_name()
        ['JOHNIE BOATRIGHT' 'ROGER SZEMRAJ' 'PHILIP KARSTING' 'JENNIFER CERVANTES'
        'RYAN WESTON' 'VAN HIPP' 'ROBIN WALKER' 'JOHN PROVENZANO' 'TODD WEISS'
        'JOHN BREAUX' 'JASON GLEASON' 'WALLY BURNETT' 'SALIM ALAMEDDIN'
        'JOHN GREEN' 'MATHEW LAPINSKI' 'STEWART HALL' 'HUNTER MOORHEAD'
        'MARK WARREN' 'EDWARD ROYCE' 'SAMANTHA CARL-YODER' 'DANIEL JOSEPH'
        'CARMENCITA WHONDER' 'DOUGLAS MAGUIRE' 'RUSSELL SULLIVAN'
        'HAROLD HANCOCK' 'JAMES DAVENPORT' 'JOHN MONSIF' 'KYLE GILLEY'
        'STEVE DANON' 'JODI BOCK DAVIDSON' 'ALEX KRIGSTEIN' 'SARAH MATHIAS'
        'ADAM GOODMAN' 'HENRY MENN' 'BRENDA OTTERSON' 'HARRY GLENN'
        'STEVEN GIULI' 'JOSE DIAZ' 'BRIAN BALLARD' 'MARCKIA HAYES']
        """

        df_lobbyists = self.get_issue_lobbyist() # obtain all lobbyist dataframe under condition 
        # creat new columns of lobbyist's full name, concatenate first and last name 
        df_lobbyists['lobbyist.full_name'] = df_lobbyists['lobbyist.first_name'] + ' '+  df_lobbyists['lobbyist.last_name']
        # get full name of unique lobbyists
        lobbyist_name = df_lobbyists['lobbyist.full_name'].unique()
        return lobbyist_name
