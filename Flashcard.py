import csv, os, shutil,time, heapq
import random
from datetime import datetime as dt

class PriorityQueue:
    def __init__(self):
        self.heap = []

    def isEmpty(self):
        return len(self.heap) == 0

    def enqueue(self,priority, data):
        heapq.heappush(self.heap,(priority,data))

    def dequeue(self):
        if self.heap:
            return heapq.heappop(self.heap)[1]

class Deck:
    def __init__(self,path):
        """
        A basic deck class where the user can make decks, select a deck to use, study the selected deck, edit the selected deck,
        export selected deck, and import other decks

        Parameters:
        path (str): A string representing the directory where the decks are stored

        Returns:
        None
        """
        self.path = path
        self.deck = None
        self.deckName = None
        self.study_deck = DeckSchedule()

    def makeDeck(self):
        """
        Generates a deck based on the users inputs as a csv file

        Parameters:
        None

        Returns:
        None
        """
        deck = []
        deck.append(["question", "answer", "date_created", "deck"])  # appends header
        existingDecks = os.listdir(self.path)
        while True:
            deckName = input("Name of the deck:\n")

            if any(char in deckName for char in invalidChars):  # if any invalid characters are in the name
                print(f"The name can not contain:")
                print(*invalidChars, sep=",")
                print("\n")

            elif deckName == "":
                print("The deck must have a name!")

            elif deckName + '.csv' in existingDecks:  # checks for duplicates
                print("Duplicate deck name try another name!")

            else:
                break

        self.makeCard(deck)
        while True:
            print(deck)
            choice = input("Do you want to add more cards?\n1): Yes:\n2): No:\n")
            if choice.lower() == "2":
                break
            elif choice.lower() == "1":
                self.makeCard(deck)
            else:
                print("Invalid Input! Please enter '1' for Yes or '2' for No.")

        with open(self.path + "\\" + deckName + ".csv", "w", newline='') as f:
            w = csv.writer(f)
            w.writerows(deck)

    def makeCard(self,deck):
        """
        Generates a card based oon the users inputs, adds it to the  deck

        Paramaters:
        deck (arr): array of all cards to store as a csv

        Returns:
        None
        """
        card = []
        question = str(input("Question for the card:\n"))
        answer = str(input("Answer for the card:\n"))
        now = str(dt.now().date()) + " " + str(dt.now().time())[:-7]  # gets current date and time
        card.append(question)
        card.append(answer)
        card.append(now)
        deck.append(card)

    def extractDeck(self):
        """
        Extracts all information from the selected deck

        Parameters:
        None:

        Returns:
        deck: (arr): An array where the data from a csv is stored
        """
        deck = []  # used an array because need to sort and search from the data structure
        with open(self.path + self.deckName, "r") as text:
            csv = text.readlines()
            for n, line in enumerate(csv, 0):
                # print(line)
                line = line.replace("\n", "")
                # print(line)
                line = line.split(",")
                card = Card(line[0], line[1], line[2], n)
                deck.append(card)
                self.study_deck.addCard(card)
        self.deck = deck
        return self.deck

    def selectDeck(self):
        """
        Returns a string of the decks name that the user chose, if valid

        Parameters:
        None

        Returns:
        str: A string of the deck name the user chose
        """
        existingDecks = os.listdir(self.path)
        if len(existingDecks) == 0:
            print("There are no decks to select!\nYou can make decks at the main menu")
            return

        else:
            while True:
                print("Select a deck:")
                for idx, d in enumerate(existingDecks, 1):
                    print(f"{idx}): {d[:-4]}")
                deck = input("")
                if deck.isnumeric() and 1 <= int(deck) <= len(existingDecks):
                    selectedDeck = existingDecks[int(deck) - 1]
                    self.deckName = selectedDeck
                    return self.deckName
                else:
                    print("\nEnter a existing deck!")

    def importDeck(self):
        """
        Allows user to import a deck, if valid

        Parameters:
        None

        Returns:
        None
        """
        deckImport = input("Enter the path to the deck you want to import:\n")
        try:
            if not os.path.exists(deckImport):
                print("Error: File not found")
                return

            with open(deckImport, "r") as f:
                text = f.read().strip()
                if text.partition("\n")[0] != "question,answer,date_created,deck":
                    print("Invalid file!")
                    return
                f.close()
                filename = os.path.basename(deckImport)
                destinationPath = os.path.join(self.path, filename)
                os.rename(deckImport, destinationPath)
                print("Deck imported successfully")

        except Exception as e:
            print(e)

    def exportDeck(self):
        """
        Allows user to export existing decks, if valid

        Parameters:
        None

        Returns:
        None
        """
        selectedDeck = self.selectDeck()
        try:
            deckExport = input("Enter the path to the deck you want to export to:\n")
            if not os.path.isdir(deckExport):
                print(f"'{deckExport}' is not a valid directory.")
                return

            shutil.copy(self.path + '\\' + selectedDeck, deckExport)
            print("Successful")

        except Exception as e:
            print(e)

    def studyDeck(self):
        """
        A function where the user could study cards from the selected deck. The frequency of cards appearing is based on their review time

        Parameters:
        None

        Returns:
        None
        """
        if not self.deck:
            print("You need to select a deck first!")
            return

        deck_copy = self.study_deck
        deck_copy.priority_deck.dequeue()#remove the header

        while not deck_copy.priority_deck.isEmpty():
            card_to_review = deck_copy.priority_deck.heap[0][1]
            if card_to_review:
                print("Question:")
                print(card_to_review.question)
                input("\nPress enter to see the answer")
                print("\nAnswer:")
                print(card_to_review.answer, "\n")

                while True:
                    choice = input("1): Again, 2): Hard, 3): Good, or 4): Remove Card")
                    if choice == '1':
                        self.study_deck.removeCard()
                        deck_copy.updateReviewTime(card_to_review, 1)
                        break
                    elif choice == '2':
                        deck_copy.updateReviewTime(card_to_review, 5)
                        deck_copy.removeCard()
                        break
                    elif choice == '3':
                        deck_copy.updateReviewTime(card_to_review, 10)
                        deck_copy.removeCard()
                        break
                    elif choice == "4":
                        deck_copy.removeCard()
                        break
                    else:
                        print("Invalid Input!")

        """OLD STUDY FUNCTION"""
        # deckCopy = self.deck
        # deckCopy.pop(0)
        # print(self.deck)
        # for i in range(0, len(self.deck)):
        #     line = random.randint(0, len(self.deck) - 1)
        #     print("Question")
        #     print(self.deck[line].question)
        #     input("\nPress enter to see the answer")
        #     print("\nAnswer")
        #     print(self.deck[line].answer, "\n")
        #     input("\nPress enter to the next question")
        #     print("\n" * 10)
        #     deckCopy.pop(line)

    def printDeck(self):
        """
        Prints a menu where the user can select what card to edit

        Parameters:
        None

        Returns:
        None
        """
        while True:
            printCards(self.deck)
            print(f"{len(self.deck)+1}): Back")
            cardEdit = input("Select a card to edit:")
            if cardEdit.isnumeric() and int(cardEdit) == len(self.deck) + 1:
                break

            elif cardEdit.isnumeric() and int(cardEdit) - 1 < len(self.deck):
                cardEditIndex = int(cardEdit) - 1
                self.deck[cardEditIndex].askCard(self.path,self.deckName)
            else:
                print("Invalid input!")

    def editDeck(self):
        """
        A function where the user can edit specific cards. They can also sort or search cards

        Parameters:
        None

        Return:
        None
        """
        # add while so that is keeps asking
        if self.deck is None:
            print("You need to select a deck first!")
            return

        while True:
            print(""
                  "1): Edit Cards\n"
                  "2): Sort Cards\n"
                  "3): Search Card\n"
                  "4): Back"
                  )
            choice = input("Select an option: ")

            if choice == "4":
                break

            if choice == "1":
                self.printDeck()

            # recall function
            elif choice == "2":
                while True:
                    print("Sort by what?"
                          "\n1): Answer alphabetically"
                          "\n2): Question alphabetically"
                          "\n3): Last Created"
                          "\n4): Back"
                          )
                    edit = input("Select an option:")
                    if edit == "4":
                        break  # break from loop
                    elif edit == "1":
                        self.deck = quickSort(self.deck, 0, len(self.deck) - 1, "question")
                        self.editDeck()
                    elif edit == "2":
                        self.deck = quickSort(self.deck, 0, len(self.deck) - 1, "answer")
                        self.editDeck()
                    elif edit == "3":
                        self.deck = quickSort(self.deck, 0, len(self.deck) - 1, "date")
                        self.editDeck()
                    else:
                        print("Invalid Input!")

            elif choice == "3":
                while True:
                    print("Search by what?"
                          "\n1): Question"
                          "\n2): Back"
                          )
                    edit = input("Select an option:")
                    if edit == "2":
                        break  # break from loop

                    elif edit == "1":
                        foundCards = []
                        question = input("Enter question to search for:")
                        for i in self.deck:
                            if i.question == question:
                                foundCards.append(i)

                        self.printDeck()

                    else:
                        print("Invalid Input!")

            else:
                print("Invalid input!")

class Card:
    def __init__(self,question,answer,date,row_number):
        """
        A basic card class that makes each card
        in a deck a card

        Parameters:
        question (str): The question to a card
        answer (str): The answer to a card
        date (str): The date the cards was created on
        row_number (int): A number that shows which row a card is stored in the csv

        Returns:
        str: The question of a card
        stt: Thr answer of a card
        str: The date the cards was created on
        """
        self.question = question
        self.answer = answer
        self.date = date
        self.row = row_number
        self.review_time = 1

    def __lt__(self, other):
        # Compare based on review_time
        return self.review_time < other.review_time

    def displayQuestion(self):
        return self.question

    def displayAnswer(self):
        return self.answer

    def displayDateCreated(self):
        return self.date

    def askCard(self,path,deckName):
        """
        A function that prints a menu where the user can edit a card or exit the menu

        Parameters:
        path (str): A string representing the directory where the decks are stored
        deckName (str): The name of the selected deck

        Returns:
        None
        """
        while True:
            print(
                f"Question): {self.question} Answer):{self.answer} Date Created): {self.date}")
            print(""
                  "1): Edit Question/Answer\n"
                  "2): Back"
                  )
            edit = input("Select an option:")
            if edit == "2":
                break  # break go back
            elif edit == "1":  # edits question
                self.editCard(path,deckName)
                break
            else:
                print("Invalid input!")

    def editCard(self,path,deckName):
        """
        A function where the user can edit a cards question or answer

        Parameters:
        path (str): A string representing the directory where the decks are stored
        deckName (str): The name of the selected deck

        Return:
        None
        """
        with open(path + "\\" + deckName, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)  # Store all rows in a list
        while True:
            print("Old Question:")
            print(self.question)
            choice = input("1): Edit Question"
                           "\n2): Skip")
            if choice == "1":
                newQuestion = input("\nWhat is the new question:")
                rows[self.row][0] = newQuestion
                with open(path + "\\" + deckName, "w", newline='') as f:
                    w = csv.writer(f)
                    w.writerows(rows)
                    self.question = newQuestion
                    break

            elif choice == "2":
                break

            else:
                print("Invalid Input!")
        while True:
            print("Old Answer:")
            print(self.answer)
            choice = input("1): Edit Answer"
                           "\n2): Skip")
            if choice == "1":
                newAnswer = input("\nWhat is the new answer:")
                rows[self.row][1] = newAnswer
                with open(path + "\\" + deckName, "w", newline='') as f:
                    w = csv.writer(f)
                    w.writerows(rows)
                    self.answer = newAnswer
                    break

            elif choice == "2":
                break

            else:
                print("Invalid Input!")

class DeckSchedule:
    def __init__(self):
        """
        Initializes a deck to be studied as a Priority Queue

        Parameters:
        None

        Returns:
        None
        """
        self.priority_deck = PriorityQueue()

    def addCard(self,card):
        """
        Adds a card with a priority number and their info to the priority queue

        Parameters:
        card (Card): The card to be added to the priority queue

        Returns:
        None
        """
        priority = card.review_time
        self.priority_deck.enqueue(priority,card)

    def removeCard(self):
        """
        Removes a card if it is over review date

        Parameters:
        None

        Returns:
        None
        """
        #do a check here or in the function
        self.priority_deck.dequeue()

    def updateReviewTime(self,card,time):
        """
        Updates a card review time based on if the user knows/does not know the card for more frequent review

        Parameters:
        card (Card): The card to edit
        time (int): The time to change in the review time

        Returns:
        None
        """
        card.review_time = time
        self.addCard(card)

class TimedCard(Card):
    def __init__(self,question,answer,date,time_limit,row_number):
        self.time = time_limit
        super().__init__(question,answer,date,row_number)

    def displayQuestion(self):# add a time lime to how long they can answer the question
        return self.question

    def displayAnswer(self):
        return self.answer

    def displayDateCreated(self):
        return self.date

invalidChars = ["\\","/",":", "*", "?",'"', "<", ">", "|"] #characters that can not be in a file's name in windows

directory = r"C:\Users\JoJo\Desktop\Python\hw west\Midterm\Decks"+'\\' # replace with any desired path to store the decks

def printCards(deck):
    """
    Print all the cards information in a deck

    Parameters
    deck (arr): An array containing all cards in the deck

    Returns
    None
    """
    for n, card in enumerate(deck, 1):
        print(f"{n}): Question): {card.question} Answer):{card.answer} Date Created): {card.date}")
    print(f"{len(deck) + 1}): Back")

def quickSort(ar,low,high,obj_func):
    if low >= high:
        return

    pivot = ar[random.randint(low,high)]
    i = low-1
    for j in range(low,high):
        if getattr(ar[j],obj_func) < getattr(pivot,obj_func):
            i += 1
            ar[i],ar[j] = ar[j],ar[i]

    ar[i+1],ar[high] = ar[high],ar[i+1]
    pi = i+1

    quickSort(ar,low,pi-1,obj_func)
    quickSort(ar,pi+1,high,obj_func)

    return(ar)



"""
MAIN LOOP HERE
"""

deck = Deck(directory)
while True:

    print(""
          "1): Make Deck"
          "\n2): Select Deck"
          "\n3): Study Deck"
          "\n4): Edit Deck"
          "\n5): Export Deck"
          "\n6): Import Deck"
          "\n7): Exit"
          )
    menuChoice = input("Choose an option:\n")

    if menuChoice == "7":
        break
    elif menuChoice == "1":
        deck.makeDeck()
    elif menuChoice == "2":
        deck.selectDeck()
        deck.extractDeck()
    elif menuChoice == "3":
        deck.studyDeck()
    elif menuChoice == "4":
        deck.editDeck()
    elif menuChoice == "5":
        deck.exportDeck()
    elif menuChoice == "6":
        deck.importDeck()
    else:
        print("Invalid Input!")


