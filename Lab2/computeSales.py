import sys #sys.exit to quit application
import re

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


def printm(m):
    for i in m:
        print(i)

class fileReader:
    '''
    Read and parse receipt files
    receipts are returned as :
        [String:AFM, Dict:receiptData, Float:receiptSum]
    receiptData:
        {ItemName: [Quantity, Price, Total]}
    '''
    def __init__(self, file):
        self.file = file

    def __fileBuffer(self):
        '''
        Reads file and returns a single receipt as String
        '''
        buffer = ''
        for line in self.file:
            if (re.fullmatch('[-]+\n', line)): return buffer;
            buffer += line
        return None

    def __readFile(self, step):
        '''
        Reads file and returns a defined amount (or less) of receipts
        :param step: number of receipts to read
        :return: list of raw receipts as strings
        '''
        chunks = []
        while ((chunk := self.__fileBuffer()) != None and (len(chunks) < step or step == -1)):
            chunks.append(chunk)
        return chunks

    def __parseChunks(self, chunks):
        '''
        Matches a list of raw receipts using regular expressions. All raw receipts that do not follow the syntactical
        rules of the file will be ignored.
        :param chunks: list of raw receipts
        :return: re matches of receipts
        '''
        matches = []
        for c in chunks:
            x = re.match("ΑΦΜ[ \t]*:[ \t]*([0-9]{10})\n(([\sα-ωΑ-Ωa-zA-Z]+:[ \t]*[0-9]+[ \t]+[0-9]+[.[0-9]+]?[ \t]+[0-9]+[.[0-9]+]?\n)+)[α-ω Α-Ω]+[ \t]*:[ \t]*([0-9]+[.[0-9]+]?)",c)
            if x != None: matches.append(x.groups())
        return matches

    def __parseMatch(self, match):
        '''
        Analyzes the matched receipt using regular expressions.
        This is used to analyze tha data portion of the matched receipt.
        :param match: matched receipt
        :return: list of [AFM as String, Data of receipt as re Match, Total as float]
        '''
        AFM = match[0]
        Total = float(match[3])
        DataMatch = re.findall("([\sα-ωΑ-Ωa-zA-Z]+):[ \t]*([0-9])+[ \t]+([0-9]+[.[0-9]+]?)[ \t]+([0-9]+[.[0-9]+]?)[ \t]*\n",match[1])
        return [AFM, DataMatch, Total]

    def __parseDataMatch(self, DataMatch):
        '''
        Parses the data portion of the receipt converting it to dict.
        Returns None for receipts that have arithmetic errors.
        :param DataMatch: dataMatched receipt
        :return: receipt or None
        '''
        data = {}
        sum = 0
        for match in DataMatch[1]:
            flmatch = list(map(lambda x: float(x), match[1:]))
            if flmatch[2] != round(flmatch[0]*flmatch[1],2): return None
            sum+=flmatch[2];
            if data.get(match[0]):
                data[match[0]][0] += flmatch[0]
                data[match[0]][2] += flmatch[2]
            else:
                data[match[0]] = flmatch
        if DataMatch[2] != sum : return None
        DataMatch[1]=data;
        return DataMatch

    def next(self,step = 1000):
        '''
        Returns next receipts from files
        :param step: number of receipts to read, -1 for all receipts of file
        :return: parsed receipts
        '''
        matches = self.__parseChunks(self.__readFile(step))
        if matches.__len__()==0:return None;
        return list(filter(None, list(map(lambda x: self.__parseDataMatch(self.__parseMatch(x)), matches))))

with open("testFile.txt") as file:
    fr = fileReader(file)
    printm(fr.next(-1))
    # while (receipt := fr.next(10)):
    #     print(receipt)


# program execution starts here
main()
