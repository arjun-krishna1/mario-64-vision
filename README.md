# Mario 64 Vision
- Playing Super Mario 64 with GPT-4V
- For this reason: https://twitter.com/realGeorgeHotz/status/1758451210892329127

https://github.com/arjun-krishna1/mario-64-vision/assets/45014214/3a8379fb-2614-4c29-a27e-dbfcc70546cd

## Algorithm
1. capture game output screenshot
2. Ask following questions:
	- What objects are in the vicinity of Mario
	- What are the hazards located relative to Mario?
3. Is there a star (objective) visible?
4. What paths or routes are available to where the star could be?
5. What is the safest route from Mario's current position to the desired location?
6. Are there any interactive elements (e.g., blocks, switches) in the scene? What do they do?

7. Based on the current game state, what would be the best next move? THink step by step and carefully
answers to all questions
last 10 moves

## IMPROVEMENTS
- Run LLaVa and ollama locally to reduce action latency
- Create long-term plans (not just next move)
- If stuck take a 360 degree look, do a scout loop
