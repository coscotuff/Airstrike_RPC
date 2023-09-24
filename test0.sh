N=10
M=5

python3 player_connector.py $N $M 0 &
python3 player_connector.py $N $M 1 &
a=1
while [ "$a" -le "$M" ]    # this is loop1
do
    python3 commander_foot_connector.py $N $M 0 $a &
    python3 commander_foot_connector.py $N $M 1 $a &
   a=`expr $a + 1`
done