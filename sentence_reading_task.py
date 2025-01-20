from psychopy import monitors, visual, core, event, logging, prefs, gui
import os
import numpy as np
import time
import serial
import serial.tools.list_ports
import random
import threading
import csv
import queue

# -----------------
# Session_settings
# -----------------
# If scanning is set to 0, the script does not monitor incoming triggers
scanning = 1

if scanning == 1:
    COM_port = 'COM8'
    baud_rate = 57600
    trigger_byte_codes = [73, 53] # byte equivalents to the ascii characters 's' and 'S'
    port_timeout = 0.01
    
    ports_available = [port.device for port in serial.tools.list_ports.comports()]
    
    if COM_port not in ports_available:
        print(f"Serial port {COM_port} not found!")
        core.quit()

# Open a dialog to request a session number
session_info = {'Session Number': ''}
dialog = gui.DlgFromDict(session_info, title='Session Information')

# Check if the dialog was cancelled
session_number = 0

if dialog.OK:
    session_number = str(session_info['Session Number'])
    print(f'Session Number: {session_number}')
else:
    print('User cancelled the dialog.')

# ----------------
# Screen settings
# ----------------

# Get all avaliable screens
monitor_ids = monitors.getAllMonitors()
print("Detected monitors:")
print(", ".join(f"{i}: {monitor_id}" for i, monitor_id in enumerate(monitor_ids)))

monitor_id = 0 # change based on the detected monitors printed to display on a different monitor

# Create a window on the desired monitor
win = visual.Window(
    fullscr=True, screen=monitor_id, 
    color=[0, 0, 0], units='pix',
    allowGUI=False, winType='pyglet')

# Get window dimensions
screen_height_pix = win.size[1]
screen_width_pix = win.size[0]

# Hide cursor on the window created
win.mouseVisible = False

# Color settings
white = 1
black = -1
grey = 0

# --------------
# Text settings
# --------------

# Text size
base_text_size = round(screen_height_pix / 30)
condition_cue_text_size = round(base_text_size*1.4)
text_wrap_width = round(screen_width_pix / 2)

# Create a fixation cross object
fixation_cross_size = round(screen_height_pix / 20)
fixation = visual.TextStim(win, text='+', height=fixation_cross_size, color=black)

# ---------------------
# Serial port settings
# ---------------------

if scanning == 1:
    # Create a thread-safe queue to continuously store subsequent triggers
    trigger_queue = queue.Queue()

    # Set a trigger .csv filename with the session number
    csv_filename = "session_" + session_number + "_triggers.csv"

    # Define the stop monitoring event to close the serial port
    stop_event = threading.Event()

    # Function to run in the background thread for trigger monitoring
    def monitor_serial(port, baud, timeout, queue, stop_event):
        try:
            ser = serial.Serial(port, baud, timeout=timeout)
            print(f"Serial port {port} opened.")
            while not stop_event.is_set():
                if ser.in_waiting > 0:
                    incoming_data = ser.read()
                    incoming_code = int.from_bytes(incoming_data, byteorder='big')
                    timestamp = time.time_ns()  # Record the time of the trigger
                    print(f"Trigger {incoming_code} received at {timestamp}.")
                    queue.put((incoming_code, timestamp))  # Add data and timestamp to the queue
            ser.close()
            print(f"Serial port {port} closed.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    # Start the background thread
    serial_thread = threading.Thread(
        target=monitor_serial,
        args=(COM_port, baud_rate, port_timeout, trigger_queue, stop_event),
        daemon=True
    )
    serial_thread.start()

    # Prepare the CSV file, adding headers if it doesn't exist
    # If there is a file access error (e.g. the file is open), raise an error and quit the experiment
    try:
        with open(csv_filename, 'a', newline='') as trigger_csvfile:
            trigger_csv_writer = csv.writer(trigger_csvfile)
            # Write header if the file is empty
            if trigger_csvfile.tell() == 0:
                trigger_csv_writer.writerow(["trigger_event", "abs_time"])
    except IOError as e:
        print(f"File access error: {e}")
        core.quit()

# ----------------------------
# Stimulus and design settings
# ----------------------------

sentence_list_A = [
    "The cat slept quietly on the sunny windowsill.",
    "A cool breeze drifted through the open window.",
    "The clock ticked softly in the empty room.",
    "She opened the book and began to read."
    ]

sentence_list_B = [
    "A dog barked in the distance, breaking the silence.",
    "He poured a cup of coffee and sat by the fire.",
    "The rain pattered lightly against the roof tiles.",
    "She smiled as she walked through the blooming garden."
    ]

sentence_list_C = [
    "A bird chirped cheerfully from a nearby tree branch.",
    "The sun rose slowly, painting the sky with gold.",
    "He tied his shoes and headed out for a morning jog.",
    "A child laughed joyfully while chasing a butterfly."
    ]

sentence_list_D = [
    "She brewed a pot of tea and settled on the couch.",
    "The mountains stood tall against the clear blue sky.",
    "He picked up the guitar and strummed a soft melody.",
    "The mist rose slowly, shrouding the valley in gray."
    ]

sentence_list_E = [
    "The warm sunlight filtered through the swaying branches.",
    "The ice cream melted quickly under the hot sun.",
    "He gazed at the stars, dreaming of distant worlds.",
    "The baker decorated cakes with colorful frosting."
    ]

sentence_list_F = [
    "The wind carried the scent of salt from the sea.",
    "A cat stretched lazily in the warm sunlight.",
    "She folded the letter and placed it in the drawer.",
    "He laced up his boots and headed for the trail."
    ]

sentence_list_G = [
    "A steaming bowl of soup sat on the edge of the table.",
    "The smell of fresh bread wafted through the bakery.",
    "A violin rested quietly on the wooden stand.",
    "A soft melody drifted from the strings of the harp."
    ]

sentence_list_H = [
    "A patch of moss grew thickly on the weathered stone.",
    "A kite soared brightly against the pale evening clouds.",
    "The blacksmith hammered a horseshoe on the anvil.",
    "The traveler traced the ancient map with her fingertip."
    ]

sentence_list_I = [
    "The jeweler polished the gemstone until it sparkled.",
    "A crescent moon rose above the jagged mountain peaks.",
    "The cyclist leaned forward as she raced down the hill.",
    "A red apple rolled off the counter and onto the floor."
    ]

sentence_list_J = [
    "A kaleidoscope of colors shifted within the stained-glass.",
    "A cluster of grapes hung low on the vine.",
    "The engineer tightened a bolt on the humming machine.",
    "The mechanic wiped his greasy hands on a faded rag."
    ]

stimulus_list_A = [sentence_list_A, sentence_list_B, sentence_list_C, sentence_list_D, sentence_list_E, sentence_list_F, sentence_list_G, sentence_list_H, sentence_list_I, sentence_list_J]
stimulus_list_B = [stimulus_list_A[i + 1] if i % 2 == 0 else stimulus_list_A[i - 1] for i in range(len(stimulus_list_A))]
full_stimulus_list = stimulus_list_A + stimulus_list_B

n_blocks = 20
reading_conditions = [1 if i % 2 == 0 else 2 for i in range(n_blocks)] # alternating between conditions every other block
trials_per_block = 4

# ---------------------
# Task timing settings
# ---------------------

instruction_screen_duration = 5
block_cue_duration = 1
trial_duration = 4
fixation_cross_duration = 0.5
block_rest_screen_duration = 17 # seconds before the 3-second countdown

if session_number != 0:
    time_log_filename = f"session_{session_number}_sentence_reading_log.csv"
else:
    time_log_filename = 'sentence_reading_log.csv'

# -----------
# Experiment
# -----------

# Open/create a CSV file to store task timing data
# Run the task with the log file open
with open(time_log_filename, 'a', newline='') as trial_csvfile:
    
    event_columns = ['event','abs_time']
    timing_writer = csv.writer(trial_csvfile)
    
    # If the file is empty, add the column headers
    if trial_csvfile.tell() == 0:
        timing_writer.writerow(event_columns)
    
    # Present the instruction screen
    instruction_text = ("Sentence reading task\n\n"
                        "Before each block, you will see a cue:\n\n"
                        "If you see 'Out Loud', read the sentences out loud.\n\n"
                        "If you see 'Silently', read the sentences in your head.")
                        
    instructions_screen = visual.TextStim(win, text=instruction_text, height=base_text_size, color=black, wrapWidth=text_wrap_width, anchorHoriz='center')
    instructions_screen.draw()
    win.flip()
    
    # Store instruction screen timings
    instruction_screen_display = time.time_ns()
    timing_writer.writerow(["instruction_screen_display", instruction_screen_display])
    trial_csvfile.flush()
    
    core.wait(instruction_screen_duration)
    
    # If scanning wait for a scanning trigger to be present
    if scanning == 1:
        
        received_target_code = False
        
        while received_target_code is False:
            
            # Allow the experimenter to quit the experiment on this screen
            if event.getKeys(['escape']):
                print("Experiment terminated by user.")
                
                # Close the COM port if listening for scanner triggers
                if scanning == 1:
                    stop_event.set()
                    
                # Exit the experiment
                win.close()
                core.quit()
            
            # Loop through the trigger queue
            while not trigger_queue.empty():
                incoming_code, timestamp = trigger_queue.get()

                # Check if the incoming code is in the list of target codes
                if int(incoming_code) in(trigger_byte_codes):
                    scanner_start_time = timestamp
                    timing_writer.writerow(["scanner_start_time", scanner_start_time])
                    trial_csvfile.flush()
                    received_target_code = True
                    print(f"First trigger code {incoming_code} received at {timestamp}. Starting task.")
                    break
    
    # Start with a rest block
    rest_text = visual.TextStim(win, text="Rest", height=condition_cue_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
    rest_text.draw()
    win.flip()
    rest_screen_display_time = time.time_ns()
    rest_screen_display_event_text = 'initial_rest_screen_display'
    timing_writer.writerow([rest_screen_display_event_text, rest_screen_display_time])
    trial_csvfile.flush()
            
    # Check for user input (including escape key)
    # Exit the trial loop if escape was pressed
    keys = event.getKeys()
    if 'escape' in keys:  # Check if the escape key is pressed
        print("Experiment terminated by user.")
                
        # Close the COM port if listening for scanner triggers
        if scanning == 1:
            stop_event.set()
                    
        # Exit the experiment
        win.close()
        core.quit()

    core.wait(block_rest_screen_duration)

    for countdown_n in range(3, 0, -1):
        if countdown_n == 1:
            countdown_text = f"Next block in {countdown_n} second"
        else:
            countdown_text = f"Next block in {countdown_n} seconds"
        countdown_stim = visual.TextStim(win, text=countdown_text, height=base_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
        countdown_stim.draw()
        win.flip()
        keys = event.getKeys()
        core.wait(1)

    # Block loop
    terminate_experiment = False

    for current_block in range(n_blocks):
        
        if terminate_experiment:
            break
        
        block_start_time =  time.time_ns()
        block_start_time_event_text = 'block_{}_start_time'.format(current_block+1)
        timing_writer.writerow([block_start_time_event_text, block_start_time])
        trial_csvfile.flush()
        
        # Block information
        block_condition = reading_conditions[current_block]
        block_sentences =full_stimulus_list[current_block]
        
        # Randomize the order of sentence presentation within the block
        indices = list(range(len(block_sentences)))
        shuffled_indices = random.sample(indices, len(indices))
        block_sentences_randomized = [block_sentences[i] for i in shuffled_indices]
        
        # Condition cue
        if block_condition == 1:
            cue_text = "Out Loud"
        else:
            cue_text = "Silently"
        
        cue_screen = visual.TextStim(win, text=cue_text, height=condition_cue_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
        cue_screen.draw()
        win.flip()
        
        # Store cue presentation timing
        block_cue_display =  time.time_ns()
        block_cue_display_event_text = 'block_{}_cue_display'.format(current_block+1)
        timing_writer.writerow([block_cue_display_event_text, block_cue_display])
        trial_csvfile.flush()
        
        keys = event.getKeys()
        if 'escape' in keys:  # Check if the escape key is pressed
            print("Escape key pressed. Exiting the experiment.")
            terminate_experiment = True
            break
        
        core.wait(block_cue_duration)
        
        # Trial loop
        for current_trial in range(trials_per_block):
            
            if terminate_experiment:
                break
            
            trial_sentence = block_sentences_randomized[current_trial]

            # Display sentence for 4s
            trial_text = visual.TextStim(win, text=trial_sentence, height=base_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
            trial_text.draw()
            win.flip()
            trial_display_time =  time.time_ns()
            trial_display_event_text = 'block_{0}_trial_{1}_display'.format(current_block+1, current_trial+1)
            timing_writer.writerow([trial_display_event_text, trial_display_time])
            trial_csvfile.flush()
            
            # Check for user input (including escape key)
            # Exit the trial loop if escape was pressed
            keys = event.getKeys()
            if 'escape' in keys:  # Check if the escape key is pressed
                print("Escape key pressed. Exiting the experiment.")
                terminate_experiment = True
                break  # Exit the loop and end the experiment
                
            core.wait(trial_duration)
            
            if scanning == 1:
                # Sample triggers from the queue and write to the CSV file
                while not trigger_queue.empty():
                    trigger, timestamp = trigger_queue.get()
                    # Write the trigger and timestamp to the CSV file
                    with open(csv_filename, 'a', newline='') as triggers_csvfile:
                        trigger_csv_writer = csv.writer(triggers_csvfile)
                        trigger_csv_writer.writerow([trigger, timestamp])
            
            # Display a fixation cross between sentences for 0.5s
            fixation.draw()
            fixation_display_time = time.time_ns()
            fixation_display_event_text = 'block_{0}_trial_{1}_fixation'.format(current_block+1, current_trial+1)
            timing_writer.writerow([fixation_display_event_text, fixation_display_time])
            trial_csvfile.flush()
            win.flip()
            core.wait(fixation_cross_duration)

        # Check if the escape key was pressed during one of the trials
        if terminate_experiment:
            break

        # Rest screen
        if current_block < n_blocks - 1:
            rest_text.draw()
            win.flip()
            rest_screen_display_time = time.time_ns()
            rest_screen_display_event_text = 'block_{}_rest_screen_display'.format(current_block+1)
            timing_writer.writerow([rest_screen_display_event_text, rest_screen_display_time])
            trial_csvfile.flush()
            
            # Check for user input (including escape key)
            # Exit the trial loop if escape was pressed
            keys = event.getKeys()
            if 'escape' in keys:  # Check if the escape key is pressed
                print("Escape key pressed. Exiting the experiment.")
                terminate_experiment = True
                break  # Exit the loop and end the experiment
            
            core.wait(block_rest_screen_duration)

            # Rest countdown
            for countdown_n in range(3, 0, -1):
                if countdown_n == 1:
                    countdown_text = f"Next block in {countdown_n} second"
                else:
                    countdown_text = f"Next block in {countdown_n} seconds"
                countdown_stim = visual.TextStim(win, text=countdown_text, height=base_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
                countdown_stim.draw()
                win.flip()
                keys = event.getKeys()
                if 'escape' in keys:  # Check if the escape key is pressed
                    print("Escape key pressed. Exiting the experiment.")
                    break  # Exit the loop and end the experiment
                core.wait(1)


    # End of experiment screen
    end_text = "End of the experiment.\n\nThe experiment will close automatically in a few seconds."
    end_screen = visual.TextStim(win, text=end_text, height=base_text_size, color=black, anchorHoriz='center', wrapWidth=text_wrap_width)
    end_screen.draw()
    win.flip()
    end_screen_display_time = time.time_ns()
    timing_writer.writerow(["end_screen_display", end_screen_display_time])
    trial_csvfile.flush()
    core.wait(2)

if scanning == 1:
    # Sample triggers from the queue and write to the CSV file
    while not trigger_queue.empty():
        trigger, timestamp = trigger_queue.get()
        # Write the trigger and timestamp to the CSV file
        with open(csv_filename, 'a', newline='') as triggers_csvfile:
            trigger_csv_writer = csv.writer(triggers_csvfile)
            trigger_csv_writer.writerow([trigger, timestamp])

# Cleanup
stop_event.set()
win.close()
core.quit()
