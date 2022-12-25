import os
import tkinter as tk
import numpy as np
import itertools as it
from PIL import ImageTk, Image

def generate_cards(num_cards=57, num_symbols=57, images_per_card=8):
    image_adjacency = np.eye(num_cards, dtype=int) * -1
    # set the number of images left to set per card
    num_images = {card: 8 for card in range(num_cards)}
    final_groups = []
    
    while np.sum(image_adjacency == 0) > 0:
        if num_cards > num_symbols:
            raise ValueError("Not enough symbols for game of this size.")
        # select a set of (num_cards - 1) // images_per_card or (num_cards - 1) // images_per_card + 1
        # card values that satisfy a set of criterion
        # create a list that keeps the order in which a group of images is added in
        image_group = []
        banned_set = set()
        possible_card = -1
        while len(image_group) < ((num_cards - 1)//images_per_card + 1):
            if len(image_group) == 0:
                if possible_card == num_cards - 1:
                    removed_group = final_groups.pop()
                    banned_set = set()
                    for edge in it.permutations(removed_group, 2):
                        image_adjacency[edge] = 0
                    possible_card = 0
                else:
                    possible_card += 1
            else:
                # random choice from card that has no edge with existing cards in the set
                possible_cards = list(set.intersection(*[set(list(np.where(image_adjacency[selected_card] == 0)[0])) for selected_card in image_group]) - banned_set)
                if len(possible_cards) == 0:
                    latest_image = image_group.pop()
                    banned_set.add(latest_image)
                    continue
                else:
                    possible_card = np.random.choice(possible_cards, size=1).item()
            image_group.append(possible_card)
            print(final_groups)
        for image in image_group:
            num_images[image] -= 1
        for edge in it.permutations(image_group, 2):
            image_adjacency[edge] = 1
        final_groups.append(image_group)
        # DONT DO THIS ASSIGNMENT UNTIL THE END
        # FOR BACKTRACKING KEEP A RUNNING LIST OF GROUPS AND KEEP THE BACKTRACKING GOING UNTIL YOU HAVE 57 GROUPS
    running_id = 1
    for group in final_groups:
        for edge in it.permutations(group, 2):
            image_adjacency[edge] = running_id
        running_id += 1

    for row in range(len(image_adjacency)):
        for other_row in range(row + 1, len(image_adjacency)):
            # 2 because of the match to itself and 1 other card
            assert len(set(image_adjacency[row]).intersection(set(image_adjacency[other_row]))) == 2
    print("This game is valid!")

    # script should assign numbers to a particular image

    return image_adjacency

def update_card(window, cards, you, game_images, label_dict, image_dict, image):

    # get window width
    window_width = window.winfo_reqwidth()

    # check if the game is over
    if len(cards) == 0:
        if you:
            for k, _ in image_dict[1].items():
                label_dict[1][k].destroy()
            label = tk.Label(text='YOU WIN!')
            label.place(x = 0.15 * window_width, y = 0.4 * window_width, anchor='s')
        else:
            for k, _ in image_dict[2].items():
                label_dict[2][k].destroy()
            label = tk.Label(text='The AI beat you.')
            label.place(x = 0.85 * window_width, y = 0.4 * window_width, anchor='s')
        return "Game Finished"

    new_card_index = np.random.choice(cards.shape[0], size=1, replace=False)
    new_card = cards[new_card_index]
    cards = np.delete(cards, new_card_index, axis=0)

    images = set(new_card[0])
    # remove self edge
    images.discard(-1)

    # check if the image is in the center card
    if image not in [image_dict[0][j][1] for j in range(len(images))]:
        return cards

    # change the image
    # Question: Why don't I need to destroy center buttons?
    i = 1 if you else 2
    for k, _ in image_dict[i].items():
        image_dict[0][k] = image_dict[i][k]
        label_dict[0][k] = tk.Button(image=image_dict[0][k][0], bd=0, bg="white", relief='sunken', command=tk.DISABLED)
        label_dict[0][k].place(x = label_dict[i][k].winfo_rootx() + 0.35 * (-np.sign(i - 1.5)) * window_width - 10, y = label_dict[i][k].winfo_rooty() - 0.3 * window_width - 20)
        label_dict[i][k].destroy()
    for j, image in enumerate(images):
        raw_image = Image.open("game_images/" + game_images[image - 1])
        transformed_image = raw_image.resize((np.random.randint(30, 90),)*2).rotate(np.random.uniform(0, 360))
        # create new button and move the old button to the center
        image_dict[i][j] = (ImageTk.PhotoImage(transformed_image), image)
        label_dict[i][j] = tk.Button(image=image_dict[i][j][0], bd=0, bg="white", command = lambda image=image: update_card(window, cards, bool(i-2), game_images, label_dict = label_dict, image_dict = image_dict, image = image))
        offset_x_low, offset_x_high = (-0.4, -0.3) if i == 1 else (0.3, 0.4)
        label_dict[i][j].place(x=np.random.uniform((0.5 + offset_x_low) * window_width,  (0.5 + offset_x_high) * window_width), y=np.random.uniform(0.35 * window_width, 0.45 * window_width))

    return cards 

def launch_game(window_width=1250, window_height=750):

    # generate the cards
    cards = generate_cards(num_cards=31, images_per_card=6)

    # get the images
    game_images = os.listdir("game_images")

    # declare the window
    window = tk.Tk()
    # set window title
    window.title("Spot It!")
    # set window width and height (originally)
    window.configure(width=window.winfo_screenwidth(), height=window.winfo_screenheight())
    # set window background color
    window.configure(bg='white')

    # Create a canvas object
    window_width, window_height = window.winfo_reqwidth(), window.winfo_reqheight()
    c = tk.Canvas(window, width=window.winfo_screenwidth(), height=window.winfo_screenheight(), bg="white")
    c.pack()

    # Draw an Oval in the canvas
    
    c.create_oval(0.4 * window_width, 10 , 0.6 * window_width, 10 + 0.2 * window_width)

    # Your card
    c.create_oval(0.05 * window_width, 0.3 * window_width , 0.25 * window_width, 0.5 * window_width)
    # AI's card
    c.create_oval(0.75 * window_width, 0.3 * window_width , 0.95 * window_width, 0.5 * window_width)

    # create user labels
    c.create_window(0.15 * window_width, 0.5 * window_width + 30, window=tk.Label(text="You", width=10, height=2))
    c.create_window(0.85 * window_width, 0.5 * window_width + 30, window=tk.Label(text="AI", width=10, height=2))

    # WORKFLOW

    # initialize game
    starting_card_indeces = np.random.choice(cards.shape[0], size=3, replace=False)
    starting_cards = cards[starting_card_indeces]
    cards = np.delete(cards, starting_card_indeces, axis=0)
    cards_you = cards[np.random.choice(cards.shape[0], size=len(cards)//2, replace=False)]
    cards_AI = cards[np.random.choice(cards.shape[0], size=len(cards)//2, replace=False)]

    assert len(cards_you) == len(cards_AI)
    # print(f"You and the AI both have {len(cards_you + 1)} cards.")

    image_dict = {}
    label_dict = {}
    for i, card in enumerate(starting_cards):
        images = set(card)
        # remove self edge
        images.discard(-1)
        image_dict[i] = {}
        label_dict[i] = {}
        for j, image in enumerate(images):
            raw_image = Image.open("game_images/" + game_images[image - 1])
            transformed_image = raw_image.resize((np.random.randint(30, 90),)*2).rotate(np.random.uniform(0, 360))
            # dictionary assignment doesn't overwrite buttons and they all get saved
            image_dict[i][j] = (ImageTk.PhotoImage(transformed_image), image)
            if i == 0:
                label_dict[i][j] = tk.Button(image=image_dict[i][j][0], bd=0, bg="white", relief='sunken', command=tk.DISABLED)
                label_dict[i][j].place(x=np.random.uniform(0.45 * window_width,  0.55 * window_width), y=np.random.uniform(10 + 0.05 * window_width, 10 + 0.15 * window_width))
            if i == 1:
                label_dict[i][j] = tk.Button(image=image_dict[i][j][0], bd=0, bg="white", command = lambda image=image: update_card(window, cards_you, True, game_images, label_dict = label_dict, image_dict = image_dict, image = image))
                label_dict[i][j].place(x=np.random.uniform(0.1 * window_width,  0.2 * window_width), y=np.random.uniform(0.35 * window_width, 0.45 * window_width))
            if i == 2:
                label_dict[i][j] = tk.Button(image=image_dict[i][j][0], bd=0, bg="white", command = lambda image=image: update_card(window, cards_AI, False, game_images, label_dict = label_dict, image_dict = image_dict, image = image))
                label_dict[i][j].place(x=np.random.uniform(0.8 * window_width,  0.9 * window_width), y=np.random.uniform(0.35 * window_width, 0.45 * window_width))
    
    window.mainloop()

if __name__ == "__main__":
    launch_game()