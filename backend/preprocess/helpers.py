from itertools import islice
import json
import os


with open('emojiIndex.json', 'r', encoding='utf8') as f:
    emoji_index = json.load(f)

# read emojiIndex.json
# emojiIndex from https://github.com/Tyrrrz/DiscordChatExporter/blob/5b1b7205037662bb28dc5e541f0950586d4b8a22/DiscordChatExporter.Core/Utils/EmojiIndex.cs
def get_emoji_code(name):
    if name in emoji_index:
        return emoji_index[name]
    else:
        return name


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


def is_compiled():
	if os.path.exists(__file__):
		return False
	else:
		return True


def batched(iterable, n):
	"Batch data into tuples of length n. The last batch may be shorter."
	# batched('ABCDEFG', 3) --> ABC DEF G
	if n < 1:
		raise ValueError('n must be at least one')
	it = iter(iterable)
	while (batch := tuple(islice(it, n))):
		yield batch



def find_missing_numbers(set1, set2):

    # both sets must be at least 2 elements
    if len(set1) < 1 or len(set2) < 1:
        print("Sets must be at least 2 elements")
        return set()

    lowest_set1 = min(set1)
    highest_set2 = max(set2)
    if lowest_set1 > highest_set2:
        # print("No common boundaries")
        return set()

    lowest_set2 = min(set2)
    highest_set1 = max(set1)
    if lowest_set2 > highest_set1:
        # print("No common boundaries")
        return set()

    # find common boundaries
    higher_lowest = max(lowest_set1, lowest_set2)
    lower_highest = min(highest_set1, highest_set2)

    # print(lowest_set1, lowest_set2, highest_set1, highest_set2)
    # print(higher_lowest, lower_highest)

    # create new sets between boundaries
    new_set1 = set()
    new_set2 = set()
    for i in set1:
        if i >= higher_lowest and i <= lower_highest:
            new_set1.add(i)
    for i in set2:
        if i >= higher_lowest and i <= lower_highest:
            new_set2.add(i)

    # print(new_set1, new_set2)

    # find symmetric difference
    symmetric_difference = new_set1.symmetric_difference(new_set2)

    # print(symmetric_difference)
    return symmetric_difference

# def find_missing_numbers_multiple(sets: list[set]) -> set:
#     """
#     not used
#     """
#     diff = set()
#     print(f"        needs {round(len(sets) * (len(sets) - 1) / 2)} combinations")
#     for i in range(len(sets)):
#         for j in range(i+1, len(sets)):
#             # print(i, j)
#             diff = diff.union(find_missing_numbers(sets[i], sets[j]))
#     return diff

def find_additional_missing_numbers(sets: list[set], new_set:set) -> set:
    diff = set()
    for i in range(len(sets)):
        diff = diff.union(find_missing_numbers(sets[i], new_set))
    return diff