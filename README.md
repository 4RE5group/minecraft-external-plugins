# minecraft external plugins
New kind of plugins in minecraft vanilla.
Basically it's just a layer on top of regular vanilla server.

You can edit prefix in `plugin_manager.py` and add/import more commands why drag and drop your files into your server root and ./plugins/ folder


## plugin development
plugins are commands that can be put in ./plugins directory
to create a new plugin, just create a new file called "myCommand" in ./plugins/
then write for example `tellraw {player} "get{{player}.Pos}"`, will tell to {player} (which will be replaced by senders's username) this x,y,z positions as nbt tag
