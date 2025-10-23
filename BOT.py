import os
import random
import discord
from discord import app_commands, Interaction, ButtonStyle, Embed
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import requests
from io import BytesIO
import base64
from keepalive import keep_alive  # Keepalive server

# ------------------- Load Environment -------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

if not DISCORD_TOKEN or not STABILITY_API_KEY:
    print("❌ Missing DISCORD_TOKEN or STABILITY_API_KEY in environment.")
    exit(1)

# ------------------- Bot Setup -------------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- On Ready -------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# ------------------- /generate -------------------
@bot.tree.command(name="generate", description="Generate an image with Stability AI")
@app_commands.describe(prompt="Describe what image you want")
async def generate(interaction: Interaction, prompt: str):
    await interaction.response.defer()
    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {"Authorization": f"Bearer {STABILITY_API_KEY}"}
    data = {"prompt": prompt, "output_format": "png"}

    try:
        response = requests.post(url, headers=headers, files={"none": ""}, data=data)
        response.raise_for_status()
        image_bytes = response.content
        file = discord.File(fp=BytesIO(image_bytes), filename="image.png")

        embed = Embed(title="🎨 Your Generated Image", color=discord.Color.purple())
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text=f"Prompt: {prompt}")

        await interaction.followup.send(embed=embed, file=file)
    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f"❌ Error generating image: {e}")

# ------------------- /embed -------------------
@bot.tree.command(name="embed", description="Send a custom embed")
@app_commands.describe(
    title="Embed title",
    description="Embed description",
    color="Hex color #RRGGBB",
    image_url="Optional image URL",
    plain_text="Text above embed"
)
async def embed_command(interaction: Interaction, title: str, description: str, color: str = "#5865F2", image_url: str = None, plain_text: str = None):
    try:
        color_value = int(color.replace("#", ""), 16)
    except ValueError:
        color_value = 0x5865F2

    embed = Embed(title=title, description=description, color=color_value)
    if image_url:
        embed.set_image(url=image_url)
    await interaction.response.send_message(content=plain_text or "", embed=embed)

# ------------------- /textbutton -------------------
@bot.tree.command(name="textbutton", description="Send a message with a custom button")
@app_commands.describe(text="Message text", label="Button label", url="Button URL", color="Button color (red, green, grey, blue)")
async def textbutton(interaction: Interaction, text: str, label: str, url: str, color: str = "grey"):
    color_map = {
        "red": ButtonStyle.danger,
        "green": ButtonStyle.success,
        "grey": ButtonStyle.secondary,
        "blue": ButtonStyle.primary
    }
    button = Button(label=label, style=color_map.get(color.lower(), ButtonStyle.secondary), url=url)
    view = View()
    view.add_item(button)
    await interaction.response.send_message(text, view=view)

# ------------------- /coinflip -------------------
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: Interaction):
    await interaction.response.send_message(f"🪙 {random.choice(['Heads', 'Tails'])}")

# ------------------- /rps -------------------
@bot.tree.command(name="rps", description="Play rock paper scissors")
@app_commands.describe(choice="Choose rock, paper, or scissors")
async def rps(interaction: Interaction, choice: str):
    options = ["rock", "paper", "scissors"]
    user_choice = choice.lower()
    bot_choice = random.choice(options)
    if user_choice not in options:
        await interaction.response.send_message("❌ Choose rock, paper, or scissors!")
        return
    if user_choice == bot_choice:
        result = "It's a tie!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "I win! 😢"
    await interaction.response.send_message(f"You chose **{user_choice}**, I chose **{bot_choice}**. {result}")

# ------------------- /8ball -------------------
@bot.tree.command(name="8ball", description="Ask the magic 8ball a question")
@app_commands.describe(question="Your question")
async def eight_ball(interaction: Interaction, question: str):
    responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
    await interaction.response.send_message(f"🎱 {random.choice(responses)}")

# ------------------- /roll -------------------
@bot.tree.command(name="roll", description="Roll for a random flavor")
async def roll(interaction: Interaction):
    result = random.choice(["Chocolate 🍫", "Waffle 🧇", "Cookie 🍪", "Sugar 🍬", "Bubblegum 🍭"])
    await interaction.response.send_message(f"You rolled: **{result}**!")

# ------------------- /announcement -------------------
@bot.tree.command(name="announcement", description="Send an announcement")
@app_commands.describe(message="The announcement text")
async def announcement(interaction: Interaction, message: str):
    await interaction.response.send_message(f"📢 **Announcement:** {message}")

# ------------------- Prefix versions -------------------
@bot.command()
async def coinflip_prefix(ctx):
    await ctx.message.delete()
    await ctx.send(f"🪙 {random.choice(['Heads', 'Tails'])}")

@bot.command()
async def rps_prefix(ctx, choice: str):
    await ctx.message.delete()
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    choice = choice.lower()
    if choice not in options:
        await ctx.send("❌ Choose rock, paper, or scissors!")
        return
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "I win! 😢"
    await ctx.send(f"You chose **{choice}**, I chose **{bot_choice}**. {result}")

@bot.command()
async def eightball_prefix(ctx, *, question: str):
    await ctx.message.delete()
    responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
    await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command()
async def roll_prefix(ctx):
    await ctx.message.delete()
    result = random.choice(["Chocolate 🍫", "Waffle 🧇", "Cookie 🍪", "Sugar 🍬", "Bubblegum 🍭"])
    await ctx.send(f"You rolled: **{result}**!")

@bot.command()
async def announcement_prefix(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(f"📢 **Announcement:** {message}")

# ------------------- Keep Alive and Run -------------------
keep_alive()
bot.run(DISCORD_TOKEN)