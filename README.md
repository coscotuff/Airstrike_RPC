# Airstrike_RPC
Airstrike_RPC is a Python-based project that leverages gRPC, RPC calls, and protocol buffers for efficient communication.

This repository contains the codebase for a streamlined and high-performance remote procedure call system designed for a game that is a part of the assignment from the Semester-I '23-24 offering of the CS G623 Advanced (Distributed) Operating Systems course.

## Requirements

- Python 3.x
- gRPC (Google Remote Procedure Call): gRPC tools and gRPC Python Library
- TKinter package (sudo apt-get install python3-tk)
- Protobuf  ‘protoc’  compiler (for .proto files)
- Threading Python Library
- Random Python Library
- OS Python Library
- Socket Python Library
- Logging Python Library
- Time Python Library
- Socket Python Library
- Protobuf Python Library

Please ensure that you have these dependencies installed before running the script.

## Running Instructions
_Note:_
_1) The operating systems of the machines on which the files are to be run must be Linux-based._
_2) Ensure that all the required software and libraries are installed on your system. For more information on which libraries and software are needed, kindly go through technical design documentation._

First, raise the privilege of the corresponding shell script file that is to be run using chmod +x filename

1) If you wish to run the single device version of the game, where the server and players (both teams) are on a single device, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_single_device.sh
./game_single_device.sh
```

2) If you wish to run the two-device version of the game where the server is on one machine and the players (both teams) are on another machine, then:
   - Find out the IP address (ipv4) of the machine running the server using a command like ```ip a```. Set the shell script variable ```IP``` in the soldier .sh file to be that IP address.
   - On the machine that is running the server, change your present working directory to that where this file exists and run:
```
sudo chmod +x game_multi_devices_server.sh
./game_multi_devices_server.sh
```
  - On the machine that is running the players, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_two_devices_soldier.sh
./game_two_devices_soldier.sh
```

3) If you wish to run the three device version of the game, where the server is on one machine and the players of each team are on their own respective machines, then:
   - Find out the ip address (ipv4) of the machine running the server using a command like ```ip a```. Set the shell script variable ```IP``` in the player .sh files to be that IP address.
   - On the machine that is running the server, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_multi_devices_server.sh
./game_multi_devices_server.sh
```
  - On the machine that is running player 0, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_three_devices_player0.sh
./game_three_devices_player0.sh
```
  - On the machine that is running player 0, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_three_devices_player1.sh
./game_three_devices_player1.sh
```
4) If you wish to run the 2M + 1 device version of the game, where the server is on one machine, and each node participating in the game is on its own device, then:
   - Find out the ip address (ipv4) of the machine running the server using a command like ```ip a```. Set the shell script variable ```IP``` in the player .sh files to be that IP address.
   - On the machine that is running the server, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_multi_devices_server.sh
./game_multi_devices_server.sh
```
  - On the machine that is running a player, change your present working directory to that of where this file exists and run:
```
sudo chmod +x game_2m_plus_1_devices_player.sh
./game_three_devices_player0.sh
```
  When prompted, the user will need to enter their player and soldier numbers as well. Care needs to be taken that the correct player and soldier numbers are entered, else there will be overwriting and the game will not start. 

_Note: In the case that the user makes an error in running the scripts, they will need to explicitly kill those processes and start anew. They can use commands like ```kill -9 $(pgrep python3 | awk '$1>=INSERT-LOW-PID')```_
