import os
from os import getenv
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
import random
import openai
from classes import MemeGenerator, MentionsNotifier, Hangman
import requests
import qrcode
import discord
from music import Music
from admin import Admin


load_dotenv("discord.env")
TOKEN = getenv("DISCORD_TOKEN")

# OPEN_AI
OPENAI_API_KEY = getenv("API_KEY")
openai.api_key = OPENAI_API_KEY

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    case_insensitive=True,
    intents=intents
)


@bot.event
async def on_ready():
    print(f'{bot.user} is ready to use!')
    await bot.add_cog(Music(bot))
    await bot.add_cog(Admin(bot))
    await bot.change_presence(activity=discord.Game("Gigachad Simulator"))


@bot.command()
async def userinfo(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.author
    elif member is not None:
        member = member
    info_embed = discord. Embed(title=f"{member.name}`s User Information", description="All information about this user.", color=member.color)
    info_embed.set_thumbnail(url=member.avatar)
    info_embed.add_field(name="Name:", value=member.name, inline=False)
    info_embed.add_field(name="Nick Name:", value=member.display_name, inline=False)
    info_embed.add_field(name="Discriminator:", value=member.discriminator, inline=False)
    info_embed.add_field(name="ID: ", value=member.id, inline=False)
    info_embed.add_field(name="Top Role: ", value=member.top_role, inline=False)
    info_embed.add_field(name="Status:", value=member.status, inline=False)
    info_embed.add_field(name="Bot User?", value=member.bot, inline=False)
    info_embed.add_field(name="Creation Date:", value=member.created_at.date(), inline=False)

    await ctx.send(embed=info_embed)


@bot.command(name="setprefix", aliases=["prefix"])
async def setprefix(ctx: Context, *, newprefix: str):
    bot.command_prefix = newprefix
    await ctx.send(f"Prefix changed to '{newprefix}'")
# Memes
meme_generator = MemeGenerator()


@bot.command(name="list_memes")
async def list_memes(ctx: Context) -> None:
    meme_list = meme_generator.list_memes()
    await ctx.send(f"**Memes**```\n{meme_list}```")


@bot.command(name="make_meme")
async def make_meme(
    ctx: Context, template_id: int, top_text: str, bottom_text: str
) -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    await ctx.channel.send(meme_url)

# Mentions
mentions_notifier = MentionsNotifier()


@bot.command(name="subscribe")
async def subscribe(ctx: Context, email: str) -> None:
    mentions_notifier.subscribe(ctx.author.id, email)


@bot.command(name="unsubscribe")
async def unsubscribe(ctx: Context) -> None:
    mentions_notifier.unsubscribe(ctx.author.id)


@bot.event
async def on_message(message: Message):

    """
    If any user in subscribers is mentioned,
    check if their value is set to True.
    If is, it'll send the email to that person.
    """
    email_msg = "Someone mentioned you in channel " + message.channel.jump_url
    for user in mentions_notifier.subscribers:
        if f"@{user}" in message.content:
            if mentions_notifier.subscribers[user] is True:
                mentions_notifier.notify_about_mention(user, email_msg)
    await bot.process_commands(message)


# Hangman

@bot.command(name="play_hangman")
async def play_hangman(ctx: Context) -> None:
    # In this command are all variables, that you need for the game.
    with open('words.txt') as file:
        words = file.read().split("\n")

    """
    bot.ANY_VARIABLE makes the variable
    applicable in any bot command (function).
    """
    bot.letters: list = []
    random_word: str = random.choice(words)
    bot.random_word: str = "" + random_word
    bot.secret_word: str = ""
    bot.list_random_word: list = []
    bot.list_secret_word: list = []
    for letter in random_word:
        bot.list_random_word.append(letter)
        bot.list_secret_word.append("-")

    for sign in bot.list_secret_word:
        bot.secret_word += sign + " "

    # Player discord account without user's code
    bot.player: str = str(ctx.author).split("#")[0]
    bot.player_id: int = ctx.author.id
    bot.guesses: str = ""
    bot.lives: int = 7
    bot.wrong_or_right: str = ""
    bot.hangman = Hangman(
        player=bot.player,
        guesses=bot.guesses,
        lives=bot.lives,
        secret_word=bot.secret_word,
        wrong_or_right=bot.wrong_or_right)

    # First message, that will be immediately edited
    embed = discord.Embed(title="Starting Hangman...", color=discord.Color.dark_gold())
    msg = await ctx.channel.send(embed=embed)
    hangman_msg = bot.hangman.call_hangman()
    # Editting the first message
    embed = discord.Embed(title="Hangman", color=discord.Color.dark_gold())
    embed.add_field(name="", value=hangman_msg, inline=False)
    bot.msg = await msg.edit(embed=embed)


@bot.command(name="guess")
async def guess(ctx: Context, letter: str) -> None:
    await ctx.message.delete()
    if ctx.author.id != bot.player_id:
        return

    """
    If player has 0 lives or already won the game,
    he can't guess anymore and has to start a new game.
    """
    if (bot.lives == 0) or ("-" not in bot.list_secret_word):
        await ctx.send("You have to start a new game first.")
        return

    # Making the input lowercase to avoid some problems
    letter = letter.lower()

    """
    If letter is not in alphabet or input is more than 1 symbol,
    set variable bot.wrong_or_right to "Enter only 1 letter at a time."
    (That's what your bot did.)

    Also if player has already guessed that input letter,
    bot will send "You already guessed that."
    and don't subtract lives and also
    do not put that letter in letters.
    """
    if (not letter.isalpha()) or (len(letter) > 1):
        bot.wrong_or_right = "Enter only 1 letter at a time."

    elif letter not in bot.letters:
        bot.letters.append(letter)

        if letter in bot.random_word:
            for index in range(0, len(bot.random_word)):
                if letter == bot.list_random_word[index]:
                    bot.list_secret_word[index] = letter.capitalize()
            bot.wrong_or_right = "Correct Guess"

        else:
            bot.wrong_or_right = "Wrong Guess"
            bot.lives -= 1

        bot.guesses += letter.capitalize() + " "
        bot.secret_word = ""
        for sign in bot.list_secret_word:
            bot.secret_word += sign + " "
    else:
        bot.wrong_or_right = "You already guessed that."

    """
    If player has 0 lives, he loses the game and
    will no longer be able to play in that game.
    (he has to start a new one)

    Else if the player guesses all the letters, he will win the game.
    And also will not be able to play the game anymore.
    (he also has to start a new game)
    """

    if bot.lives == 0:
        bot.wrong_or_right = f"You lost, the word was: {bot.random_word}"
    elif "-" not in bot.list_secret_word:
        bot.wrong_or_right = "You won!"

    # Call the function with new values.
    bot.hangman = Hangman(
        player=bot.player,
        guesses=bot.guesses,
        lives=bot.lives,
        secret_word=bot.secret_word,
        wrong_or_right=bot.wrong_or_right)

    embed = discord.Embed(title="Hangman", color=discord.Color.dark_gold())
    embed.add_field(name="", value=bot.hangman.call_hangman(), inline=False)
    await bot.starting_msg.edit(embed=embed)


# OPEN AI

@bot.command(name="imagine")
async def image(ctx: Context, *prompt: str) -> None:
    """Dall-E image"""
    prompt = " ".join(word for word in prompt)
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
    except openai.error.InvalidRequestError:
        await ctx.send(f"{ctx.author.mention} Your prompt may contain text that is not allowed by our safety system.")
    image_url = response['data'][0]['url']
    print(prompt)
    await ctx.send(image_url)


@bot.command(name="chat")
async def chat(ctx: Context, *prompt: str) -> None:
    """ChatGPT chat"""
    openai.organization = "org-owMimhd2VJEuA3M4mM2N4R8X"
    prompt = " ".join(word for word in prompt)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    if "```" in completion.choices[0]['message']['content']:
        await ctx.send(f"{completion.choices[0]['message']['content']}")
    else:
        await ctx.send(f"```{completion.choices[0]['message']['content']}```")


@bot.command(name="rps")
async def rps(ctx: Context, player_choice: str) -> None:
    """Rock, paper, scissors!"""
    choices = ("rock", "paper", "scissors")
    if player_choice not in choices:
        await ctx.send(f"{ctx.author.mention} invalid choice, you can choose only rock, paper or scissors")
    else:
        bot_choice = random.choice(choices)
        if player_choice == bot_choice:
            await ctx.send(f"I chose {bot_choice}\n**It's a tie!**")
        elif (player_choice == "rock" and bot_choice == "scissors") or \
             (player_choice == "paper" and bot_choice == "rock") or \
             (player_choice == "scissors" and bot_choice == "paper"):
            await ctx.send(f"I chose {bot_choice}\n**You won!**")
        else:
            await ctx.send(f"I chose {bot_choice}\n**I won!**")


@bot.command(name="deepai")
async def deepai(ctx: Context, *prompt: str) -> None:
    DEEP_AI_KEY = getenv("DEEP_AI_KEY")
    prompt = " ".join(word for word in prompt)
    r = requests.post(
     "https://api.deepai.org/api/text2img",
     data={
        'text': prompt,
     },
     headers={'api-key': DEEP_AI_KEY}
    )
    url = r.json()["output_url"]
    await ctx.send(url)


@bot.command(name="qr")
async def qr(ctx: Context, *url: str) -> None:
    url = " ".join(word for word in url)
    img = qrcode.make(url)
    img.save("qr.png")
    with open("qr.png", "rb") as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
    os.remove("qr.png")


@bot.command(name="weather")
async def weather(ctx: Context, city: str):
    WEATHER_KEY = getenv("WEATHER_KEY")
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}").json()
    print(response["weather"])
    print(response["weather"][0]["description"])
    await ctx.send(f'In {city} it is **{round((int(response["main"]["temp"])-273.15), 2)}°C** and **{response["weather"][0]["description"]}**')


@bot.command(name="timezone")
async def timezone(ctx: Context, continent: str, city: str):
    response = requests.get(f"http://worldtimeapi.org/api/timezone/{continent}/{city}").json()
    await ctx.send(f"In {city} it's **{response['datetime'].split()[0][11:16]}**")


bot.run(TOKEN)
