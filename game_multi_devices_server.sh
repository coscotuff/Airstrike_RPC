# Description: This is a shell script to run the game on two different machines. 
# This is the server side.
# N and M are hyperparameters.

N=10
M=5
a=1

sleep .5
python3 player_connector.py $N $M 0 &
sleep .5
python3 player_connector.py $N $M 1 &