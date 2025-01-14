from base.assoc import Assoc
from base.constants import Team
from base.spymaster import BaseSpymaster

from openai import OpenAI

class MyAssoc(Assoc):
    def __init__(self):
        super().__init__()
        # Initialize your model/embedding here

    def getAssocs(self, pos, neg, topn):
        # Implement your word association logic
        pass

    def preprocess(self, w):
        # Implement any word preprocessing
        pass


class MySpymaster(BaseSpymaster):
    def __init__(self, assoc):
        super().__init__(assoc)
        self.client = OpenAI()

    def makeClue(self, board, team: Team):
        """
        Generate a clue for your team.

        Args:
            board: Dictionary with keys 'R' (red), 'U' (blue), 'N' (neutral), 'A'
                (assassin)
            team: Team.RED or Team.BLUE indicating your team

        Returns:
            tuple: ((clue_word, number_of_words), debug_info)
        """
        # Step 1: Extract all words from the game board into a set
        # This will be used later to ensure our clue isn't one of the board words
        board_words = set(
            [item for sublist in list(board.values()) for item in sublist]
        )

        # Step 2: Identify our team's words and the opponent's words based on team color
        # 'U' represents blue team, 'R' represents red team
        my_words = board["U" if team == Team.BLUE else "R"]
        opponent_words = board["R" if team == Team.BLUE else "U"]

        # Step 3: Create negative word list (words we want to avoid)
        # Combines opponent's words with neutral ('N') and assassin ('A') words
        # These are words our clue should NOT be similar to
        assassin = board["A"] 
        # Create positive word list (words we want to target)
        pos = my_words

        if len(pos) > 3 :
            num_words_to_guess = "2 or 3 specified words"
            num_words_to_guess2 = "2 or 3"
            prioritize_big_clues = "If possible, prioritize clues connecting 3 words."
        elif len(pos) >= 2 :
            num_words_to_guess = "2 specified words"
            num_words_to_guess2 = "2"
            prioritize_big_clues = ""
        else :
            num_words_to_guess = "to 1 specified word"
            num_words_to_guess2 = "to 1"
            prioritize_big_clues = ""

        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "developer", 
                    "content": f"You are playing the spymaster in the game Codenames. \
                                Your role is to generate single-word clues that connect \
                                {num_words_to_guess} while avoiding certain forbidden \
                                words. The clue should be lowercase, followed by a comma, \
                                the number of associated words, another comma, and the \
                                associated words separated by commas without spaces. Avoid \
                                extra text or explanation in your response.\n\n Example output:\n \
                                lime,3,pie,light,disease\n\n{prioritize_big_clues} Ensure the \
                                clue does not match or relate to any forbidden words before \
                                finalizing your response. There will be one assassin word. If \
                                your partner guesses the assassin from your clue you loose the game."
                },
                {
                    "role": "user",
                    "content": f"Connect {num_words_to_guess2} of the following words: \
                                {', '.join(pos)}. The clue must \
                                not relate to: {', '.join(opponent_words)}, and {assassin[0]}. \
                                The assassin word that your clue must not related to is {assassin[0]}"
                }
            ]
        )

        clue_info = completion.choices[0].message.content.split(',')
        return (clue_info[0], clue_info[1]), clue_info[2:]



