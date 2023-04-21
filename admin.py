import discord
from discord.ext import commands
from discord.ext.commands import Context


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context, member: discord.Member, *, reason=None):
        await ctx.guild.ban(member, reason=reason)
        embed = discord.Embed(title="Success!", color=discord.Color.red())
        embed.add_field(name="Ban:", value=f'{member.mention} has been banned by {ctx.author.mention}.', inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: Context, *, userid):
        user = discord.Object(id=userid)
        await ctx.guild.unban(user)
        embed = discord.Embed(title="Success!", color=discord.Color.red())
        embed.add_field(name="Unban:", value=f'<@{userid}> has been unbanned by {ctx.author.mention}.', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: Context, member: discord.Member, *, reason=None):
        await ctx.guild.kick(member, reason=reason)
        embed = discord.Embed(title="Success!", color=discord.Color.red())
        embed.add_field(name="Kick:", value=f'{member.mention} has been kicked by {ctx.author.mention}.', inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx: Context, member: discord.Member, *, reason):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        if not role:
            role = await ctx.guild.create_role(name='Muted')
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, speak=False, send_messages=False)
        await member.add_roles(role)
        embed = discord.Embed(title="Success!", color=discord.Color.red())
        embed.add_field(name="Mute:", value=f'{member.mention} has been muted by {ctx.author.mention}.', inline=False)
        embed.add_field(name="Reason:", value=reason, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx: Context, *, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        await member.remove_roles(role, reason=None)
        embed = discord.Embed(title="Success!", color=discord.Color.green())
        embed.add_field(name="Unmute:", value=f'{member.mention} has been unmuted by {ctx.author.mention}.', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx: Context, num_messages: int):
        await ctx.channel.purge(limit=num_messages+1)
        embed = discord.Embed(title="Success!", color=discord.Color.green())
        embed.add_field(name="Delete:", value=f'{num_messages} messages was deleted.', inline=False)
        await ctx.send(embed=embed)
