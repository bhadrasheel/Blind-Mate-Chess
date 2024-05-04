import requests
import json
import pyttsx3
import sys
import re
import gesture as ges

api_token = "lip_yzGgMK9RQgJTo2aMUlHH"
username = "Happy02001"
game_id=""


engine = pyttsx3.init()
engine.setProperty('rate', 150) 




def get_current_ongoing_game(username):
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.get(f"https://lichess.org/api/user/{username}/current-game", headers=headers)
        if response.status_code == 200:
            game_data = response.json()
            return game_data
        else:
            print(f"Failed to retrieve the current ongoing game for {username}.")
            return None
    except requests.RequestException as e:
        print(f"An error occurred while retrieving the current ongoing game: {str(e)}")
        return None


current_ongoing_game = get_current_ongoing_game(username)

if current_ongoing_game:
    game_id = current_ongoing_game['id']





def recognize_confirmation(notation):

    while True:
        
        engine.say(f"You said {notation}, is that correct?")
        engine.runAndWait()
            
        test_string = ges.guess()

        if bool(re.match(r'(i9|j10)$', test_string)):
            notation = test_string
        else:
            notation = notation



        if notation == "i9":
            print("Confirmed")
            engine.say("Confirmed")
            engine.runAndWait()
            return True
        elif notation == "j10":
            print("Not confirmed")
            engine.say("Not confirmed")
            engine.runAndWait()
            return False
                
        




def recognize_notation(last_move):


    while True:
            
        print("Please show a valid chess notation")
        engine.say("Please show a valid chess notation")
        engine.runAndWait()

    
                
        test_string = ges.guess()

        if bool(re.match(r'[a-hA-H][1-8]$', test_string)):
            notation = test_string
        else:
            notation = ""

        if notation:

            print(f"Recognized notation: {notation.upper()}")

            confirm = recognize_confirmation(notation)

            if confirm:
                return notation.lower()
            else:
                engine.say(f"Last Move is {last_move}")
                engine.runAndWait()
        else:
            print(f"Invalid notation")
            engine.say("Sorry, I did not recognize a valid notation")
            engine.runAndWait()





def move(last_move):

    value = False

    while not value:

        start_position = recognize_notation(last_move)
        end_position = recognize_notation(last_move)

        value = play_move(start_position+end_position)





def play_move(move):
    url = f"https://lichess.org/api/board/game/{game_id}/move/{move}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        print(f"{move} played successfully.")
        engine.say(f"{move} played successfully.")
        return True
    else:
        print(f"Failed to play move. Status code: {response.status_code}")
        print(response.text)
        engine.say(response.text)
        return False





def stream_game_moves():
    url = f"https://lichess.org/api/board/game/stream/{game_id}"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    response = requests.get(url, headers=headers, stream=True)



    if response.status_code == 200:
        last_move = None
        for line in response.iter_lines():
            if line:
                game_data = line.decode("utf-8")
                game_json = json.loads(game_data)

                def check():
                    if game_json.get('status') == 'mate':
                        winner = game_json.get('winner', 'none')
                        if winner == 'white':
                            print("White player won the game.")
                            engine.say("White player won the game.")
                            engine.runAndWait()
                            sys.exit()

                        elif winner == 'black':
                            print("Black player won the game.")
                            engine.say("Black player won the game.")
                            engine.runAndWait()
                            sys.exit()


                    elif game_json.get('status') == 'resign':
                        winner = game_json.get('winner')
                        if winner == 'black':
                            print("White player resigned.")
                            engine.say("White player resigned.")
                            engine.runAndWait()
                            sys.exit()


                        elif winner == 'white':
                            print("Black player resigned.")
                            engine.say("Black player resigned.")
                            engine.runAndWait()
                            sys.exit()



                    elif game_json.get('status') == 'draw':
                        print("Game ended in a draw")
                        engine.say("Game ended in a draw")
                        engine.runAndWait()
                        sys.exit()

                if 'white' in game_json and 'black' in game_json:
                    if game_json['white'].get('name') == username:
                        color = 'white'
                    elif game_json['black'].get('name') == username:
                        color = 'black'
                    else:
                        color = 'unknown'

                if 'state' in game_json and 'moves' in game_json['state']:
                    moves = game_json['state']['moves']
                    moves_count = len(moves.split())
                    if moves_count > 0:
                        last_move = moves.split()[-1]
                    else:
                        last_move=None
                        
                elif 'moves' in game_json:
                    moves = game_json['moves']
                    moves_count = len(moves.split())
                    if moves_count > 0:
                        last_move = moves.split()[-1]
                    else:
                        last_move=None
                else:
                    continue

                if color=='white' and moves_count%2==0:
                    check()
                    print("Your turn")
                    print(f"Opponent played: {last_move}")
                    engine.say(f"Opponent played {last_move}, Your Turn")
                    engine.runAndWait()
                    move(last_move)

                
                elif color=='black' and moves_count%2==1:
                    check()
                    print("Your turn")
                    print(f"Opponent played: {last_move}")
                    engine.say(f"Opponent played {last_move}, Your Turn")
                    engine.runAndWait()
                    move(last_move)

                
                

    else:
        print(f"Error: {response.status_code} - {response.text}")





stream_game_moves()