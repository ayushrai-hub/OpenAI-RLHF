import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, PropertyMock
import discord
from discord.ext import commands
from datetime import timedelta

# Import your bot file
from ideal import bot  # Assuming your bot code is in bot.py

class TestDiscordBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = bot
        
        # Create mock context
        self.ctx = Mock()
        self.ctx.send = AsyncMock()
        
        # Create mock channel
        self.ctx.channel = Mock()
        self.ctx.channel.edit = AsyncMock()
        self.ctx.channel.set_permissions = AsyncMock()
        
        # Create mock guild and role
        self.ctx.guild = Mock()
        self.ctx.guild.default_role = Mock()
        
        # Create mock member
        self.member = Mock(spec=discord.Member)
        self.member.mention = "@testuser"
        self.member.timeout = AsyncMock()
        self.member.kick = AsyncMock()
        self.member.ban = AsyncMock()

        # Mock response for HTTP exceptions
        self.mock_response = Mock()
        self.mock_response.status = 403
        self.forbidden_exception = discord.Forbidden(self.mock_response, "Missing Permissions")

    # Test Ping Command
    @patch('discord.ext.commands.Bot.latency', new_callable=PropertyMock)
    async def test_ping_command(self, mock_latency):
        mock_latency.return_value = 0.1
        await self.bot.get_command('ping').callback(self.ctx)
        self.ctx.send.assert_called_once()
        self.assertTrue("Pong!" in self.ctx.send.call_args[0][0])

    # Test Kick Command
    async def test_kick_command(self):
        # Test successful kick
        await self.bot.get_command('kick').callback(self.ctx, self.member, reason="test reason")
        self.member.kick.assert_called_once_with(reason="test reason")
        self.ctx.send.assert_called_once()

        # Test failed kick
        self.ctx.send.reset_mock()
        self.member.kick.side_effect = self.forbidden_exception
        await self.bot.get_command('kick').callback(self.ctx, self.member)
        self.ctx.send.assert_called_once_with('Failed to kick member.')

    # Test Ban Command
    async def test_ban_command(self):
        # Test successful ban
        await self.bot.get_command('ban').callback(self.ctx, self.member, reason="test reason")
        self.member.ban.assert_called_once_with(reason="test reason")
        self.ctx.send.assert_called_once()

        # Test failed ban
        self.ctx.send.reset_mock()
        self.member.ban.side_effect = self.forbidden_exception
        await self.bot.get_command('ban').callback(self.ctx, self.member)
        self.ctx.send.assert_called_once_with('Failed to ban member.')

    # Test Mute Command
    async def test_mute_command(self):
        # Test successful mute
        duration = 10
        await self.bot.get_command('mute').callback(self.ctx, self.member, duration)
        self.member.timeout.assert_called_once_with(timedelta(minutes=duration))
        self.ctx.send.assert_called_once()

        # Test failed mute
        self.ctx.send.reset_mock()
        self.member.timeout.side_effect = self.forbidden_exception
        await self.bot.get_command('mute').callback(self.ctx, self.member)
        self.ctx.send.assert_called_once_with('Failed to mute member.')

    # Test Lock Command
    async def test_lock_command(self):
        await self.bot.get_command('lock').callback(self.ctx)
        self.ctx.channel.set_permissions.assert_called_once_with(
            self.ctx.guild.default_role,
            send_messages=False
        )
        self.ctx.send.assert_called_once()

    # Test Unlock Command
    async def test_unlock_command(self):
        await self.bot.get_command('unlock').callback(self.ctx)
        self.ctx.channel.set_permissions.assert_called_once_with(
            self.ctx.guild.default_role,
            send_messages=True
        )
        self.ctx.send.assert_called_once()

    # Test Slowmode Command
    async def test_slowmode_command(self):
        # Test successful slowmode
        seconds = 30
        await self.bot.get_command('slowmode').callback(self.ctx, seconds)
        self.ctx.channel.edit.assert_called_once_with(slowmode_delay=seconds)
        self.ctx.send.assert_called_once()

        # Test failed slowmode
        self.ctx.send.reset_mock()
        self.ctx.channel.edit.side_effect = self.forbidden_exception
        await self.bot.get_command('slowmode').callback(self.ctx, seconds)
        self.ctx.send.assert_called_once_with('Failed to set slowmode.')

    # Test Error Handler
    async def test_on_command_error(self):
        # Test missing permissions
        error = commands.MissingPermissions(['test_permission'])
        await self.bot.on_command_error(self.ctx, error)
        self.ctx.send.assert_called_once_with("You don't have permission to use this command.")

        # Test member not found
        self.ctx.send.reset_mock()
        error = commands.MemberNotFound('test')
        await self.bot.on_command_error(self.ctx, error)
        self.ctx.send.assert_called_once_with("Member not found.")

        # Test generic error
        self.ctx.send.reset_mock()
        error = Exception('test error')
        await self.bot.on_command_error(self.ctx, error)
        self.ctx.send.assert_called_once_with("An error occurred: test error")

if __name__ == '__main__':
    unittest.main(verbosity=2)