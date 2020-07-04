#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import requests
import Levenshtein as Lev
from tqdm import tqdm
import argparse
from diff_generator import diff_match_patch

dmp = diff_match_patch()


input_dir = '/home/tareq/Downloads/testset/testset1_noisy_smartphone_single_speaker'
audio_extension = 'mp3'
url = 'http://alap.centralindia.cloudapp.azure.com:8084/transcribe/form/output'




def calculate_wer(hypothesis, ground_truth):
        """
        Computes the Word Error Rate, defined as the edit distance between the
        two provided sentences after tokenizing to words.
        Arguments:
            hypothesis (string): space-separated sentence
            ground_truth (string): space-separated sentence
        """
        # build mapping of words to integers
        b = set(hypothesis.split() + ground_truth.split())
        word2char = dict(zip(b, range(len(b))))

        # map the words to a char array (Levenshtein packages only accepts
        # strings)
        w1 = [chr(word2char[w]) for w in hypothesis.split()]
        w2 = [chr(word2char[w]) for w in ground_truth.split()]

        distance = Lev.distance(''.join(w1), ''.join(w2))
        num_words = len(ground_truth.split())
        return float(distance) / num_words


def read_transcript(wav_path, audio_ext):
    transcript_path = wav_path.replace("."+audio_ext', '.txt')
    with open(transcript_path, mode='r', encoding='utf8') as f:
        text = f.read()
    return text

def write_predicted_transcript(wav_path, text, audio_ext):
    transcript_path = wav_path.replace('.'+audio_ext, '-predicted.txt')
    with open(transcript_path, mode='w', encoding='utf8') as f:
        f.write(text)
    

def write_html_report(results, avg_wer):
    base_dir = os.path.dirname(input_dir)
    html_path = os.path.join(base_dir, 'report-'+os.path.basename(input_dir)+'.html')
    print('Writing report to {}', html_path)
    print('Please open this file in your browser.')
    with open(html_path, mode='w', encoding='utf8') as f:
        f.write('<h3>Average WER on {} files: {:.2f}</h3><br><br>'.format(len(results), avg_wer))
        for result in results:
            f.write("Audio: {} <br>".format(result['audio']))
            f.write("WER: {:.2f} <br>".format(result['WER']))
            f.write("Transcript: {} <br>".format(result['diff_html']))
            f.write('<hr style="height:2px;border-width:0;color:gray;background-color:gray"><br>')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', help='Path to the directory containing wavs and txts', 
            type=str, required=True)
    parser.add_argument('--audio-extension', help='Extension of the audio files in input_dir. Supported formats - almost all common formats (wav, mp3, aac etc)', 
            type=str, default='wav')
    parser.add_argument('--api-endpoint', help='API Endpoint URL where the ASR is deployed.',
            type=str, default='http://alap.centralindia.cloudapp.azure.com:8086/transcribe/form/output')
    
    params = parser.parse_args()

    input_dir = params.input_dir
    audio_extension = params.audio_extension
    url = params.api_endpoint

    audios = glob.glob(os.path.join(input_dir, '*.' + audio_extension))
    print("Total audio files found: ", len(audios))

    if len(audios) < 1:
        print('No audio found in dir: ', input_dir)
        print('Have you specified the correct directory? Or try setting --audio-extension param if your audios are not in wav format')
        sys.exit()

    total_wer = 0
    results = []
    for audio in tqdm(audios):
        try:
            print('\nProcessing file: ', audio)
            post_file = {'file':open(audio, 'rb')}
            r = requests.post(url, files=post_file)
            hyp_text = r.json()['transcript']
            ground_truth = read_transcript(audio, audio_extension)
            write_predicted_transcript(audio, hyp_text, audio_extension)
            wer = calculate_wer(hyp_text, ground_truth)
            diff = dmp.diff_main(ground_truth, hyp_text)
            total_wer += wer
            results.append({
                'audio': os.path.basename(audio),
                'WER': wer,
                'ground_truth': ground_truth,
                'predicted': hyp_text,
                'diff_html': dmp.diff_prettyHtml(diff)
            })
            print('Predicted: ', hyp_text)
            print('Ground Truth: ', ground_truth)
            print('WER: ', wer)

        except Exception as e:
            print(e)
            print('Connection lost. Failed to transcribe ', audio)

    avg_wer = total_wer / len(audios)
    print("Avg WER on all files: ",avg_wer)

    write_html_report(results, avg_wer)
