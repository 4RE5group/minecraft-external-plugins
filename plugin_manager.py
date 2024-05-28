import subprocess
import threading
import os
import re
import time

def last_word(string1, string2):
    string1=string1.replace(" "+string2, "")
    a = string1.split(" ")
    return a[len(a)-1]

def start_minecraft_server(jar_path):
    # Start the Minecraft server process
    process = subprocess.Popen(
        ['java', '-jar', jar_path, 'nogui'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    return process

def read_server_output(process):
    # Read the server output in a separate thread
    def read_output(stream):
        with stream:
            for line in iter(stream.readline, ''):
                print(line, end='')  # Print to console or handle as needed

    threading.Thread(target=read_output, args=(process.stdout,)).start()
    threading.Thread(target=read_output, args=(process.stderr,)).start()

def send_command_to_server(process, command):
    print("=> "+command)
    process.stdin.write(command + '\n')
    process.stdin.flush()

def processPlugin(process, file):
    # Match the pattern get{Entity.Property}
    while True:
        match = re.search(r'get\{([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\}', file)
        if match:
            entity = match.group(1)
            property = match.group(2)
            send_command_to_server(process, f"data get entity {entity} {property}")
            # print(f"data get entity {entity} {property}")
            result=""
            try:
                for line in iter(process.stdout.readline, ''):
                    result = line.strip().split("has the following entity data: ")[1].strip("'")
                    break
            except:
                print("Couldn't get ouput of get{"+entity+"."+property+"}")
            file = file.replace("get{"+entity+"."+property+"}", result)
            # print("Replaced '"+"get{"+entity+"."+property+"}"+"' with '"+result+"'")
        else:
            break
    return file

jar_path = './server.jar'  # Path to your Minecraft server jar file
prefix = "!"
server_process = start_minecraft_server(jar_path)

# init
os.system("mkdir -p plugins")
print("Minecraft external plugins loader")
print("       made by 4re5 group        ")
print("")
print("Plugins path: ./plugins/")
print(f"Jar path: {jar_path}")
print(f"Commands prefix: '{prefix}'")
print("")

try:
    stream=server_process.stdout
    with stream:
        for line in iter(stream.readline, ''):
            line = line.strip()
            playername=""
            if " <" in line and "> " in line:
                playername=line.split(" <")[1].split("> ")[0]
                print(f"Player {playername} has sent a message")
            if line.endswith(prefix+"version"):
                send_command_to_server(server_process, f"tellraw {playername} \"§6Minecraft external plugins, V1.0\"")
                send_command_to_server(server_process, f"tellraw {playername} \"§6https://github.com/4RE5group/minecraft-external-plugins\"")
            elif line.endswith("left the game"):
                playername=last_word(line, "left the game")
                print(f"player {playername} left the game")
            elif line.endswith("joined the game"):
                playername=last_word(line, "joined the game")
                print(f"player {playername} joined the game")
            for filename in os.listdir("plugins"):
                f = os.path.join("plugins", filename)
                if os.path.isfile(f):
                    if line.endswith(prefix+filename):
                        file = open(f).read()
                        file = file.replace("{player}", playername)
                        file = processPlugin(server_process, file)
                        # todo: add get{command} to get output
                        send_command_to_server(server_process, file)
                        print(f"command {prefix}{filename} has been executed")
except KeyboardInterrupt:
    print("Stopping server...")
    send_command_to_server(server_process, "stop")
    time.sleep(10)
    server_process.terminate()
    server_process.wait()
