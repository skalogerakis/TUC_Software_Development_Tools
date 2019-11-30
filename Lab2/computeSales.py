import sys  # sys.exit to quit application
import re
import time
import math


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
		while (True):

			chunk = self.__fileBuffer()
			if chunk == None or (len(chunks) >= step and step != -1): break

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
			x = re.match(
				"ΑΦΜ[ \t]*:[ \t]*([0-9]{10})\n(([ \t]*[\sα-ωΑ-Ωa-zA-Z]+[ \t]*:[ \t]*[0-9]+[ \t]+[0-9]+[.[0-9]+]?[ \t]+[0-9]+[.[0-9]+]?\n)+)[α-ω Α-Ω]+[ \t]*:[ \t]*([0-9]+[.[0-9]+]?)",
				c)
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
		DataMatch = re.findall(
			"[ \t]*([\sα-ωΑ-Ωa-zA-Z]+?)[ \t]*:[ \t]*([0-9])+[ \t]+([0-9]+[.[0-9]+]?)[ \t]+([0-9]+[.[0-9]+]?)[ \t]*\n", match[1])
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
			name = match[0].upper()
			# TODO somewhere here loses in decimal
			flmatch = list(map(lambda x: float(x), match[1:]))
			if flmatch[2] != round(flmatch[0] * flmatch[1], 2): return None
			sum += flmatch[2]
			if data.get(name):
				data[name] += flmatch[2]
			else:
				data[name] = flmatch[2]
		# Add some tolerance to the comparison to avoid errors due to float calculation
		if not math.isclose(DataMatch[2], sum, abs_tol=0.001): return None
		DataMatch[1] = data
		return DataMatch

	def next(self, step=100):
		'''
		Returns next receipts from files
		:param step: number of receipts to read, -1 for all receipts of file
		:return: parsed receipts
		'''
		matches = self.__parseChunks(self.__readFile(step))
		if matches.__len__() == 0: return None;
		return list(filter(None, list(map(lambda x: self.__parseDataMatch(self.__parseMatch(x)), matches))))


def mergeDict(dict1, dict2):
	''' Merge dictionaries and sum values of common keys in list'''
	dict3 = {**dict1, **dict2}
	for key, value in dict3.items():
		if key in dict1 and key in dict2:
			dict3[key] = value + dict1[key]
	return dict3


AFMDict = {}
ProductDict = {}


def printm(m):
	for i in m:
		print(i)


def main():
	menu()


# function that processes all data from new file
def new_file():
	print("Enter file name:")
	choice = input()
	try:
		with open(choice) as file:

			fr = fileReader(file)
			while (True):
				receipts = fr.next()
				if not receipts: break
				for receipt in receipts:
					# Populate AFM Dict
					if AFMDict.get(receipt[0]):
						AFMDict[receipt[0]] = mergeDict(AFMDict[receipt[0]], receipt[1])
					else:
						AFMDict[receipt[0]] = receipt[1]
					# Populate Product Dict

					for k, v in receipt[1].items():
						if ProductDict.get(k):
							if ProductDict[k].get(receipt[0]):
								ProductDict[k][receipt[0]] += v
							else:
								ProductDict[k][receipt[0]] = v
						else:
							ProductDict[k] = {receipt[0]: v}
	except FileNotFoundError:
		pass


# Function that prints statistics for a specific product
def product_stat():
	print("Enter Product Name:")
	choice = input().upper()
	if not ProductDict.get(choice): return
	for key, value in sorted(ProductDict[choice].items(), key=lambda item: (item[0], item[1]), reverse=False):
		print("%s %.2f" % (key, round(value, 2)))

'''
	NOT USED.Function that prints statistics for a specific product ONLY IN CASE OF VERY LARGE FILE(In this case we dont 
	create two different dictionaries to prevent memory issues. The dictionary left has as key AFM, so in order to find 
	our result we search through all the values. This leads on large complexity and slow run time as we need to parse 
	the whole dictionary but it will not fail during execution). This function could substitute product_stat and
	no second dictionary would be demanded
'''
# def product_stat_BIGFILE():
# 	print("Enter Product Name:")
# 	choice = input().upper()
#
# 	for key, values in AFMDict.items():
# 		# for base_key in AFMDict.keys():
# 		valUpdater = 0;
# 		flag = 0;
# 		for val in values:
# 			if val == choice:
# 				flag = 1;
# 				valUpdater += AFMDict[key].get(val)
#
# 		if flag == 0: continue
# 		print("%s: %.2f" % (key, round(valUpdater, 2)))


# Function that prints statistics for a specific AFM
def afm_stat():
	print("Enter AFM:")
	choice = input()
	if not AFMDict.get(choice): return
	for key, value in sorted(AFMDict[choice].items(), key=lambda item: (item[0], item[1]), reverse=False):
		print("%s %.2f" % (key, round(value, 2)))


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
	menu()


# Our main menu
def menu():
	print()
	print(
		"Give your preference: (1: read new input file, 2: print statistics for a specific product, 3: print statistics for a specific AFM, 4: exit the program)")
	choice = input()
	menu_choice(choice)


if __name__ == "__main__": main()
