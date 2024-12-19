import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend

import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import database_manager as dbm
import os

# Function to fetch data for plotting win rate vs pick rate for a specific role
def fetch_plot_data(role, min_games=0):
    query = f"""
        SELECT championName,
               COUNT(*) as total_games,
               100.0 * SUM(CASE WHEN win = 1 THEN 1 ELSE 0 END) / COUNT(*) AS win_rate
        FROM participants
        WHERE individualPosition = '{role}'
        GROUP BY championName
        HAVING COUNT(*) >= {min_games}
        ORDER BY total_games DESC;
    """
    # Get data from the database using the database manager
    data = dbm.get_data(query)

    # Calculate pick rate for each champion in the role
    total_games = data['total_games'].sum()
    data['pick_rate'] = (data['total_games'] / total_games) * 100

    return data

def plot_role_data(role, min_games=0):
    # Fetch data for the specified role
    data = fetch_plot_data(role, min_games)

    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the full path to the assets directory
    assets_dir = os.path.join(current_dir, "assets")

    # Ensure the assets directory exists
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # Define the full path for the champion images directory
    champion_images_dir = os.path.join(assets_dir, "champion_images")

    # Define the full path for the plot file
    plot_path = os.path.join(assets_dir, f"{role.lower()}_plot.png")

    # Create a scatter plot with champion images as data points
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title(f"{role} Role: Pick Rate vs Win Rate (Minimum {min_games} Games)")
    ax.set_xlabel("Win Rate (%)")
    ax.set_ylabel("Pick Rate (%)")
    ax.grid(True)

    # Scatter plot for win rate vs pick rate (note the axes are swapped)
    ax.scatter(data['win_rate'], data['pick_rate'], alpha=0.5)

    # Iterate over the champions and plot each one with its image
    for _, row in data.iterrows():
        champion_name = row['championName']
        win_rate = row['win_rate']
        pick_rate = row['pick_rate']

        # Construct the full path to the champion image
        image_path = os.path.join(champion_images_dir, f"{champion_name}.png")
        if os.path.exists(image_path):
            img = Image.open(image_path)

            # Create an OffsetImage object
            im = OffsetImage(img, zoom=0.15)  # Adjust zoom as needed for better visibility
            ab = AnnotationBbox(im, (win_rate, pick_rate), frameon=False, pad=0.1)
            ax.add_artist(ab)

    # Save the plot to the assets directory
    plt.savefig(plot_path, format="png", bbox_inches='tight', dpi=300)
    plt.close(fig)

    return plot_path