#
# PowerAdmin Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2008 Mark Weirath (xlr8or@xlr8or.com)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# CHANGELOG
#
# 0.2 - 2010/10/24 - Courgette 
#    * beta release for testing and feedbacks
# 0.3 - 2010/10/24 - Courgette
#    * make it compatible with v1.4.0 
#
__version__ = '0.3'
__author__  = 'Courgette'

import string
import b3
import b3.events
import b3.plugin
try:
    # B3 v1.4.0+
    from b3.parsers.frostbite.connection import FrostbiteCommandFailedError
except ImportError:
    # B3 v1.4.0
    from b3.parsers.frostbite.bfbc2Connection import Bfbc2CommandFailedError as FrostbiteCommandFailedError

#--------------------------------------------------------------------------------------------------
class PoweradminmohPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    
    _enableTeamBalancer = None
    _ignoreBalancingTill = 0
    
    _matchmode = False
    _match_plugin_disable = []
    _matchManager = None
    
    
    def startup(self):
        """\
        Initialize plugin settings
        """
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return False
        self._registerCommands()
    
        # do not balance on the 1st minute after bot start
        self._ignoreBalancingTill = self.console.time() + 60
        
        # Register our events
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        

    def onLoadConfig(self):
        self.LoadTeamBalancer()
        self.LoadMatchMode()
    

    def LoadTeamBalancer(self):
        try:
            self._enableTeamBalancer = self.config.getboolean('teambalancer', 'enabled')
        except:
            self._enableTeamBalancer = False
            self.debug('Using default value (%s) for Teambalancer enabled', self._enableTeamBalancer)


    def LoadMatchMode(self):
        # MATCH MODE SETUP
        self._match_plugin_disable = []
        try:
            self.debug('match_plugins_disable/plugin : %s' %self.config.get('match_plugins_disable/plugin'))
            for e in self.config.get('match_plugins_disable/plugin'):
                self.debug('match_plugins_disable/plugin : %s' %e.text)
                self._match_plugin_disable.append(e.text)
        except:
            self.debug('Can\'t setup match disable plugins because there is no plugins set in config')


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func
        return None
    
    
    def _registerCommands(self):
        # register our commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp
                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
    

    ##########################################################################

    def onEvent(self, event):
        """\
        Handle intercepted events
        """
        if event.type == b3.events.EVT_CLIENT_TEAM_CHANGE:
            self.onTeamChange(event.data, event.client)
        elif event.type == b3.events.EVT_GAME_ROUND_START:
            # do not balance on the 1st minute after bot start
            self._ignoreBalancingTill = self.console.time() + 60
        elif event.type == b3.events.EVT_CLIENT_AUTH:
            self.onClientAuth(event.data, event.client)


    def onClientAuth(self, data, client):
        #store the time of teamjoin for autobalancing purposes 
        client.setvar(self, 'teamtime', self.console.time())


    def onTeamChange(self, data, client):
        #store the time of teamjoin for autobalancing purposes 
        client.setvar(self, 'teamtime', self.console.time())
        self.verbose('Client variable teamtime set to: %s' % client.var(self, 'teamtime').value)
        
        if self._enableTeamBalancer:
            if self.console.time() < self._ignoreBalancingTill:
                return
            
            if client.team in (b3.TEAM_SPEC, b3.TEAM_UNKNOWN):
                return
            
            # get teams
            team1players, team2players = self.getTeams()
            
            # if teams are uneven by one or even, then stop here
            if abs(len(team1players) - len(team2players)) <= 1:
                return
            
            biggestteam = team1players
            if len(team2players) > len(team1players):
                biggestteam = team2players
            
            # has the current player gone contributed to making teams uneven ?
            if client.cid in biggestteam:
                self.debug('%s has contributed to unbalance the teams')
                client.message('do not make teams unbalanced')
                if client.teamId == 1:
                    newteam = '2'
                else:
                    newteam = '1' 
                try:
                    self.console.write(('admin.movePlayer', client.cid, newteam, 0, 'true'))
                except FrostbiteCommandFailedError, err:
                    self.warning('Error, server replied %s' % err)
                
                
    
    ###########################################################################
    
    def cmd_pb_sv_command(self, data, client, cmd=None):
        """\
        <punkbuster command> - Execute a punkbuster command
        """
        if not data:
            client.message('missing paramter, try !help pb_sv_command')
        else:
            self.debug('Executing punkbuster command = [%s]', data)
            try:
                response = self.console.write(('punkBuster.pb_sv_command', '%s' % data))
            except FrostbiteCommandFailedError, err:
                self.error(err)
                client.message('Error: %s' % err.response)


    def cmd_runnextround(self, data, client, cmd=None):
        """\
        Switch to next round, without ending current
        """
        self.console.say('forcing next round')
        time.sleep(1)
        self.console.write(('admin.runNextRound',))
        
    def cmd_restartround(self, data, client, cmd=None):
        """\
        Restart current round
        """
        self.console.say('Restart current round')
        time.sleep(1)
        self.console.write(('admin.restartRound',))

    def cmd_kill(self, data, client, cmd=None):
        """\
        <player> Kill a player without scoring effects
        """
        # this will split the player name and the message
        input = self._adminPlugin.parseUserCmd(data)
        if input:
            sclient = self._adminPlugin.findClientPrompt(input[0], client)
            if not sclient:
                # a player matchin the name was not found, a list of closest matches will be displayed
                # we can exit here and the user will retry with a more specific player
                return False
            else:
                try:
                    self.console.write(('admin.killPlayer', sclient.cid))
                except FrostbiteCommandFailedError, err:
                    client.message('Error: %s' % err.response)


    def cmd_changeteam(self, data, client, cmd=None):
        """\
        [<name>] - change a player to the other team
        """
        input = self.parseUserCmd(data)
        if not input:
            client.message('Invalid data, try !help changeteam')
        else:
            # input[0] is the player id
            sclient = self._adminPlugin.findClientPrompt(input[0], client)
            if sclient:
                if sclient.teamId == 1:
                    newteam = '2'
                else:
                    newteam = '1' 
                try:
                    self.console.write(('admin.movePlayer', sclient.cid, newteam, 0, 'true'))
                    cmd.sayLoudOrPM(client, '%s forced to the other team' % sclient.cid)
                except Bfbc2CommandFailedError, err:
                    client.message('Error, server replied %s' % err)

    ##########################################################################

    def cmd_teams(self ,data , client, cmd=None):
        """\
        Make the teams balanced
        """
        if client:
            team1players, team2players = self.getTeams()
            self.debug('team1players: %s' % team1players)
            self.debug('team2players: %s' % team2players)
            # if teams are uneven by one or even, then stop here
            gap = abs(len(team1players) - len(team2players))
            if gap <= 1:
                client.message('Teams are balanced, %s vs %s (diff: %s)' %(len(team1players), len(team2players), gap))
            else:
                self.teambalance()

    def cmd_teambalance(self, data, client=None, cmd=None):
        """\
        <on/off> - Set teambalancer on/off
        Setting teambalancer on will warn players that make teams unbalanced
        """
        if not data:
            if client:
                if self._enableTeamBalancer:
                    client.message("team balancing is on")
                else:
                    client.message("team balancing is off")
            else:
                self.debug('No data sent to cmd_teambalance')
        else:
            if data.lower() in ('on', 'off'):
                if data.lower() == 'off':
                    self._enableTeamBalancer = False
                    client.message('Teambalancer is now disabled')
                elif data.lower() == 'on':
                    self._enableTeamBalancer = True
                    client.message('Teambalancer is now enabled')
            else:
                if client:
                    client.message("Invalid data, expecting 'on' or 'off'")
                else:
                    self.debug('Invalid data sent to cmd_teambalance : %s' % data)
                    
        
    def cmd_match(self, data, client, cmd=None): 
        """\
        <on/off> - Set server match mode on/off
        """
        if not data or str(data).lower() not in ('on','off'):
            client.message('Invalid or missing data, expecting "on" or "off"')
            return False
        else:
            if data.lower() == 'on':
                
                self._matchmode = True
                self._enableTeamBalancer = False
                
                for e in self._match_plugin_disable:
                    self.debug('Disabling plugin %s' %e)
                    plugin = self.console.getPlugin(e)
                    if plugin:
                        plugin.disable()
                        client.message('plugin %s disabled' % e)
                
                self.console.say('match mode: ON')
                if self._matchManager:
                    self._matchManager.stop()
                self._matchManager = MatchManager(self)
                self._matchManager.initMatch()

            elif data.lower() == 'off':
                self._matchmode = False
                if self._matchManager:
                    self._matchManager.stop()
                self._matchManager = None
                
                # enable plugins
                for e in self._match_plugin_disable:
                    self.debug('enabling plugin %s' %e)
                    plugin = self.console.getPlugin(e)
                    if plugin:
                        plugin.enable()
                        client.message('plugin %s enabled' % e)

                self.console.say('match mode: OFF')

    #########################################################################
    def getTeams(self):
        """Return two lists containing the names of players from both teams"""
        team1players = []
        team2players = []
        for name, clientdata in self.console.getPlayerList().iteritems():
            if str(clientdata['teamId']) == '1':
                team1players.append(name)
            elif str(clientdata['teamId']) == '2':
                team1players.append(name)
        return team1players, team2players

                
    def teambalance(self):
        if self._enableTeamBalancer:
            # get teams
            team1players, team2players = self.getTeams()
            
            # if teams are uneven by one or even, then stop here
            gap = abs(len(team1players) - len(team2players))
            if gap <= 1:
                self.verbose('Teambalance: Teams are balanced, T1: %s, T2: %s (diff: %s)' %(len(team1players), len(team2players), gap))
                return
            
            howManyMustSwitch = int(gap / 2)
            bigTeam = 1
            smallTeam = 2
            if len(team2players) > len(team1players):
                bigTeam = 2
                smallTeam = 1
                
            self.verbose('Teambalance: Teams are NOT balanced, T1: %s, T2: %s (diff: %s)' %(len(team1players), len(team2players), gap))
            self.console.saybig('Autobalancing Teams!')

            ## we need to change team for howManyMustSwitch players from bigteam
            playerTeamTimes = {}
            clients = self.console.clients.getList()
            for c in clients:
                if c.teamId == bigTeam:
                    teamTimeVar = c.isvar(self, 'teamtime')
                    if not teamTimeVar:
                        self.debug('client has no variable teamtime')
                        c.setvar(self, 'teamtime', self.console.time())
                        self.verbose('Client variable teamtime set to: %s' % c.var(self, 'teamtime').value)
                    playerTeamTimes[c.cid] = teamTimeVar.value
            
            self.debug('playerTeamTimes: %s' % playerTeamTimes)
            sortedPlayersTeamTimes = sorted(playerTeamTimes.iteritems(), key=lambda (k,v):(v,k))
            self.debug('sortedPlayersTeamTimes: %s' % sortedPlayersTeamTimes)

            for c, teamtime in sortedPlayersTeamTimes[:howManyMustSwitch]:
                try:
                    self.debug('forcing %s to the other team' % c.cid)
                    self.console.write(('admin.movePlayer', c.cid, smallTeam, 0, 'true'))
                except FrostbiteCommandFailedError, err:
                    self.error(err)
                

################################################################################## 
import threading
class MatchManager:
    plugin = None
    _adminPlugin = None
    console = None
    playersReady = {}
    countDown = 10
    running = True
    timer = None
    countdownStarted = None
    
    def __init__(self, plugin):
        self.plugin = plugin
        self.console = plugin.console
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            raise Exception('Could not find admin plugin')
    
    def stop(self):
        try: self.timer.cancel()
        except: pass
        self.running = False
        self.unregisterCommandReady()
        
    def initMatch(self):
        for c in self.console.clients.getList():
            c.setvar(self.plugin, 'ready', False)
        self.countdownStarted = False
        self.registerCommandReady()
        self.console.say('MATCH starting soon !!')
        self.console.say('ALL PLAYERS : type !ready when you are ready')
        self.timer = threading.Timer(10.0, self._checkIfEveryoneIsReady)
        self.timer.start()
    
    def registerCommandReady(self):
        self._adminPlugin.registerCommand(self.plugin, 'ready', 0, self.cmd_ready)
    
    def unregisterCommandReady(self):
        # unregister the !ready command
        try:
            cmd = self._adminPlugin._commands['ready']
            if cmd.plugin == self.plugin:
                self.plugin.debug('unregister !ready command')
                del self._adminPlugin._commands['ready']
        except KeyError:
            pass
    
    def sayToClient(self, message, client):
        """We need this to bypass the message queue managed by the frostbite parser"""
        self.console.write(('admin.say', message, 'player', client.cid))

    def _checkIfEveryoneIsReady(self):
        self.console.debug('checking if all players are ready')
        isAllPlayersReady = True
        waitingForPlayers = []
        for c in self.console.clients.getList():
            isReady = c.var(self.plugin, 'ready', False).value
            self.plugin.debug('is %s ready ? %s' % (c.cid, isReady))
            if isReady is False:
                waitingForPlayers.append(c)
                self.sayToClient('we are waiting for you. type !ready', c)
                isAllPlayersReady = False
    
        if len(waitingForPlayers) > 0 and len(waitingForPlayers) <= 6:
            self.console.say('waiting for %s' % ', '.join([c.cid for c in waitingForPlayers]))
        
        try: self.timer.cancel()
        except: pass
        
        if isAllPlayersReady is True:
            self.console.say('All players are ready, starting count down')
            self.countDown = 10
            self.countdownStarted = True
            self.timer = threading.Timer(0.9, self._countDown)
        else:
            self.timer = threading.Timer(10.0, self._checkIfEveryoneIsReady)
            
        if self.running:
            self.timer.start()

    def _countDown(self):
        self.plugin.debug('countdown: %s' % self.countDown)
        if self.countDown > 0:
            self.console.write(('admin.say', 'MATCH STARTING IN %s' % self.countDown, 'all'))
            self.countDown -= 1
            if self.running:
                self.timer = threading.Timer(1.0, self._countDown)
                self.timer.start()
        else:    
            # make sure to have a brief big text
            self.console.write(('admin.say', 'FIGHT !!!', 'all'))
            self.console.say('Match started. GL & HF')
            self.console.write(('admin.restartMap',))
            self.stop()

    def cmd_ready(self, data, client, cmd=None): 
        """\
        Notify other teams you are ready to start the match
        """
        self.plugin.debug('MatchManager::ready(%s)' % client.cid)
        if self.countdownStarted:
            client.message('Count down already started. You cannot change your ready state')
        else:
            wasReady = client.var(self.plugin, 'ready', False).value
            if wasReady:
                client.setvar(self.plugin, 'ready', False)
                self.sayToClient('You are not ready anymore', client)
                client.message('You are not ready anymore')
            else:
                client.setvar(self.plugin, 'ready', True)
                self.sayToClient('You are now ready', client)
                client.message('You are now ready')
            self._checkIfEveryoneIsReady()



if __name__ == '__main__':
    ############# setup test environment ##################
    import time
    from b3.fake import fakeConsole, joe, superadmin
    
    fakeConsole.gameName = 'moh'
    def frostbitewrite(msg, maxRetries=1, needConfirmation=False):
        """send text to the console"""
        if type(msg) == str:
            # console abuse to broadcast text
            self.say(msg)
        elif type(msg) == tuple:
            print "   >>> %s" % repr(msg)
    fakeConsole.write = frostbitewrite
    
    from b3.config import XmlConfigParser
    conf = XmlConfigParser()
    conf.loadFromString("""
    <configuration plugin="poweradminmoh">
      <settings name="commands">
        <set name="pb_sv_command-pb">100</set>
        
        <set name="runnextround-nextrnd">40</set>
        <set name="restartround-restartrnd">40</set>
        <set name="kill">40</set>
        
        <set name="team">20</set>
        <set name="teambalance">20</set>
        <set name="changeteam">20</set>
        
        <set name="match">20</set>
      </settings>
      
      <settings name="teambalancer">
        <set name="enabled">no</set>
      </settings>
      
      
      <match_plugins_disable>
        <plugin>spree</plugin>
        <plugin>adv</plugin>
        <plugin>tk</plugin>
        <plugin>pingwatch</plugin>
      </match_plugins_disable>
    </configuration>
    """)  
    
    p = PoweradminmohPlugin(fakeConsole, conf)
    p.onStartup()
    
    ########################## ok lets test ###########################
    
    def test_pb():        
        superadmin.says('!pb PB_PList')
        time.sleep(5)
        
    def test_straighforward_commands():
        superadmin.says('!nextrnd')
        time.sleep(1)
        superadmin.says('!restartrnd')
        time.sleep(5)
        
    def test_kill():
        superadmin.says('!kill nobody')
        superadmin.says('!kill jo')
        time.sleep(5)
        
    def test_matchmode():
        superadmin.says('!match')
        superadmin.says('!match off')
        time.sleep(2)
        superadmin.says('!match on')
        time.sleep(2)
        joe.says('!ready')
        time.sleep(20)
        superadmin.says('!ready')
        time.sleep(120)
        
    joe.connects('Joe')
    superadmin.connects('superadmin')
    test_matchmode()