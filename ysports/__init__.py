"""
YSports

A python module for reading fantasy sports data from the Yahoo Sports API.

Version 0.1 allows the user to do three-legged authentication in order to
query Yahoo Sports. Arbitrary queries can be made either via YQL or the 
REST API.
"""

__author__ = 'Anthony Castillo'
__version__ = '0.1.0'
__all__ = ['YAuth', 'YLeague']


import oauth2 as oauth
import urlparse, json
import logging, webbrowser, csv, os, time

from ysports.settings import *


class YLeague(object):

    def __init__(self, YAuth, league_key=DFT_LEAGUE_KEY):
        """
        Initialize an object to represent a Yahoo fantasy sports league.
        """
        self.yauth = YAuth
        self.league_key = league_key
        self.__get_league_info()


    def __get_league_info(self):
        """
        Load league info from Yahoo.
        """
        q = 'http://fantasysports.yahooapis.com/fantasy/v2/league/' + self.league_key
        r, c = self.yauth.request(q)

        if r['status'] == '200':
            c_json = json.loads(c)
            league_data = c_json['fantasy_content']['league'][0]
            self.name = league_data['name']
            self.num_teams = league_data['num_teams']
            self.current_week = league_data['current_week']
            self.league_id = league_data['league_id']
            self.url = league_data['url']
            self.start_date = league_data['start_date']
        else:
            raise IOError

    
    def scoreboard(self, week=None):
        """
        Return the league's latest scoreboard, or the scoreboard for a given week 
        if week is specified.
        """

        q = "select * from fantasysports.leagues.scoreboard where league_key='" + self.league_key + "'"
        if week:
            q = q +  " and week=" + str(week)

        return self.yauth.request_yql(q)


class YAuth(object):

    def __init__(self, auth_filepath=DFT_AUTH_FILE):
        """
        Initialize a Yahoo authorization object to store consumer and auth
        token information.
        """
        ## Load Authorization Info
        self.auth_filepath = auth_filepath
        try:
            self.auth_values = self.read_auth_file(self.auth_filepath)
        except:
            raise Exception ('Could not read auth file at: %s' % self.auth_filepath)
        else:
            self.consumer_key = self.auth_values['consumer_key']
            self.consumer_secret = self.auth_values['consumer_secret']
            self.token_key = self.auth_values['token_key']
            self.token_secret = self.auth_values['token_secret']
            self.auth_session_handle = self.auth_values['session_handle']
            self.consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
            self.auth_timestamp = time.time()

            ## Either reauthorize the stored token...
            if self.token_key and self.token_secret and self.auth_session_handle:
                self.atoken = oauth.Token(self.token_key, self.token_secret)
                self.access_client = oauth.Client(self.consumer, self.atoken)
                self.reauthorize()
    
            ## ...or request a new authorization token.
            else:
                if INTERACTIVE_AUTHORIZATION:
                    self.request_and_authorize()


    def request_and_authorize(self):
        """
        Request user to authorize application on Yahoo.
        """
        self.auth_url = self.get_auth_url()
        webbrowser.open(self.auth_url)
        auth_code = raw_input('Enter Yahoo Authorization Code: ')
        if not self.authorize(auth_code):
            print 'Authorization failed. Please get a new auth url and try again.'
            logging.warning('Authorization failed.')
    

    def get_auth_url(self):
        """
        Get authorization url from Yahoo.
        """
        self.request_client = oauth.Client(self.consumer)
        resp, content = self.request_client.request(REQUEST_TOKEN_URL, 
                                                      method='GET',
                                                      parameters={'oauth_callback':'oob'})
        if resp['status'] == '200':
            self.request_info = dict(urlparse.parse_qsl(content))
            self.request_key = self.request_info['oauth_token']
            self.request_secret = self.request_info['oauth_token_secret']
            logging.info('Requesting authorization at: %s' % self.request_info['xoauth_request_auth_url'])
            return self.request_info['xoauth_request_auth_url']
        else:
            logging.error('Could not retrieve authorization url.')
            raise Exception


    def authorize(self, auth_code):
        """
        Use the provided auth code to get an auth token from Yahoo.
        """
        ## Set up authorization client
        rtoken = oauth.Token(self.request_key, self.request_secret)
        rtoken.set_verifier(auth_code)
        auth_client = oauth.Client(self.consumer, rtoken)
        resp, content = auth_client.request(AUTH_TOKEN_URL)

        if resp['status'] == '200':
            self.auth_token_info = dict(urlparse.parse_qsl(content))
            self.auth_token_key = self.auth_token_info['oauth_token']
            self.auth_token_secret = self.auth_token_info['oauth_token_secret']
            self.auth_session_handle = self.auth_token_info['oauth_session_handle']
    
            ## Create access client
            self.atoken = oauth.Token(self.auth_token_key, self.auth_token_secret)
            self.access_client = oauth.Client(self.consumer, self.atoken)
            self.write_auth_file(self.auth_filepath)
            return True
        else:
            return False


    def reauthorize(self):
        """
        Reauthorize an existing auth token.
        """
        logging.info('Reauthorizing stored token....')
        r, c = self.access_client.request(AUTH_TOKEN_URL, parameters={'oauth_session_handle':self.auth_session_handle})

        if r['status'] == '200':
            self.auth_token_info = dict(urlparse.parse_qsl(c))
            self.auth_token_key = self.auth_token_info['oauth_token']
            self.auth_token_secret = self.auth_token_info['oauth_token_secret']
            self.atoken = oauth.Token(self.auth_token_key, self.auth_token_secret)
            self.access_client = oauth.Client(self.consumer, self.atoken)
            self.auth_timestamp = time.time()
            logging.info('Token reauthorized.')
        else:
            logging.error('Could not reauthorize token.')
            raise Exception ('Could not reauthorize token.')


    def read_auth_file(self, auth_filepath):
        """
        Read authorization info from the auth file.
        
        *** You should make up your own method for securely
            storing token and consumer information. ***
        
        """
        vals = {}
        try:
            with open(auth_filepath, 'rb') as f:
                f_iter = csv.DictReader(f)
                vals = f_iter.next()
                f.close()
        except:
            logging.error('Problem reading auth file: %s' % self.auth_filepath)
            raise IOError
    
        return vals


    def write_auth_file(self, auth_filepath):
        """
        Write authorization info to a file.
        
        *** You should make up your own method for securely
            storing token and consumer information. ***
        
        """
        fieldnames = ['consumer_secret', 'consumer_key', 'token_key', 'token_secret', 'session_handle']
        headers = dict((n,n) for n in fieldnames)
        d = {'consumer_secret':self.consumer_secret,
             'consumer_key':self.consumer_key,
             'token_key':self.auth_token_key,
             'token_secret':self.auth_token_secret,
             'session_handle':self.auth_session_handle}
        try:
            with open(auth_filepath, 'wb') as f:
                auth_writer = csv.DictWriter(f, fieldnames)
                auth_writer.writerow(headers)
                auth_writer.writerow(d)
                f.close()
        except:
            logging.warning('Problem writing auth file.')


    def __atoken_is_expired(self):
        """
        Check if the auth token has expired.
        """
        return (int(self.auth_timestamp) + TOKEN_EXPIRATION_TIME) < time.time()
        

    def request(self, query):
        """
        Send a REST request to Yahoo.
        """
        if self.__atoken_is_expired():
            self.reauthorize()

        return self.access_client.request(query, parameters={'format':'json'})


    def request_yql(self, query):
        """
        Send a YQL request to Yahoo.
        """
        if self.__atoken_is_expired():
            self.reauthorize()

        return self.access_client.request(YQL_ENDPOINT, parameters={'format':'json',
                                                                    'q':query,})
