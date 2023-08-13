from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from SS import SS

PATH = "chromedriver.exe"

def setup_page():
    # Sets up selenium and then clicks the x button 
    service = ChromeService(executable_path=PATH)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options,service=service)
    url = "https://www.nytimes.com/games/wordle/index.html"
    driver.get(url)
    driver.maximize_window()
    
    continue_button = driver.find_element(By.CLASS_NAME, 'purr-blocker-card__button')
    continue_button.click()

    time.sleep(1)

    start_button = driver.find_element(By.CLASS_NAME, 'Welcome-module_button__ZG0Zh')
    start_button.click()

    driver.execute_script("window.scrollTo(0, 400)")

    exit_button = driver.find_element(By.CLASS_NAME, "Modal-module_closeIcon__TcEKb")
    exit_button.click()

    time.sleep(2)

    imgs = driver.find_elements(By.TAG_NAME, 'button')
    for img in imgs:
        print(img.get_attribute("alt"))
        print("--")

    body = driver.find_element(By.TAG_NAME, 'body')

    time.sleep(1)
    return body

def solve_word(word_list):
    body = setup_page()

    solved = False
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
    
    #ss = SS(788, 850, 292, 353, 70, 70) # Without ads
    ss = SS(753, 800, 215, 260, 85, 85)

    while tries < 7 and not solved:

        # First guess always being crane 
        if tries == 1:
            guess = "arose"
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
            
            print("Possible words on try", tries, ":", possible_words)
            guess = possible_words[largest_value_index]


        # Enters the guess then enters
        body.send_keys(guess)
        body.send_keys(Keys.RETURN)
        time.sleep(3)

        # Takes screneshots
        ss.get_letters()
        ss.show_images(test_var)
        test_var += 1
        ss.go_down()
        time.sleep(3)
        
        print(ss.color_map[-1])

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
                        if letter in correct_positions.values():
                            for index in correct_positions:
                                if correct_positions[index] == letter and word[index] == letter:
                                    word = None
                        
                        if word != None:
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
        if guess in possible_words:
            possible_words.remove(guess)


    if solved: 
        time.sleep(30)
    else:
        print("Remaining possible words: ", possible_words)


if __name__ == "__main__":
    #setup_page()
    solve_word('Five Word List.txt')