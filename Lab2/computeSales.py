import sys #sys.exit to quit application


def main():
    menu()


# function that processes all data from new file
def new_file():
    print("New file func")


# Function that prints statistics for a specific product
def product_stat():
    print("Product stat")


# Function that prints statistics for a specific AFM
def afm_stat():
    print("AFM stat")


# Choose the right function given user input
def menu_choice(choice):
    if choice == "1":
        new_file()
    elif choice == "2":
        product_stat()
    elif choice == "3":
        afm_stat()
    elif choice == "4":
        # Exit choice
        sys.exit(9)
    else:
        print("Invalid menu choice")
    # ????? Prints menu repeatedly
    menu()


# Our main menu
def menu():
    print()
    print(
        '''Give your preference:
        1: Read new input file
        2: Print statistics for a specific product
        3: Print statistics for a specific AFM
        4: Exit the program
        '''
    )

    choice = input()
    menu_choice(choice)


# program execution starts here
main()
