import streamlit as st
from itertools import product
from collections import defaultdict
import nltk

# --- Setup NLTK word list (load once, cache) ---
@st.cache_resource
def load_dict():
    nltk.download("words")
    from nltk.corpus import words
    word_list = set(w.lower() for w in words.words())
    prefixes = set()
    for w in word_list:
        for i in range(1, len(w)):
            prefixes.add(w[:i])
    return word_list, prefixes

WORD_LIST, PREFIXES = load_dict()


# --- Word validation ---
def is_valid_word(word):
    return word in WORD_LIST


# --- Get neighbors (8 directions) ---
def neighbors(r, c, rows, cols):
    for dr, dc in product([-1, 0, 1], repeat=2):
        if dr == dc == 0:
            continue
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


# --- DFS with prefix pruning ---
def dfs(path, board, found, max_len):
    rows, cols = len(board), len(board[0])
    r, c = path[-1]
    word = "".join(board[pr][pc] for pr, pc in path).lower()

    # prune search if not a valid prefix
    if word not in PREFIXES and word not in WORD_LIST:
        return

    # record valid word
    if len(word) >= 4 and is_valid_word(word):
        found.add(word.upper())

    if len(path) < max_len:
        for nr, nc in neighbors(r, c, rows, cols):
            if (nr, nc) not in path:
                dfs(path + [(nr, nc)], board, found, max_len)


# --- Search whole board ---
def search_board(board, max_word_length=12):
    found = set()
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            dfs([(r, c)], board, found, max_word_length)
    return found


# --- Group words by length ---
def group_by_length(words):
    grouped = defaultdict(list)
    for word in words:
        grouped[len(word)].append(word)
    return dict(sorted(grouped.items()))


# --- Streamlit UI ---
st.title("🔤 Boggle Word Finder")

st.markdown("Enter letters for each cell. Only A-Z letters allowed.")

# --- Choose board size ---
board_size = st.number_input("Board size (e.g. 4 for 4x4):", min_value=2, max_value=10, value=4, step=1)

# --- Input grid ---
board = []
for i in range(board_size):
    row = []
    cols = st.columns(board_size)
    for j in range(board_size):
        cell = cols[j].text_input(f"({i+1},{j+1})", max_chars=1, key=f"cell_{i}_{j}")
        row.append(cell.strip().upper() if cell else "")
    board.append(row)

# --- Solve button ---
if st.button("🧠 Solve"):
    # Check board validity
    if any("" in row for row in board):
        st.error("Please fill in all cells with letters.")
    else:
        st.info("Solving... Please wait.")
        words_found = search_board(board, max_word_length=board_size * board_size)
        grouped = group_by_length(words_found)

        if not grouped:
            st.warning("No valid words found.")
        else:
            st.success(f"Found {sum(len(v) for v in grouped.values())} valid words!")

            for length, words in grouped.items():
                st.subheader(f"📏 {length}-letter words ({len(words)} found)")
                st.write(", ".join(sorted(words)))
