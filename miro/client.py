"""
Work with Miro REST API 
"""
from typing import List

import requests
import json
import pprint

from miro.objects.base_miro_object import MiroObjectType
from miro.objects.board import Board
from miro.objects.widgets import Widget
from miro.utils import (get_json_or_raise_exception,
                        UnexpectedResponseException, create_widget_by_type)


class MiroApiClient:
    # constants

    # end-point paths differ between v1 and v2
    boards = 'boards'
    items = 'items'
    endp_names = { boards: { '1': 'boards', '2': 'boards'}, \
        items: { '1': 'widgets', '2': 'items'} }


    def __init__(self, base_url: str, auth_token: str, **kwargs):
        self.api_version = str(kwargs['api_version']) if 'api_version' in kwargs else '2'
        self.debug = kwargs['debug'] if 'debug' in kwargs else False
        self.limit = kwargs['limit'] if 'limit' in kwargs else 50
        self.base_url = base_url if not base_url else 'https://api.miro.com'
        self.auth_token = auth_token
        self.auth_header_as_dict = {
            'Authorization': f'Bearer {self.auth_token}'
        }
        self.log_msg('Created new Miro client', pprint.pformat(self))

    def log_msg(self, *args):
        """ Depending on the debug status - write a log message or do nothing """
        if self.debug:
            for x in args:
                print(x)
            print("\n")

    def endpoint_name(self, object_name):
        """ Return the part of the end-point URL, specific to a particular
        object - e.g. for "boards" it would be https://api.miro.com/v2/boards/

        This method is needed since there seem to changes in the naming
        between v1 and v2 - what used to be called "widgets" is now called
        "items". This way the actual code, producing API request can stay
        the same """
        if object_name in self.endp_names:
            # we know this end-point
            data = self.endp_names[object_name]
            if str(self.api_version) in data:
                # and we know it for the desired version
                return data[str(self.api_version)]
        raise NameError(f'Unknown end-point name for {object_name} v{self.api_version}')

    def request_with_tracing(self, method: str, url: str, **kwargs ):
        """ Send a REST API request and return its response with
        the possibility to trace it
        """
        self.log_msg(f"Sending {method} request to {url}\n")
        if "json" in kwargs:
            self.log_msg("\nJSON data: ", json.dumps(kwargs['json'], indent=4))
        
        response = requests.request( method, url, **kwargs)
        self.log_msg("received status code", response.status_code, \
            "\nResponse body: ", json.dumps(response.json(), indent=4))
        return response

    def get_all_widgets_by_board_id(self, board_id: str) -> List[Widget]:
        url = f'{self.base_url}/v{self.api_version}/' + \
            self.endpoint_name(self.boards) + f'/{board_id}/' + \
            self.endpoint_name(self.items) + f'?limit={self.limit}'
        #response = requests.get(url, headers=self.auth_header_as_dict)
        response = self.request_with_tracing('GET', url, \
            headers=self.auth_header_as_dict)
        self.log_msg(pprint.pformat(response))
    
        collection_json = get_json_or_raise_exception(response)
        try:
            widgets_json = collection_json['data']
            for w in widgets_json:
                self.log_msg(pprint.pformat(w))
            return [create_widget_by_type(w) for w in widgets_json]
        except Exception as e:
            raise UnexpectedResponseException(cause=e)

    def get_board_by_id(self, board_id: str) -> Board:
        url = f'{self.base_url}/v{self.api_version}/' + \
            self.endpoint_name(self.boards) + f'/{board_id}'
        response = self.request_with_tracing('GET', url, \
            headers=self.auth_header_as_dict)
        board_json = get_json_or_raise_exception(response)

        try:
            return Board(
                obj_id=board_json['id'],
                name=board_json['name'],
                description=board_json['description']
            )
        except Exception as e:
            raise UnexpectedResponseException(cause=e)

    def create_board(self, name: str, description: str) -> Board:
        headers = {
            'Content-Type': 'application/json'
        }
        headers.update(self.auth_header_as_dict)

        board_data = {
            'name': name,
            'description': description
        }

        url = f'{self.base_url}/v{self.api_version}/' + \
            self.endpoint_name(self.boards) + '/'
        response = requests.post(url, json=board_data, headers=headers)

        board_json = get_json_or_raise_exception(response)

        try:
            return Board(
                obj_id=board_json['id'],
                name=board_json['name'],
                description=board_json['description']
            )
        except Exception as e:
            raise UnexpectedResponseException(cause=e)

    def add_widget(self, board_id: str, new_widget: Widget) -> Widget:
        headers = {
            'Content-Type': 'application/json'
        }
        headers.update(self.auth_header_as_dict)

        widget_data = new_widget.attributes2miro()

        url = f'{self.base_url}/v{self.api_version}/' + \
            self.endpoint_name(self.boards) + f'/{board_id}'
        response = self.request_with_tracing("POST", url, json=widget_data, headers=headers)
        
        widget_json = get_json_or_raise_exception(response)
        self.log_msg(widget_json)
        try:
            return Widget(
                obj_id=widget_json['id']
            )
        except Exception as e:
            raise UnexpectedResponseException(cause=e)
