import random
import streamlit as st

st.set_page_config(page_title="Grid Number Generator", layout="wide")
st.title("Grid Number Generator with Special Rules")

# ===============================
# USER INPUTS
# ===============================
TOTAL_SETS = st.number_input("Total sets:", min_value=1, value=5)
GRID_SIZE = st.number_input("Grid size (e.g., 5 for 5x5):", min_value=2, value=5)
SPECIAL_COUNT = st.number_input("How many special numbers to control?", min_value=0, value=1)

special_rules = []
for i in range(SPECIAL_COUNT):
    st.subheader(f"Special Number {i+1}")
    num = st.number_input(f"Special number:", key=f"special_num_{i}", value=5)
    repeat_sets = st.number_input(
    f"In how many sets {num} should appear (max 3 per set)?",
    key=f"repeat_{i}",
    min_value=1,
    max_value=1000,  # allow user to type any reasonable number
    value=1

    )
    special_rules.append({"number": num, "repeat_sets": repeat_sets})

OUTPUT_FILE = "multi_repeat_no_row_repeat_final.txt"

# ===============================
# NUMBER POOL
# ===============================
numbers_pool = [
    5,10,15,20,25,
    30,50,75,100,150,
    200,250,300,500,750,
    1000,1250,1500,1750,2000,
    3000,3500,4000,5000,
    5500,6000,6500,7000,7500,8000,
    8500,9000,9500,10000
]

# ===============================
# HELPER FUNCTION
# ===============================
def place_number_no_same_row(grid, num, times):
    rows_available = [r for r in range(len(grid)) if num not in grid[r] and any(cell is None for cell in grid[r])]
    times = min(times, len(rows_available))
    if times == 0:
        return
    chosen_rows = random.sample(rows_available, times)
    for r in chosen_rows:
        empty_cols = [c for c in range(len(grid[r])) if grid[r][c] is None]
        col = random.choice(empty_cols)
        grid[r][col] = num

# ===============================
# GENERATE SETS
# ===============================
if st.button("Generate Sets"):
    all_sets = []

    for set_index in range(TOTAL_SETS):
        grid = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]
        used_counts = {}

        # ----- Place special numbers -----
        for rule in special_rules:
            if set_index < rule["repeat_sets"]:
                num = rule["number"]
                place_number_no_same_row(grid, num, 3)
                used_counts[num] = 3

        # ----- Place one random number 2 times -----
        available_for_random_repeat = [n for n in numbers_pool if used_counts.get(n,0) <= 1]
        if available_for_random_repeat:
            random_num = random.choice(available_for_random_repeat)
            times_to_add = min(2, 3 - used_counts.get(random_num,0))
            place_number_no_same_row(grid, random_num, times_to_add)
            used_counts[random_num] = used_counts.get(random_num,0) + times_to_add

        # ----- Fill remaining cells safely -----
        remaining_cells = [(r,c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] is None]
        fill_pool = []
        for n in numbers_pool:
            current_count = used_counts.get(n,0)
            if current_count < 3:
                fill_pool += [n]*(3-current_count)

        if len(remaining_cells) > len(fill_pool):
            st.error(f"❌ Cannot fill set {set_index+1} without exceeding max 3 per number.")
            continue

        random.shuffle(fill_pool)
        for (r,c), n in zip(remaining_cells, fill_pool):
            grid[r][c] = n

        # Display set in Streamlit
        st.write(f"**Set {set_index+1}**")
        for row in grid:
            st.write(row)

        # Prepare for download
        block = "\n".join([",".join(map(str,row)) for row in grid])
        all_sets.append(block)

    if all_sets:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n\n".join(all_sets))

        st.success(f"✅ File saved locally as: {OUTPUT_FILE}")
        st.download_button("Download Generated Sets", data="\n\n".join(all_sets), file_name=OUTPUT_FILE)
