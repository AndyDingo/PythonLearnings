print("Rock...")
print("Paper...")
print("Scissors...")

player1 = input("Player 1, make your move: ")
player2 = input("Player 2, make your move: ")

if player1 == player2:
    print("It's a tie!")
elif player1 == "rock":
    if player2 == "scissors":
        print("player wins!")
    elif player2 == "paper":
        print("player2 wins!")
elif player1 == "paper":
    if player2 == "rock":
        print("player wins!")
    elif player2 == "scissors":
        print("player2 wins!")
elif player1 == "scissors":
    if player2 == "paper":
        print("player wins!")
    elif player2 == "rock":
        print("player2 wins!")
else:
    print("Something went wrong :C ")
