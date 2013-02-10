
# YSports (v 0.1)

## About
YSports is a python library for reading fantasy sports data from the Yahoo Sports API.

Version 0.1 allows the user to do three-legged authentication in order to
query Yahoo Sports. Arbitrary queries can be made either via YQL or the 
REST API.

The YLeague class has been set up as the first instance of a class representing
league data at a higher level of abstraction.

### To Do
- unit tests
- better error handling
- dynamically insert query parameters
- secure token storage
- flesh out YLeague
- more classes for representing different data sets (e.g. Player, Roster, etc.)

### Contributions
Bug fixes, features, patches, code improvements, etc. are always welcome.


## Installation
Download from github. 

### Dependencies
- httplib2

`
    >>> pip install httplib2
`

- [zbowling's fork of python oauth2](https://github.com/zbowling/python-oauth2) (See [discussion on StackOverflow](http://stackoverflow.com/questions/4026759/problems-with-python-oauth2-and-yahoos-fantasy-sports-api/4468269#4468269) for why this fork.)


## Usage

### Setup
Enter your consumer key and consumer secret into the appropriate fields in the authorization csv file:

    ./ysports/cache/tokensecrets.csv

**Note: determine your own method for securely storing your authorization tokens. The method used in this library is not secure.**


### Sample Usage
#### The YLeague Object

Create an Auth object, then create a League object:

    >>> import ysports
    >>> Y = ysports.YAuth()
    Enter Yahoo Authorization code: xxxxxx
    >>> L = ysports.YLeague(Y, "<your_league_key>")
    >>> L.name
    Your League Name


#### Arbitrary REST Query

    >>> q1 = 'http://fantasysports.yahooapis.com/fantasy/v2/player/223.p.5479'
    >>> response, content = Y.request(q1)
    >>> print content
    [... fantasy info for Drew Brees, JSON format ...]

    
#### Arbitrary YQL Query
    >>> q2 = 'select * from fantasysports.leagues.scoreboard where league_key="<your_league_key>"'
    >>> response, content = Y.request_yql(q2)
    >>> print content
    [... your league's info, JSON format ...]

