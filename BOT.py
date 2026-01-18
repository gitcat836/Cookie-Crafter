import os
import discord
from discord import app_commands, Interaction, ButtonStyle, Embed
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import requests
import random
from io import BytesIO

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

if DISCORD_TOKEN is None:
    print("❌ Error: DISCORD_TOKEN not found in .env")
    exit(1)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# On Ready
# -------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# -------------------
# /generate command
# -------------------
@bot.tree.command(name="generate", description="Generate an image with Stability AI")
@app_commands.describe(prompt="Describe what image you want")
async def generate(interaction: Interaction, prompt: str):
    await interaction.response.defer()  # avoid timeout
    try:
        # Pollinations.ai URL construction
        seed = random.randint(1, 1000000)
        image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        
        response = requests.get(image_url)
        response.raise_for_status()
        
        image_bytes = BytesIO(response.content)
        file = discord.File(fp=image_bytes, filename="image.png")

        embed = Embed(title="🎨 Your Generated Image", color=discord.Color.teal())
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text=f"Prompt: {prompt} | via Pollinations.ai")

        await interaction.followup.send(embed=embed, file=file)
    except Exception as e:
        await interaction.followup.send(f"❌ Error generating image: {e}")

# -------------------
# /embed command
# -------------------
@bot.tree.command(name="embed", description="Send a custom embed")
@app_commands.describe(title="Embed title", description="Embed description", color="Hex color #RRGGBB", image_url="Optional image URL", plain_text="Text above embed")
async def embed_cmd(interaction: Interaction, title: str, description: str, color: str = "#2f3136", image_url: str = None, plain_text: str = ""):
    await interaction.response.defer()
    try:
        col = int(color.strip("#"), 16)
        embed = Embed(title=title, description=description, color=col)
        if image_url:
            embed.set_image(url=image_url)
        await interaction.followup.send(content=plain_text, embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

# -------------------
# /textbutton command
# -------------------
@bot.tree.command(name="textbutton", description="Send text with a clickable button")
@app_commands.describe(text="Button text", label="Button label", style="Style: primary, secondary, success, danger", url="Optional URL")
async def textbutton(interaction: Interaction, text: str, label: str, style: str = "primary", url: str = None):
    await interaction.response.defer()
    style_dict = {"primary": ButtonStyle.primary, "secondary": ButtonStyle.secondary, "success": ButtonStyle.success, "danger": ButtonStyle.danger}
    btn = Button(label=label, style=style_dict.get(style.lower(), ButtonStyle.primary), url=url)
    view = View()
    view.add_item(btn)
    await interaction.followup.send(content=text, view=view)

# -------------------
# /coinflip command
# -------------------
@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: Interaction):
    await interaction.response.send_message(random.choice(["Heads 🪙", "Tails 🪙"]))

# -------------------
# /rps command
# -------------------
@bot.tree.command(name="rps", description="Play rock paper scissors")
@app_commands.describe(choice="Choose rock, paper, or scissors")
async def rps(interaction: Interaction, choice: str):
    choice = choice.lower()
    options = ["rock", "paper", "scissors"]
    if choice not in options:
        await interaction.response.send_message("❌ Invalid choice! Choose rock, paper, or scissors.")
        return
    bot_choice = random.choice(options)
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "You lose! 😢"
    await interaction.response.send_message(f"Your choice: {choice}\nBot's choice: {bot_choice}\n{result}")

# -------------------
# /8ball command
# -------------------
@bot.tree.command(name="8ball", description="Ask the magic 8ball")
@app_commands.describe(question="Your question")
async def eight_ball(interaction: Interaction, question: str):
    responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
    await interaction.response.send_message(f"🎱 Question: {question}\nAnswer: {random.choice(responses)}")

# -------------------
# /roll command
# -------------------
@bot.tree.command(name="roll", description="Roll for a random sweet treat")
async def roll(interaction: Interaction):
    items = ["Chocolate", "Waffle", "Cookie", "Sugar", "Bubblegum"]
    await interaction.response.send_message(f"🎲 You rolled: {random.choice(items)}")

# Prefix version of coinflip, rps, 8ball, roll
@bot.command()
async def coinflip_prefix(ctx: commands.Context):
    await ctx.message.delete()
    await ctx.send(random.choice(["Heads 🪙", "Tails 🪙"]))

@bot.command()
async def rps_prefix(ctx: commands.Context, choice: str):
    await ctx.message.delete()
    choice = choice.lower()
    options = ["rock", "paper", "scissors"]
    if choice not in options:
        await ctx.send("❌ Invalid choice! Choose rock, paper, or scissors.")
        return
    bot_choice = random.choice(options)
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or (choice == "paper" and bot_choice == "rock") or (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "You lose! 😢"
    await ctx.send(f"Your choice: {choice}\nBot's choice: {bot_choice}\n{result}")

@bot.command()
async def eightball(ctx: commands.Context, *, question: str):
    await ctx.message.delete()
    responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not", "Ask again later"]
    await ctx.send(f"🎱 Question: {question}\nAnswer: {random.choice(responses)}")

@bot.command()
async def roll_prefix(ctx: commands.Context):
    await ctx.message.delete()
    items = ["Chocolate", "Waffle", "Cookie", "Sugar", "Bubblegum"]
    await ctx.send(f"🎲 You rolled: {random.choice(items)}")

# -------------------
# /announcement command
# -------------------
@bot.tree.command(name="announcement", description="Send a plain text announcement")
@app_commands.describe(message="The message to announce")
async def announcement(interaction: Interaction, message: str):
    await interaction.response.defer()
    await interaction.channel.send(message)
    await interaction.followup.send("✅ Announcement sent!", ephemeral=True)

@bot.command(name="announcement")
async def announcement_prefix(ctx: commands.Context, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

# -------------------
# Run bot
# -------------------
bot.run(DISCORD_TOKEN)