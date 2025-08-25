import streamlit as st
from itertools import product
from nltk.corpus import wordnet as wn
from collections import defaultdict

# --- Setup WordNet (make sure it's downloaded on first run) ---
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')


# --- Word validation ---
def is_valid_word(word):
    return bool(wn.synsets(word.lower()))


# --- Get neighbors (8 directions) ---
def neighbors(r, c, rows, cols):
    for dr, dc in product([-1, 0, 1], repeat=2):
        if dr == dc == 0:
            continue
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc


# --- DFS search ---
def dfs(path, board, max_len):
    rows, cols = len(board), len(board[0])
    r, c = path[-1]
    word = "".join(board[pr][pc] for pr, pc in path)
    if len(word) >= 4:
        yield word
    if len(path) < max_len:
        for nr, nc in neighbors(r, c, rows, cols):
            if (nr, nc) not in path:
                yield from dfs(path + [(nr, nc)], board, max_len)


# --- Search board ---
def search_board(board, max_word_length=12):
    found = set()
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            for w in dfs([(r, c)], board, max_word_length):
                if is_valid_word(w):
                    found.add(w.upper())
    return found


# --- Group words by length ---
def group_by_length(words):
    grouped = defaultdict(list)
    for word in words:
        grouped[len(word)].append(word)
    return dict(sorted(grouped.items()))


# --- Streamlit UI ---
st.title("🔤 Boggle Word Finder with WordNet")

st.markdown("Enter letters for each cell. Only A-Z letters allowed. Case-insensitive.")

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
