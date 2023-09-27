# Description: This is a shell script to run the game on the same machine. N and m are hyperparameters.

N=5
M=2
a=1

sleep .5
python3 player_connector.py $N $M 0 &
sleep .5
python3 player_connector.py $N $M 1 &
sleep .5
while [ "$a" -le "$M" ]    # this is loop1
do
    python3 commander_foot_connector.py $N $M 0 $a &
    python3 commander_foot_connector.py $N $M 1 $a &
   a=`expr $a + 1`
done