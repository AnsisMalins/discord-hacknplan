import argparse
import discord
import re
import requests

parser = argparse.ArgumentParser()
parser.add_argument("--discord-token", required=True, help="The bot token from your Discord developer dashboard")
parser.add_argument("--hacknplan-api-key", required=True, help="The Hacknplan API key from your account settings")
parser.add_argument("--hacknplan-project-id", required=True, help="The ID of the Hacknplan project you're in")
args = parser.parse_args()

client = discord.Client(fetch_offline_members=False, max_messages=None, guild_subscriptions=False)

@client.event
async def on_ready():
    print("Logged in as " + str(client.user))

@client.event
async def on_message(message):
    if message.type != discord.MessageType.default or message.author.bot or message.author.system:
        return

    match = re.search(r"(?:^|\s)#(\d+)(?:$|\s)", message.content)
    if match == None:
        return
    workItemId = match[1]

    response = requests.get("https://api.hacknplan.com/v0/projects/" + args.hacknplan_project_id
            + "/workitems/" + workItemId, headers = { "Authorization": "ApiKey " + args.hacknplan_api_key })
    if response.status_code != 200:
        print("Could not get work item " + workItemId + " because " + response.reason)
        return
    workItem = response.json();

    await message.channel.send(embed=discord.Embed(
        title=workItem["title"],
        url="https://app.hacknplan.com/p/" + str(workItem["projectId"])
            + "/kanban?categoryId=" + str(workItem["category"]["categoryId"])
            + "&boardId=" + str(workItem["board"]["boardId"])
            + "&taskId=" + str(workItem["workItemId"])))

client.run(args.discord_token)