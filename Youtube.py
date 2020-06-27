from traceback import print_exc
import json
import pickle
import os.path
from os import remove

import googleapiclient
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google_auth_httplib2 as httplib2 

class Youtube:
    scopes = ['https://www.googleapis.com/auth/youtube']
    default_path = 'secrets.json'
    @classmethod
    def __init__(cls, secret):
        try:
            if not os.path.exists('token.pickle'):
                cls.token = cls.__generateCreds(credentials=secret)
            else:
                cls = cls.from_token(token='token.pickle')
        except Exception:
            print_exc()
            cls.token = cls.__generateCreds(credentials=cls.default_path)
    @classmethod
    def from_token(cls, token=None):
        try:
            if token == None:
                cls.token = cls.__generateCreds(credentials=cls.default_path)

                cls = cls.from_token(token='token.pickle')
            else:
                if isinstance(token, str) and token.endswith('.pickle'):
                    with open(token, 'rb') as f:
                        cls.token = pickle.load(f)
                    return cls
                else:
                    raise TypeError('Error: token must be a path to a pickle file containing the token credentials')
        except Exception:
            print_exc()
            return None
    @classmethod
    def __generateCreds(cls, credentials):
        creds = None
        try:
            if isinstance(credentials, str) and credentials.endswith('.json'):
                flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes=cls.scopes)
                creds = flow.run_local_server(port=8200)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            else:
                raise TypeError('Error: secret must be a path to a json file containing the secrets')
        except Exception:
            print_exc()
        finally:
            return creds
    @classmethod
    def setDefaultPath(cls, path):
        cls.default_path = path
    @classmethod
    def getDefaultPath(cls):
        return cls.default_path
    @classmethod
    def setScopes(cls, scopes):
        cls.scopes = scopes
        remove('token.pickle')
        cls.token = cls.__generateCreds('secrets.json')
    @classmethod
    def getScopes(cls):
        return cls.scopes
    @classmethod
    def getSubscriptions(cls, channel='mine', opt=None):
        response = None
        try:
            if not isinstance(channel, str):
                raise TypeError('Error: channel must be of type str')
            http = googleapiclient.http.build_http()
            if channel == 'mine':
                channel_id = True
            else:
                channel_id = channel

            if opt == None:
                options = {
                    'part': 'contentDetails',
                }
                if isinstance(channel_id, bool):
                    options['mine'] = True
                else:
                    options['channelId'] = channel_id
            else:
                if not isinstance(opt, dict):
                    raise TypeError('Error: opt must be a dict')
                params = (
                    'part',
                    'id',
                    'channelId',
                    'mine',
                    'myRecentSubscribers',
                    'mySubscribers',
                    'forChannelId',
                    'maxResults',
                    (
                        'id',
                        'channelId',
                        'mine',
                        'myRecentSubscribers',
                        'mySubscribers'
                    )
                )
                if cls.__check_params(params, opt):
                    options = opt
                else:
                    raise TypeError('Error: Invalid opt argument')

            if options.get('mine'):
                response = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/subscriptions?part={options["part"]}&mine={options["mine"]}', 'GET')
            else:
                response = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/subscriptions?part={options["part"]}&channelId={options["channelId"]}', 'GET')
            
            body = json.loads(response[1].decode('utf-8'))
            response = body

        except Exception:
            print_exc()
        finally:
            return response 
    @classmethod
    def __check_params(cls, params, options, count=1):
        try:
            i = 0
            if not isinstance(params, tuple) or not isinstance(options, dict) or not isinstance(count, int):
                raise TypeError('Error: params must be a tuple\n\t keys must be a dict\n\t count must be an int')

            if isinstance(params[ len(params) - 1 ], tuple):
                keywords = params[ len(params) - 1 ]
            
            for key in options.keys():
                if not key in params:
                    raise KeyError('Error: invalid key found')

                if key in keywords:
                    i += 1
                else:
                    continue

                if i > count:
                    raise KeyError('Error: keyword found more than spec value')
            
            return True
        except Exception:
            print_exc()
            return False
    @classmethod
    def getPLaylist(cls, playlist='mine', opt=None):
        response = None
        try:
            if not isinstance(playlist, str):
                raise TypeError('Error: channel must be of type str')
            http = googleapiclient.http.build_http()
            if playlist == 'mine':
                playlist_id = True
            else:
                playlist_id = playlist
            
            if opt == None:
                options = {
                    'part': 'contentDetails,snippet',
                }
                if isinstance(playlist_id, bool):
                    options['mine'] = True
                else:
                    options['id'] = playlist_id
            else:
                if not isinstance(opt, dict):
                    raise TypeError('Error: opt must be a dict')
                params = (
                        'part',
                        'id',
                        'channelId',
                        'mine',
                        (
                            'id',
                            'channelId',
                            'mine'
                        )
                )
                if cls.__check_params(params, opt):
                    options = opt
                else:
                    raise TypeError('Error: Invalid opt argument')

            if options.get('mine'):
                response = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/playlists?part={options["part"]}&mine={options["mine"]}', 'GET')
            else:
                response = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/playlists?part={options["part"]}&id={options["id"]}', 'GET')

            body = json.loads(response[1].decode('utf-8'))
            response = body

        except Exception:
            print_exc()
        finally:
            return response
    @classmethod
    def getVideo(cls, id, opt=None):
        response = None
        try:
            if not isinstance(id, str):
                raise TypeError('Error: id must be a string')
            http = googleapiclient.http.build_http()

            if opt == None:
                options = {
                    'part': 'contentDetails, snippet, statistics, status',
                    'id': id
                }
            else:
                if not isinstance(opt, dict):
                    raise TypeError('Error: opt must be a dict')
                params = (
                    'part',
                    'chart',
                    'id',
                    'myRating',
                    'h1',
                    'maxHeight',
                    'maxResults',
                    'maxWidth',
                    (
                        'chart',
                        'id',
                        'myRating'
                    )
                )
                if cls.__check_params(params, opt):
                    options = opt
                else:
                    raise TypeError('Error: Invalid opt argument')
            
            response = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/videos?part={options["part"]}&id={options["id"]}', 'GET')
            body = json.loads(response[1].decode('utf-8'))
            response = body

        except Exception:
            print_exc()
        finally:
            return response
    @classmethod
    def likeVideo(cls, id):
        request = None
        try:
            if not isinstance(id, str):
                raise TypeError('Error: id must be a string')
            http = googleapiclient.http.build_http()

            request = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/videos/rate?id={id}&rating=like', 'POST')
            status = request[0]['status']
            if status == '204':
                return True
            else:
                return False
        except Exception:
            print_exc() 
    @classmethod
    def removeLike(cls, id):
        request = None
        try:
            if not isinstance(id, str):
                raise TypeError('Error: id must be a string')
            http = googleapiclient.http.build_http()

            request = httplib2.AuthorizedHttp(cls.token, http).request(f'https://www.googleapis.com/youtube/v3/videos/rate?id={id}&rating=none', 'POST')
            status = request[0]['status']
            if status == '204':
                return True
            else:
                return False
        except Exception:
            print_exc()