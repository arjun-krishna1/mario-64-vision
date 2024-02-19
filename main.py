import pyautogui
import os
import time
import base64
import json

import uuid

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Function to cal gpt 4 vision api
def make_image_api_call(client, image_url, text):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_url}"
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response

# Function to make gpt 4 text API call
def make_text_api_call(client, text, format):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                ],
            }
        ],
        max_tokens=300,
        response_format={"type": format}
    )
    return response

def take_centered_screenshot(width=700, height=500, save_path='centered_screenshot.png'):
    """
    Takes a screenshot of a specified width and height, centered on the screen.

    Args:
    - width: The width of the screenshot area.
    - height: The height of the screenshot area.
    - save_path: The file path where the screenshot will be saved.
    """
    screen_width, screen_height = pyautogui.size()  # Get the size of the primary monitor.

    # Calculate the top left coordinates of the screenshot area to center it
    # added padding to take screnshot of the game screen only
    left = (screen_width - width) // 2 - 280
    top = (screen_height - height) // 2 + 50

    # Capture and save the screenshot
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(save_path)
    print(f"Screenshot saved to {save_path}.")

def execute_move(move):
    move_key_map = {
        "right": "h",
        "left": "f",
        "forward": "t",
        "backward": "g",
        "jump": "x",
        "punch": "s",
    }

    if move in move_key_map:
        move_key = move_key_map[move]
        # TODO pyautogui was not working on wayland ubuntu
        # so installed and switched in ydotool
        # pyautogui.typewrite(move_key, interval=0.25)
        os.system(f"ydotool key --delay 50 --repeat 12 {move_key}")
    else:
        print(f"key not found for move {move}")

def main():
    print("Starting the program, taking a screenshot...")
    time.sleep(1)

    while True:
        try:
            screenshot_path = f"{uuid.uuid4()}.png"
            print(f"Taking screenshot to {screenshot_path}")

            # Take a centered screenshot
            take_centered_screenshot(save_path=screenshot_path)
            image_url = encode_image(screenshot_path)

            print("Calling OpenAI API")
            
            # Observe the current scene with GPT 4 Vision
            OBSERVATION_TASK = """You are an expert Super Mario 64 player who has beat this game many times.
            You are action-oriented and decisive.
            List enemies, doors and in-game interactive elements that will be important to the game that are ON SCREEN.
            When listing elements, mention the general direction of them with relation to the Mario character.
            Do not list Mario, Counters/Meters or Controls or elements that are not ON SCREEN"""
            observation_response = make_image_api_call(client, image_url, OBSERVATION_TASK)

            print(f"Result for Observation Task': {observation_response.choices[0].message.content}")

            PLANNING_TASK = f"""You are an expert Super Mario 64 player who has beat this game many times.
            You are action-oriented and decisive.
            Given these observations of a scene from the Super Mario 64 game think step by step and give what immediate action should be taken to get closer to the star (objective).
            Be specific in terms of the general directions the character should be moved towards and what actions they should take
            Example: Move closer to the door by moving forward
            Be concise and give only one clear and simple plan
            Observation: {observation_response.choices[0].message.content}"""
            planning_response = make_text_api_call(client, PLANNING_TASK, "text")

            print(f"Result for Planning Task': {planning_response.choices[0].message.content}")

            # Get next series of moves
            NEXT_MOVE_TASK = f"""You are an expert Super Mario 64 player who has beat this game many times.
            You are action-oriented and decisive even if there is not much to go off of.
            Given this short term plan give a short list of moves to implement it: {planning_response.choices[0].message.content}

            Here is a list of possible moves for you to take:
            right
            left
            forward
            back
            jump
            punch

            Give a list of moves to go down this path before you would need another observation. Be concise and return the result in JSON with the following format:
            moves: [
                "move_right_of_camera",
                ... all moves are only from the list of possible moves avoce
            ]
            """
            move_response = make_text_api_call(client, NEXT_MOVE_TASK, "json_object")

            print(f"Result for Moving Task': {move_response.choices[0].message.content}")

            moves = json.loads(move_response.choices[0].message.content)["moves"]

            print(f"Starting the following moves: {moves}")
            for move in moves:
                print(f"Doing the move {move}")
                execute_move(move)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            pass  # This will pass any other exceptions


if __name__ == "__main__":
    main()
