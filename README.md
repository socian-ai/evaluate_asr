# Intro
The script transcribes audio files in a given directory, calculates WER and generates an HTML report containing diffs, WER etc.

# Setup 
1. It supports only Python3. First install Python3 if not already installed.
2. Install virtualenv if not already installed. Run `python3 -m pip install --user virtualenv`
3. Create a virtual environment for the script. Navigate to the cloned directory and run `python3 -m virtualenv --python=python3 venv` . 
4. Install Python package dependencies. `python3 -m pip install -r requirements.txt`
Now you are ready to run the script.

# How to run
Before running the script, activate the created virtualenv using `source venv/bin/activate` (assuming you are in the repository directory where you cloned it). 

## Input params
- input-dir: The directory where your audio files and their corresponding ground truth transcripts live. Audio files and transcripts must use same filename. For example, audio1.wav file's transcript name must be audio1.txt
- audio-extension: wav or mp3, default - wav
- api-endpoint: The API endpoint URL where the ASR API is deployed. default given.

Run `python evaluate_asr.py --input-dir <path-to-your-testset-directory>` for executing the script.

The script will save the predicted transcript text files in `input-dir` with `<audio_file_name>-predicted.txt`.

It will output an HTML file outside of `input-dir` with WER report and diffs between ground truth transcripts and predicted transcripts.
