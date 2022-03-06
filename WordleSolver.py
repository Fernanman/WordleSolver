from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from SS import SS

PATH = "chromedriver.exe"

def solve_word(word_list):
    solved = False

    # Sets up selenium and then clicks the x button 
    driver = webdriver.Chrome(PATH)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    url = "https://www.nytimes.com/games/wordle/index.html"
    driver.get(url)
    driver.maximize_window()

    body = driver.find_element(By.TAG_NAME, 'body')
    body.click()
    
    possible_words = []

    with open(word_list, 'r') as f:
        for word in f:
            word = word.replace('\n', '')
            possible_words.append(word)

    tries = 1
    test_var = 0    

    letter_blacklist = set()
    correct_positions = {}
    wrong_positions = defaultdict(set)
    
    ss = SS(795, 856, 304, 365, 67, 68)

    while tries < 7 and not solved:

        # First guess always being crane 
        if tries == 1:
            guess = "house"
        # Concurrent guesses will pick the word that will get rid of most other words if it is wrong 
        else:
            new_letters = {}
            most_common_letter = defaultdict(int)
            word_picker = {}

            # Goes ahead and finds the most common letters and the words that have the most unique letters
            for i, word in enumerate(possible_words):
                letter_string = ""
                for letter in word:
                    if (letter not in wrong_positions) and (letter not in correct_positions.values()):
                        most_common_letter[letter] += 1
                        if letter not in letter_string:
                            letter_string += letter
                # Appends to the new letters list a tuple with the index of the word and how many new letters it contains
                new_letters[i] = len(letter_string)
            
            # Gives values to each word and then 
            for i, word in enumerate(possible_words):
                value = new_letters[i]
                used_letters = ""

                for letter in word:
                    if letter in most_common_letter and letter not in used_letters:
                        used_letters += letter
                        value += most_common_letter[letter]

                word_picker[i] = value

            # Picks the word that has the highest value
            for i in word_picker:
                if i == 0:
                    largest_value_index = i
                else:
                    if word_picker[i] > word_picker[largest_value_index]:
                        largest_value_index = i

            guess = possible_words[largest_value_index]

        # Enters the guess then enters
        body.send_keys(guess)
        body.send_keys(Keys.RETURN)
        time.sleep(3)

        # Takes screneshots
        ss.get_letters()
        #ss.show_images(test_var)
        test_var += 1
        ss.go_down()
        time.sleep(3)

        # If it is solved
        if ss.color_map[-1] == [2, 2, 2, 2, 2]:
            print("Correct guess! Word was:", guess + '.', "Gotten with", 6 - tries, "tries left.")
            solved = True
            break
        else:
            print("Guessed word was:", guess + ',', 6 - tries, "tries left.")
            if tries == 6:
                print(possible_words)

            for i in range(len(ss.color_map[-1])):
                # Puts the letters in correct positions dictionary
                if ss.color_map[-1][i] == 2:
                    correct_positions[i] = guess[i]
                # Puts letters in black list
                elif ss.color_map[-1][i] == 0:
                    letter_blacklist.add(guess[i])
                #Puts letters in wrong positions if letter is in the word but not in the right position
                elif ss.color_map[-1][i] == 1:
                    wrong_positions[guess[i]].add(i)

            #Adjusts the possible words according to the parameters
            for word in possible_words[:]:
                broke = False

                #Removes all the words that have blacklisted letters in them
                for letter in letter_blacklist:
                    if letter in word:
                        possible_words.remove(word)
                        broke = True
                        break
                if broke: 
                    continue

                #Removes all words that don't have letters in the correct positions
                for i in correct_positions:
                    if word[i] != correct_positions[i]:
                        possible_words.remove(word)
                        broke = True
                        break
                if broke: 
                    continue

                #Removes all words that don't have those letters as well as those that do have them in that position
                for letter in wrong_positions:
                    if letter not in word:
                        possible_words.remove(word)
                        broke = True
                        break
                    else:
                        for i in wrong_positions[letter]:
                            if letter == word[i]:
                                possible_words.remove(word)
                                broke = True
                                break
                        if broke: break
                if broke: 
                    continue

        tries += 1

    time.sleep(100)

if __name__ == "__main__":
    solve_word('Five Word List.txt')