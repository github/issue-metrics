# -*- coding: utf-8 -*-
import json
import os
from pprint import pprint
import click
from dotenv import load_dotenv
from tabulate import tabulate
from azure.devops.v7_1.work_item_tracking import CommentCreate

from odious_ado.settings import BaseConfig
from odious_ado.plugins.ado import AdoClient


@click.group(name="ado")
@click.pass_context
def ado(ctx):
    ctx.ensure_object(dict)
    # cluster = session.create({})
    # engine = session.factory.create({})
    config = BaseConfig()
    ctx.obj["client"] = AdoClient()

    pass


@ado.command()
@click.pass_context
def info(ctx) -> None:
    """
    Get ADO client info.
    """
    # results = session.info()
    #
    # if results is None:
    #     click.secho("Unable to connect to database.")
    # else:
    #     click.secho(tabulate(results, headers="keys", tablefmt="psql"))


@ado.group("projects")
@click.pass_context
def projects(ctx):
    pass


@projects.command("ls")
@click.pass_context
def list_projects(ctx):
    client = ctx.obj.get("client")

    if client is None:
        click.secho("Unable to get ado client.")
    else:
        # click.secho(tabulate(results, headers="keys", tablefmt="psql"))=
        get_projects_response = client.get_core_client.get_projects()
        index = 0

        while get_projects_response is not None:
            for project in get_projects_response:
                pprint("[" + str(index) + "] " + project.name)
                index += 1

            if isinstance(get_projects_response, list):
                get_projects_response = None
            # else:
            #     if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
            #         # Get the next page of projects
            #         get_projects_response = client.get_core_client.get_projects(
            #             continuation_token=get_projects_response.continuation_token)
            #     else:
            #         # All projects have been retrieved
            #

        for i in client.get_work_item_client.get_recent_activity_data():
            print(i.id)
            pprint(i.title)
            pprint(i.team_project)
            pprint(i.identity_id)

            c = client.get_work_item_client.get_comments(i.team_project, i.id)

            # new_msg = CommentCreate("test for the hackathon!")
            #
            # blrg = client.get_work_item_client.add_comment(new_msg, i.team_project, i.id)

            # pprint(blrg.as_dict())

            pprint(c.as_dict())

            # pprint.pprint(dir(i))
        #
        #     pprint.pprint(i.as_dict())

            # pprint.pprint(dir(client.get_comments()))
            # pprint.pprint(client.get_comments().as_dict())
