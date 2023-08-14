import os
import sys

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient, CommentList, CommentCreate

import pprint
from odious_ado.settings import BaseConfig


class AdoClient:
    def __init__(self):

        settings = BaseConfig.get_settings()

        # Create a connection to the org
        self._credentials = BasicAuthentication('', settings.ADO_PAT)
        self._connection = Connection(base_url=settings.ADO_ORGANIZATION_URL, creds=self._credentials)

        # Get a client (the "core" client provides access to projects, teams, etc)
        self._core_client = self._connection.clients.get_core_client()
        self._work_item_client = WorkItemTrackingClient(
            base_url=f"{settings.ADO_ORGANIZATION_URL}",
            creds=self._credentials
        )

        # self._comments = CommentList(url="")

    @property
    def get_core_client(self):
        return self._core_client

    @property
    def get_work_item_client(self):
        return self._work_item_client

    # def get_comments(self):
    #     return self._comments

# def __get_aws_accounts():
#     client = boto3.client('organizations')
#
#     response = client.list_accounts()
#     aws_accounts: {str: str} = {}
#     for account in response.get('Accounts'):
#         if account.get('Status', 'suspended').lower() == 'active':
#             aws_accounts[account.get('Name')] = account.get('Id')
#
#     return aws_accounts

