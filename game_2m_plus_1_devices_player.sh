# Description: This is a shell script to run the game on two different machines. 
# This is the client side.
# N and M are hyperparameters.
# IP is the IP address of the machine where the connectors are running, it is to be updated to the machine where it is run.

N=10
M=5
echo "Enter Your Player Number (0/1): "
read player
echo "Enter Your Soldier Number (1 to $M): "
read soldier
IP=172.17.74.181

python3 commander_foot_connector.py $N $M $player $soldier $IP
