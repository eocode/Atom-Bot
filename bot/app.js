[
    {
        "trigger": "Conecta bocinas",
        "command": "bluetoothctl disconnect D4:91:0F:FD:2C:60 && bluetoothctl connect D4:91:0F:FD:2C:60",
        "offCommand": "bluetoothctl disconnect D4:91:0F:FD:2C:60",
        "ground": "foreground",
        "voice": "bocinas",
        "voiceReply": "Bocinas conectadas",
        "allowParams": "true"
    },      
    {
     "trigger": "Actualizar Bot",
     "command": "cd /home/pi/Desktop/Ada-Bot && git pull",
     "offCommand": "",
     "ground": "foreground",
     "voice": "actualizar",
     "voiceReply": "Ada se ha actualizado correctamente",
     "allowParams": "false"
    },
]