import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import seaborn as sns
import datetime


def adjust_positions_old(data, separation=2):
    # Extract names and goals from data
    names = list(data.keys())
    goals = [data[name]['goal'] for name in names]
    # Sort names and goals based on goals in descending order
    sorted_indices = sorted(range(len(goals)),
                            key=lambda k: goals[k], reverse=True)
    sorted_names = [names[i] for i in sorted_indices]
    sorted_goals = [goals[i] for i in sorted_indices]
    # Initialize previous y-position to the maximum possible y-position
    prev_y = max(goals)
    # Initialize dictionary to hold new y-positions
    new_positions = {}
    # For each name, adjust y-position based on required separation
    for name, goal in zip(sorted_names, sorted_goals):
        if name == sorted_names[0]:
            new_y = goal
        elif prev_y - goal < separation:
            new_y = prev_y - separation
        else:
            new_y = goal
        new_positions[name] = new_y
        prev_y = new_y
    return new_positions



def weekly_plot_old(data, weeks, title=None, save=False):
    # Initialize variables

    weeks += 1 # Because I want to start with week 0
    names = list(data.keys())
    num_lines = len(names)
    goals = np.array([data[name]['goal'] for name in names])
    progress = np.array([sum(data[name]['weekly_progress']) for name in names])
    weekly_progress = [[0] + data[name]['weekly_progress'] for name in names]
    percent_completed = progress / goals * 100

    colors = sns.color_palette("husl", num_lines)

    ################################################################################################
    # Plotting

    fig, ax = plt.subplots(2, 1, figsize=(12, 10))

    # Subplot 1 (top) ##############################################################################

    ax[0].bar(names, [100]*len(names),color=colors, alpha=0.4, label='Goal')
    ax[0].bar(names, percent_completed, color=colors, label='Current Progress')
    
    # Goal & Progress Text 
    for i in range(len(names)):
        ax[0].text(i, percent_completed[i], str(progress[i]), color='black',
                   ha='center', va='bottom', fontweight='bold') # Progress label
        if percent_completed[i] < 100: # Goal label
            ax[0].text(i, 100, str(goals[i]), color='black',
                       ha='center', va='bottom', fontweight='bold')

    # Subplot 2 (bottom) ###########################################################################
    new_positions = adjust_positions_old(data, separation=3) # rate label locations
    for i in range(len(names)):

        # Line Plot ############################################################
        cum_progress = np.cumsum(weekly_progress[i])
        if len(weekly_progress[0]) == weeks: # plot star points on last week
            ax[1].plot(cum_progress, c=colors[i], label=names[i],
                       marker='o', alpha=0.5)
            ax[1].scatter(weeks-1, cum_progress[-1], c=colors[i], s=150,
                          alpha=0.5, marker='*')
        else:
            ax[1].plot(cum_progress, c=colors[i], label=names[i],
                       marker='o', alpha=0.5)

        # Projection Line 
        remaining = goals[i] - progress[i] # remaining # of exercises for goal
        remaining_weeks = weeks - len(weekly_progress[i])
        if remaining_weeks > 0:
            # Calculate require rates to achieve goal
            start_rate = goals[i] / (weeks-1)
            req_rate = remaining / remaining_weeks
            projection = [cum_progress[-1] + req_rate * j \
                          for j in range(remaining_weeks + 1)]
            prog_lbl_color = 'r' if req_rate > start_rate else 'k'
            # Plot projection line
            ax[1].plot(range(len(weekly_progress[i]) - 1, weeks),  projection,
                       c=colors[i], linestyle='dashed', alpha=0.5)
            # Plot rate labels
            y = new_positions[names[i]]
            ax[1].text(weeks, y, f'{req_rate:.1f}/wk\n({names[i]})', ha='right',
                       va='center', alpha=0.5, color=prog_lbl_color, fontsize=9)

    ################################################################################################
    # Plot formatting & Saving
    ################################################################################################
    ax[0].set_ylabel('Percent Completed (%)')
    ax[0].set_title('Current Progress vs Goal')

    if remaining_weeks == 0:
        ax[1].legend()
    ax[1].yaxis.set_minor_locator(tck.AutoMinorLocator())
    ax[1].grid(which='both', alpha=0.2)
    ax[1].set_xticks(range(weeks))
    ax[1].set_xticklabels(range(0, weeks))
    ax[1].set_xlabel('Week')
    ax[1].set_ylabel('Cumulative Exercises')
    ax[1].set_title('Weekly Progress and Projections')

    if title is not None:
            plt.suptitle(title, fontsize=24)

    plt.tight_layout()
    plt.show()
    now = datetime.datetime.now()
    if save:
        fig.savefig(f"{now.strftime('%d_%m_%Y')}_current_progress.png",
                    dpi=600, bbox_inches='tight')



    return fig, ax