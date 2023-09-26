# Description: This is a shell script to run the game on two different machines. N and M are hyperparameters.
# IP is the IP address of the machine where the connectors are running.

N=10
M=5
a=1
IP=172.17.74.74

sleep .5
python3 player_connector.py $N $M 0 &
sleep .5
python3 player_connector.py $N $M 1 &
sleep .5
while [ "$a" -le "$M" ]    # this is loop1
do
    python3 commander_foot_connector.py $N $M 0 $a $IP &
    python3 commander_foot_connector.py $N $M 1 $a $IP &
   a=`expr $a + 1`
done