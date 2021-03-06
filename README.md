Power Admin Medal of Honor plugin for Big Brother Bot (www.bigbrotherbot.net)
=============================================================================


Description
-----------

This plugin brings Medal of Honor specific features to Bigbrotherbot.


******
*NOTE: since B3 v1.10.1 beta this plugin has been included in the standard plugins set, thus all patches and updates will be performed in the official B3 repository.*
******

Commands
--------

!pb_sv_command <punkbuster command> - Execute a punkbuster command
!runnextround - Switch to next round, without ending current
!restartround - Restart current round
!kill <player> - Kill a player without scoring effects
!teams - Make the teams balanced
!teambalance <on/off> - Set teambalancer on/off
!changeteam [<player>] - change a player to the other team
!swap <playerA> <playerB> - swap teams for player A and B (if in different teams)
!scramble - schedule teams scramble at next round
!scramblemode <random|score> - how to scramble ? randomly, by scores
!autoscramble <off|round|map> - auto scramble at each round/map change
!match <on/off> - Set server match mode on/off
!spect <player> - Send a player to spectator mode
!reserveslot <player>
!unreserveslot <player>
!setnextmap <map name>

Changelog
---------

v0.3 - 2010/10/24 - make it compatible with v1.4.0
v0.2 - 2010/10/24 - beta release for testing and feedbacks
v0.4 - 2010/10/24 - Courgette (thanks to GrossKopf, foxinabox & Darkskys for tests and feedbacks)
  * fix misspelling
  * fix teambalancing mechanism
  * add 2 settings for the teambalancer in config file
  * fix !changeteam command crash
  * !pb_sv_command : when PB respond with an error, displays the PB response instead of "There was an error processing your command"
  * !runnextround : when MoH respond with an error message display that message instead of "There was an error processing your command"
  * !restartround : when MoH respond with an error message display that message instead of "There was an error processing your command"
v0.5 - 2010/10/24 - Courgette
  * minor fix
  * major fix to the admin.movePlayer MoH command. This affected all team balancing features
v0.6 - 2010/10/25 - Courgette
  * fix !runnextround
  * fix !restartround
  * matchmod will now restart round when count down is finished
0.7 - 2010/10/28 - Courgette
  * prevent autobalancing right after a player disconnected
  * attempt to be more fair in the choice of the player to move over to avoid the same
    player being switch consecutively
  * add command !swap to swap a player with another one
0.8 - 2010/10/25 - Courgette
  * when balancing, broadcast who get balanced
0.9 - 2010/11/01 - Courgette
  * add !scramble command to plan team scrambing on next round start
0.10 - 2010/11/04 - Courgette
  * add !scramblemode, !autoscramble
  * can scramble based on player scores
0.11 - 2010/11/04 - Courgette
  * fix auto scramble at map change
  * fix scrambling strategy 'by scores'
0.12 - 2010/11/06 - Courgette
  * fix !scramble which would scramble each following round (whatever !autoscramble)
  * fix !autoscramble map
0.13 - 2010/11/09 - Courgette
  * add maxlevel for the teambalancer
1.0 - 2010/11/14 - Courgette
  * add !spect command
  * add !reserveslot and !unreserveslot commands
  * add !setnextmap command  
1.1 - 2011/06/04 - Courgette
  * fix teambalancer which would swap the first instead of the last guy who changed teams
  
Installation
------------

 * copy poweradminmoh.py into b3/extplugins
 * add to the plugins section of your main b3 config file : 
      <plugin name="poweradminmoh" config="@b3/extplugins/conf/plugin_poweradminmoh.xml" />


Support
-------

Support is only provided on www.bigbrotherbot.net forums on the following topic :
http://www.bigbrotherbot.net/forums/plugins-by-courgette/poweradmin-moh/

