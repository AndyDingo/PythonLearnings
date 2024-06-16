import random
player_wins = 0
computer_wins = 0
winning_score = 3

print("Rock, Paper, Scissors, Lizard, Spock: The Python Game")
print("")
print("Remember to have fun!")

# player = input("Player, please make your move: ").lower()


# rand_num = random.randint(0, 5)

# Convert name to number using conditionals
def name_to_number(name):
    if name == "rock":
        return 0
    elif name == "paper":
        return 1
    elif name == "scissors":
        return 2
    elif name == "lizard":
        return 3
    elif name == "spock":
        return 4
    else:
        print("An error has occurred in NAME.")


# Convert number to a name using conditionals
def number_to_name(rand_num):
    if rand_num == 0:
        return "rock"
    elif rand_num == 1:
        return "paper"
    elif rand_num == 2:
        return "scissors"
    elif rand_num == 3:
        return "lizard"
    elif rand_num == 4:
        return "spock"
    else:
        print("An error has occurred in RAND_NUM.")


# Rest of the logic
def lets_play_rpsls(player_choice):
    # print a blank line to separate consecutive games
    print("\n")

    # print out the message for the player's choice
    print("Player chooses " + player_choice)

    # convert the player's choice to player_number using the function name_to_number()
    player_number = name_to_number(player_choice)

    # compute random guess for comp_number using random.randrange()
    comp_number = random.randrange(0, 5)

    # convert comp_number to comp_choice using the function number_to_name()
    comp_choice = number_to_name(comp_number)

    # print out the message for computer's choice
    print(f"Computer plays {comp_choice}")

    # compute difference of comp_number and player_number modulo five
    difference = (comp_number - player_number) % 5

    # use if/elif/else to determine winner, print winner message
    if difference == 1 or difference == 2:
        print("Computer wins!")
    elif difference == 4 or difference == 3:
        print("Player wins!")
    elif difference == 0:
        print("Player and computer tie!")


# lets_play_rpsls(player)

# Tests
lets_play_rpsls("rock")
lets_play_rpsls("paper")
lets_play_rpsls("scissors")
lets_play_rpsls("lizard")
lets_play_rpsls("spock")