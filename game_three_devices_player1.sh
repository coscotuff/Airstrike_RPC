# Description: This is a shell script to run the game on two different machines. 
# This is the client side.
# N and M are hyperparameters.
# IP is the IP address of the machine where the connectors are running, it is to be updated to the machine where it is run.

N=10
M=5
a=1
IP=172.17.74.181

while [ "$a" -le "$M" ]    # this is loop1
do
    python3 commander_foot_connector.py $N $M 1 $a $IP &
   a=`expr $a + 1`
done