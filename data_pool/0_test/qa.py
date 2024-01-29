# Conbine different columns of the dataset into one column

import pandas as pd
import torch
from transformers import BertTokenizer, BertModel, BertForQuestionAnswering
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

import json
import logging
import os
import pickle
import subprocess
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from threading import Event
from time import time
from typing import List, Tuple, Dict

import numpy as np

import events as e
import settings as s
from agents import Agent, SequentialAgentBackend
from fallbacks import pygame
from items import Coin, Explosion, Bomb


# class Trophy:
#     coin_trophy = pygame.transform.smoothscale(pygame.image.load(s.ASSET_DIR / 'coin.png'), (15, 15))
#     suicide_trophy = pygame.transform.smoothscale(pygame.image.load(s.ASSET_DIR / 'explosion_0.png'), (15, 15))
#     time_trophy = pygame.image.load(s.ASSET_DIR / 'hourglass.png')


class GenericWorld:
    logger: logging.Logger

    running: bool = False
    step: int
    replay: Dict
    round_statistics: Dict

    agents: List[Agent]
    active_agents: List[Agent]
    arena: np.ndarray
    coins: List[Coin]
    bombs: List[Bomb]
    explosions: List[Explosion]

    round_id: str

    def __init__(self, args: WorldArgs):
        self.args = args
        self.setup_logging()

        self.colors = list(s.AGENT_COLORS)

        self.round = 0
        self.round_statistics = {}

        self.running = False

    class Trophy:
        coin_trophy = pygame.transform.smoothscale(pygame.image.load(s.ASSET_DIR / 'coin.png'), (15, 15))
        suicide_trophy = pygame.transform.smoothscale(pygame.image.load(s.ASSET_DIR / 'explosion_0.png'), (15, 15))
        time_trophy = pygame.image.load(s.ASSET_DIR / 'hourglass.png')


    def setup_logging(self):
        self.logger = logging.getLogger('BombeRLeWorld')
        self.logger.setLevel(s.LOG_GAME)
        handler = logging.FileHandler(f'{self.args.log_dir}/game.log', mode="w")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info('Initializing game world')

    def new_round(self):
        if self.running:
            self.logger.warning('New round requested while still running')
            self.end_round()

        new_round = self.round + 1
        self.logger.info(f'STARTING ROUND #{new_round}')

        def add_agent(self, agent_dir, name, train=False):
            assert len(self.agents) < s.MAX_AGENTS

            # if self.args.single_process:
            backend = SequentialAgentBackend(train, name, agent_dir)
            # else:
            # backend = ProcessAgentBackend(train, name, agent_dir)
            backend.start()

            color = self.colors.pop()
            agent = Agent(name, agent_dir, name, train, backend, color, color)
            self.agents.append(agent)
        # Bookkeeping
        self.step = 0
        self.bombs = []
        self.explosions = []

        if self.args.match_name is not None:
            match_prefix = f"{self.args.match_name} | "
        else:
            match_prefix = ""
        self.round_id = f'{match_prefix}Round {new_round:02d} ({datetime.now().strftime("%Y-%m-%d %H-%M-%S")})'

        # Arena with wall and crate layout
        self.arena, self.coins, self.active_agents = self.build_arena()

        for agent in self.active_agents:
            agent.start_round()

        self.replay = {
            'round': new_round,
            'arena': np.array(self.arena),
            'coins': [c.get_state() for c in self.coins],
            'agents': [a.get_state() for a in self.agents],
            'actions': dict([(a.name, []) for a in self.agents]),
            'permutations': []
        }

        self.round = new_round
        self.running = True

    def build_arena(self) -> Tuple[np.array, List[Coin], List[Agent]]:
        raise NotImplementedError()


    def add_agent(self, agent_dir, name, train=False):
        assert len(self.agents) < s.MAX_AGENTS

        # if self.args.single_process:
        backend = SequentialAgentBackend(train, name, agent_dir)
        # else:
        # backend = ProcessAgentBackend(train, name, agent_dir)
        backend.start()

        color = self.colors.pop()
        agent = Agent(name, agent_dir, name, train, backend, color, color)
        self.agents.append(agent)

    def tile_is_free(self, x, y):
        is_free = (self.arena[x, y] == 0)
        if is_free:
            for obstacle in self.bombs + self.active_agents:
                is_free = is_free and (obstacle.x != x or obstacle.y != y)
        return is_free

    def perform_agent_action(self, agent: Agent, action: str):
        # Perform the specified action if possible, wait otherwise
        if action == 'UP' and self.tile_is_free(agent.x, agent.y - 1):
            agent.y -= 1
            agent.add_event(e.MOVED_UP)
        elif action == 'DOWN' and self.tile_is_free(agent.x, agent.y + 1):
            agent.y += 1
            agent.add_event(e.MOVED_DOWN)
        elif action == 'LEFT' and self.tile_is_free(agent.x - 1, agent.y):
            agent.x -= 1
            agent.add_event(e.MOVED_LEFT)
        elif action == 'RIGHT' and self.tile_is_free(agent.x + 1, agent.y):
            agent.x += 1
            agent.add_event(e.MOVED_RIGHT)
        elif action == 'BOMB' and agent.bombs_left:
            self.logger.info(f'Agent <{agent.name}> drops bomb at {(agent.x, agent.y)}')
            self.bombs.append(Bomb((agent.x, agent.y), agent, s.BOMB_TIMER, s.BOMB_POWER, agent.bomb_sprite))
            agent.bombs_left = False
            agent.add_event(e.BOMB_DROPPED)
        elif action == 'WAIT':
            agent.add_event(e.WAITED)
        else:
            agent.add_event(e.INVALID_ACTION)

    def poll_and_run_agents(self):
        raise NotImplementedError()

    def send_game_events(self):
        pass

    def do_step(self, user_input='WAIT'):
        assert self.running

        self.step += 1
        self.logger.info(f'STARTING STEP {self.step}')

        self.user_input = user_input
        self.logger.debug(f'User input: {self.user_input}')

        self.poll_and_run_agents()

        # Progress world elements based
        self.collect_coins()
        self.update_explosions()
        self.update_bombs()
        self.evaluate_explosions()
        self.send_game_events()

        if self.time_to_stop():
            self.end_round()

    def collect_coins(self):
        for coin in self.coins:
            if coin.collectable:
                for a in self.active_agents:
                    if a.x == coin.x and a.y == coin.y:
                        coin.collectable = False
                        self.logger.info(f'Agent <{a.name}> picked up coin at {(a.x, a.y)} and receives 1 point')
                        a.update_score(s.REWARD_COIN)
                        a.add_event(e.COIN_COLLECTED)
                        a.trophies.append(Trophy.coin_trophy)

    def update_explosions(self):
        # Progress explosions
        remaining_explosions = []
        for explosion in self.explosions:
            explosion.timer -= 1
            if explosion.timer <= 0:
                explosion.next_stage()
                if explosion.stage == 1:
                    explosion.owner.bombs_left = True
            if explosion.stage is not None:
                remaining_explosions.append(explosion)
        self.explosions = remaining_explosions

    def update_bombs(self):
        """
        Count down bombs placed
        Explode bombs at zero timer.

        :return:
        """
        for bomb in self.bombs:
            if bomb.timer <= 0:
                # Explode when timer is finished
                self.logger.info(f'Agent <{bomb.owner.name}>\'s bomb at {(bomb.x, bomb.y)} explodes')
                bomb.owner.add_event(e.BOMB_EXPLODED)
                blast_coords = bomb.get_blast_coords(self.arena)

                # Clear crates
                for (x, y) in blast_coords:
                    if self.arena[x, y] == 1:
                        self.arena[x, y] = 0
                        bomb.owner.add_event(e.CRATE_DESTROYED)
                        # Maybe reveal a coin
                        for c in self.coins:
                            if (c.x, c.y) == (x, y):
                                c.collectable = True
                                self.logger.info(f'Coin found at {(x, y)}')
                                bomb.owner.add_event(e.COIN_FOUND)

                # Create explosion
                screen_coords = [(s.GRID_OFFSET[0] + s.GRID_SIZE * x, s.GRID_OFFSET[1] + s.GRID_SIZE * y) for (x, y) in
                                 blast_coords]
                self.explosions.append(Explosion(blast_coords, screen_coords, bomb.owner, s.EXPLOSION_TIMER))
                bomb.active = False
            else:
                # Progress countdown
                bomb.timer -= 1
        self.bombs = [b for b in self.bombs if b.active]

    def evaluate_explosions(self):
        # Explosions
        agents_hit = set()
        for explosion in self.explosions:
            # Kill agents
            if explosion.is_dangerous():
                for a in self.active_agents:
                    if (not a.dead) and (a.x, a.y) in explosion.blast_coords:
                        agents_hit.add(a)
                        # Note who killed whom, adjust scores
                        if a is explosion.owner:
                            self.logger.info(f'Agent <{a.name}> blown up by own bomb')
                            a.add_event(e.KILLED_SELF)
                            explosion.owner.trophies.append(Trophy.suicide_trophy)
                        else:
                            self.logger.info(f'Agent <{a.name}> blown up by agent <{explosion.owner.name}>\'s bomb')
                            self.logger.info(f'Agent <{explosion.owner.name}> receives 1 point')
                            explosion.owner.update_score(s.REWARD_KILL)
                            explosion.owner.add_event(e.KILLED_OPPONENT)
                            explosion.owner.trophies.append(pygame.transform.smoothscale(a.avatar, (15, 15)))

        # Remove hit agents
        for a in agents_hit:
            a.dead = True
            self.active_agents.remove(a)
            a.add_event(e.GOT_KILLED)
            for aa in self.active_agents:
                if aa is not a:
                    aa.add_event(e.OPPONENT_ELIMINATED)

    def end_round(self):
        if not self.running:
            raise ValueError('End-of-round requested while no round was running')
        # Wait in case there is still a game step running
        self.running = False

        for a in self.agents:
            a.note_stat("score", a.score)
            a.note_stat("rounds")
        self.round_statistics[self.round_id] = {
            "steps": self.step,
            **{key: sum(a.statistics[key] for a in self.agents) for key in ["coins", "kills", "suicides"]}
        }

    def time_to_stop(self):
        # Check round stopping criteria
        if len(self.active_agents) == 0:
            self.logger.info(f'No agent left alive, wrap up round')
            return True

        if (len(self.active_agents) == 1
                and (self.arena == 1).sum() == 0
                and all([not c.collectable for c in self.coins])
                and len(self.bombs) + len(self.explosions) == 0):
            self.logger.info(f'One agent left alive with nothing to do, wrap up round')
            return True

        if any(a.train for a in self.agents) and not self.args.continue_without_training:
            if not any([a.train for a in self.active_agents]):
                self.logger.info('No training agent left alive, wrap up round')
                return True

        if self.step >= s.MAX_STEPS:
            self.logger.info('Maximum number of steps reached, wrap up round')
            return True

        return False

    def end(self):
        if self.running:
            self.end_round()

        results = {'by_agent': {a.name: a.lifetime_statistics for a in self.agents}}
        for a in self.agents:
            results['by_agent'][a.name]['score'] = a.total_score
        results['by_round'] = self.round_statistics

        if self.args.save_stats is not False:
            if self.args.save_stats is not True:
                file_name = self.args.save_stats
            elif self.args.match_name is not None:
                file_name = f'results/{self.args.match_name}.json'
            else:
                file_name = f'results/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.json'

            name = Path(file_name)
            if not name.parent.exists():
                name.parent.mkdir(parents=True)
            with open(name, "w") as file:
                json.dump(results, file, indent=4, sort_keys=True)

# Read the original CSV file
df_part = pd.read_csv('articles.csv', index_col='PMID', usecols=['PMID', 'TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'])

# Create a new DataFrame with the desired structure
new_df = pd.DataFrame(index=df_part.index)

# Combine the information into a single column
new_df['Combined_Info'] = ('Title: ' + df_part['TI'].fillna('None') + '\n' +
    'Abstract: ' + df_part['AB'].fillna('None') + '\n' +
    'Authors: ' + df_part['FAU'].fillna('None') + '\n' +
    'Data of Publication: ' + df_part['DP'].fillna('None') + '\n' +
    'Terms or keywords associated with the article: ' + df_part['OT'].fillna('None') + '\n' +
    'Journal Title: ' + df_part['JT'].fillna('None') + '\n' +
    'Medical subject headings: ' + df_part['MH'].fillna('None')
)

# Save the new DataFrame to a CSV file
new_df.to_csv('combined_data.csv')

def split_csv(input_csv, output_prefix, chunk_size):
    # Read the large CSV file into a pandas DataFrame

    new_df['Combined_Info'] = (
        'Title: ' + df_part['TI'].fillna('None') + '\n' +
    'Abstract: ' + df_part['AB'].fillna('None') + '\n' +
    'Authors: ' + df_part['FAU'].fillna('None') + '\n' +
    'Data of Publication: ' + df_part['DP'].fillna('None') + '\n' +
    'Terms or keywords associated with the article: ' + df_part['OT'].fillna('None') + '\n' +
    'Journal Title: ' + df_part['JT'].fillna('None') + '\n' +
    'Medical subject headings: ' + df_part['MH'].fillna('None')
    )
    df = pd.read_csv(input_csv)

    # Determine the number of chunks needed
    num_chunks = (len(df) // chunk_size) + 1

    # Split the DataFrame into chunks
    chunks = [df[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

    # Save each chunk as a separate CSV file
    for i, chunk in enumerate(chunks):
        output_csv = f"{output_prefix}_{i + 1}.csv"
        chunk.to_csv(output_csv, index=False)
        print(f"Chunk {i + 1} saved to {output_csv}")

# Example usage
input_csv_path = 'data_1.csv'  # Replace with the path to your large CSV file
output_prefix = 'sub_data'  # Prefix for the output CSV files
chunk_size = 1000  # Number of rows per chunk

# split_csv(input_csv_path, output_prefix, chunk_size)
# Embedding the abstracts using BERT and saving them to a file


# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
def outer():
  print("I'm the outer function.")
  def inner():
    print("And I'm the inner function.")
  inner()

outer()
# Tokenize and encode the abstracts
def encode_abstracts_sliding_window(abstracts, window_size=512, stride=256):
    # def split_csv(input_csv=None, output_prefix=None, chunk_size=None):
    #     # Read the large CSV file into a pandas DataFrame
    #     print(" ")
        # df = pd.read_csv(input_csv)

        # # Determine the number of chunks needed
        # num_chunks = (len(df) // chunk_size) + 1

        # # Split the DataFrame into chunks
        # chunks = [df[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

        # # Save each chunk as a separate CSV file
        # for i, chunk in enumerate(chunks):
        #     output_csv = f"{output_prefix}_{i + 1}.csv"
        #     chunk.to_csv(output_csv, index=False)
        #     print(f"Chunk {i + 1} saved to {output_csv}")

    encoded_abstracts = []

    for abstract in tqdm(abstracts, desc="Encoding Abstracts", unit="abstract"):
        tokens = tokenizer.tokenize(abstract)
        total_length = len(tokens)

        # Determine the number of overlapping windows
        num_windows = abs(total_length - window_size) // stride + 1

        for i in range(0, num_windows * stride, stride):
            # Extract a window of tokens
            window_tokens = tokens[i:i + window_size]

            # Convert tokens back to a string
            window_text = tokenizer.convert_tokens_to_string(window_tokens)

            # Tokenize and encode the window
            inputs = tokenizer(window_text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)

            encoded_abstracts.append(outputs.last_hidden_state.mean(dim=1))

    if not encoded_abstracts:
        print("No encoded abstracts found.")
    return torch.cat(encoded_abstracts, dim=0)


# Function to save encoded abstracts
def save_encoded_abstracts(encoded_abstracts, filename):
    torch.save(encoded_abstracts, filename)

# Function to load encoded abstracts
def load_encoded_abstracts(filename):
    return torch.load(filename)

# Example: Load, encode, and save each part separately
for i in tqdm(range(1, 11), desc="Processing Parts", unit="part"):
    file_path = f'sub_data_{i}.csv'
    df_part1 = pd.read_csv(file_path)

    # Encode abstracts
    encoded_abstracts_part1 = encode_abstracts_sliding_window(df_part1['Combined_Info'])

    # Save encoded abstracts
    save_encoded_abstracts(encoded_abstracts_part1, f'encoded_data_part_{i}.pt')

# Load and concatenate encoded abstracts from all parts
encoded_abstracts_parts = []
for i in tqdm(range(1, 11), desc="Loading Parts", unit="part"):
    encoded_abstracts_part = load_encoded_abstracts(f'encoded_data_part_{i}.pt')
    encoded_abstracts_parts.append(encoded_abstracts_part)

# Concatenate the parts
encoded_abstracts1 = torch.cat(encoded_abstracts_parts, dim=0)

# Save the encoded_abstracts tensor
torch.save(encoded_abstracts1, 'encoded_data.pt')

# Load pre-trained BERT model and tokenizer
qa_model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
qa_tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

# Function to retrieve top k similar abstracts
def retrieve_top_k_abstracts(query, abstracts, df, k=5):
    # Encode the query using the sliding window approach (as before)
    query_embedding = encode_abstracts_sliding_window([query])
    
    # Calculate cosine similarity between the query and encoded abstracts
    similarities = cosine_similarity(query_embedding, abstracts)
    
    # Get the indices of the top k most similar abstracts
    top_k_indices = similarities.argsort()[0, -k:][::-1]

    if len(top_k_indices) == 0:
        print("No matching abstracts found.")
        return []

    # Print some information for debugging
    print("Top k PMIDs:", df.index[top_k_indices].tolist())
    print("Abstract lengths:", [len(df.loc[pmid, 'Combined_Info']) for pmid in df.index[top_k_indices]])

    return top_k_indices


# Function to generate answers using the QA model
def generate_answers(question, abstracts, df):
    answers = []

    for index in abstracts:
        # Get the PMID
        pmid = df.index[index]

        # Get the abstract text
        abstract_text = df.loc[pmid, 'Combined_Info']

        # Tokenize and encode the question and abstract
        inputs = qa_tokenizer(question, abstract_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Perform inference with the QA model
        with torch.no_grad():
            outputs = qa_model(**inputs)

        # Get the predicted answer
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        answer = qa_tokenizer.convert_tokens_to_string(qa_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

        answers.append(answer)

    return answers

# Using PMID as the index column
df_part3 = pd.read_csv('data_1.csv', index_col='PMID')
# df_part = pd.read_csv('articles.csv', index_col='PMID', usecols=['TI', 'AB', 'FAU', 'DP', 'OT', 'JT', 'MH'])

# Example usage
encoded_abstracts = load_encoded_abstracts('encoded_data.pt')
question = "what is Artificial Intelligence?"
top_k_abstracts = retrieve_top_k_abstracts(question, encoded_abstracts, df_part3, k=5)

# Print the top 5 similar abstracts
print("Top 5 Similar Abstracts:")
for index in top_k_abstracts:
    pmid = df_part3.index[index]
    print("PMID:", pmid)
    print("Abstract:", df_part3.loc[pmid, 'Combined_Info'])

answers = generate_answers(question, top_k_abstracts, df_part3)

# Display the generated answers
print("\nGenerated Answers:")
for answer in answers:
    print(answer)

if __name__ == "__main__":
    trophy = Trophy()
