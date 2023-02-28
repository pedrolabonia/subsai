#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Short description of this Python module.
Longer description of this module.
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

from typing import Tuple
import pysubs2
from pysubs2 import SSAFile, SSAEvent

from subsai.models.abstract_model import AbstractModel
import whisper_timestamped
from subsai.utils import _load_config, get_available_devices


class WhisperTimeStamped(AbstractModel):
    model_name = 'openai/whisper'
    config_schema = {
        # load model config
        'model_type': {
            'type': list,
            'description': "One of the official model names listed by `whisper.available_models()`, or "
                           "path to a model checkpoint containing the model dimensions and the model "
                           "state_dict.",
            'options': whisper_timestamped.available_models(),
            'default': 'base'
        },
        'device': {
            'type': list,
            'description': "The PyTorch device to put the model into",
            'options': [None, *get_available_devices()],
            'default': None
        },
        'download_root': {
            'type': str,
            'description': "Path to download the model files; by default, it uses '~/.cache/whisper'",
            'options': None,
            'default': None
        },
        'in_memory': {
            'type': bool,
            'description': "whether to preload the model weights into host memory",
            'options': None,
            'default': False
        },
        # transcribe config
        'verbose': {
            'type': bool,
            'description': "Whether to display the text being decoded to the console. "
                           "If True, displays all the details,"
                           "If False, displays minimal details. If None, does not display anything",
            'options': None,
            'default': None
        },
        'temperature': {
            'type': Tuple,
            'description': "Temperature for sampling. It can be a tuple of temperatures, which will be "
                           "successively used upon failures according to either `compression_ratio_threshold` "
                           "or `logprob_threshold`.",
            'options': None,
            'default': (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
        },
        'compression_ratio_threshold': {
            'type': float,
            'description': "If the gzip compression ratio is above this value, treat as failed",
            'options': None,
            'default': 2.4
        },
        'logprob_threshold': {
            'type': float,
            'description': "If the average log probability over sampled tokens is below this value, treat as failed",
            'options': None,
            'default': -1.0
        },
        'no_speech_threshold': {
            'type': float,
            'description': "If the no_speech probability is higher than this value AND the average log probability "
                           "over sampled tokens is below `logprob_threshold`, consider the segment as silent",
            'options': None,
            'default': 0.6
        },
        'condition_on_previous_text': {
            'type': bool,
            'description': "if True, the previous output of the model is provided as a prompt for the next window; "
                           "disabling may make the text inconsistent across windows, but the model becomes less "
                           "prone to getting stuck in a failure loop, such as repetition looping or timestamps "
                           "going out of sync.",
            'options': None,
            'default': True
        },
        # decode options
        'task': {
            'type': list,
            'description': "whether to perform X->X 'transcribe' or X->English 'translate'",
            'options': ['transcribe', 'translate'],
            'default': 'transcribe'
        },
        'language': {
            'type': str,
            'description': "language that the audio is in; uses detected language if None",
            'options': None,
            'default': None
        },
        'sample_len': {
            'type': int,
            'description': "maximum number of tokens to sample",
            'options': None,
            'default': None
        },
        'best_of': {
            'type': int,
            'description': "number of independent samples to collect, when t > 0",
            'options': None,
            'default': None
        },
        'beam_size': {
            'type': int,
            'description': "number of beams in beam search, when t == 0",
            'options': None,
            'default': None
        },
        'patience': {
            'type': float,
            'description': "patience in beam search (https://arxiv.org/abs/2204.05424)",
            'options': None,
            'default': None
        },
        'length_penalty': {
            'type': float,
            'description': "'alpha' in Google NMT, None defaults to length norm",
            'options': None,
            'default': None
        },
        'suppress_tokens': {
            'type': str,
            'description': 'list of tokens ids (or comma-separated token ids) to suppress "-1" will suppress '
                           'a set of symbols as defined in `tokenizer.non_speech_tokens()`',
            'options': None,
            'default': "-1"
        },
        'fp16': {
            'type': bool,
            'description': 'use fp16 for most of the calculation',
            'options': None,
            'default': True
        },
        'remove_punctuation_from_words': {
            'type': bool,
            'description': "If False, words will be glued with the next punctuation mark (if any)."
                           "If True, there will be no punctuation mark in the `words[:]['text']` list."
                           "It only affects these strings; This has no influence on the computation of the word"
                           " confidence, whatever the value of `include_punctuation_in_confidence` is.",
            'options': None,
            'default': False
        },
        'refine_whisper_precision': {
            'type': float,
            'description': 'How much can we refine Whisper segment positions, in seconds. Must be a multiple of 0.02.',
            'options': None,
            'default': 0.5
        },
        'min_word_duration': {
            'type': float,
            'description': 'Minimum duration of a word, in seconds. If a word is shorter than this, timestamps will '
                           'be adjusted.',
            'options': None,
            'default': 0.04
        },
        'plot_word_alignment': {
            'type': float,
            'description': 'Minimum duration of a word, in seconds. If a word is shorter than this, timestamps will '
                           'be adjusted.',
            'options': None,
            'default': 0.04
        },
        'seed': {
            'type': int,
            'description': "Random seed to use for temperature sampling, for the sake of reproducibility."
                           "Choose None for unpredictable randomness",
            'options': None,
            'default': 1234
        },
        'naive_approach': {
            'type': bool,
            'description': "Force the naive approach that consists in decoding twice the audio file, once to get the "
                           "transcription and once with the decoded tokens to get the alignment. "
                           "Note that this approach is used anyway when beam_size is not None and/or when the "
                           "temperature is a list with more than one element.",
            'options': None,
            'default': False
        },
        'naive_approach': {
            'type': bool,
            'description': "Force the naive approach that consists in decoding twice the audio file, once to get the "
                           "transcription and once with the decoded tokens to get the alignment. "
                           "Note that this approach is used anyway when beam_size is not None and/or when the "
                           "temperature is a list with more than one element.",
            'options': None,
            'default': False
        }

    }

    def __init__(self, media_file, model_config={}):
        super(WhisperTimeStamped, self).__init__(model_config=model_config,
                                                 model_name=self.model_name)
        # config
        self.model_type = _load_config('model_type', model_config, self.config_schema)
        self.device = _load_config('device', model_config, self.config_schema)
        self.download_root = _load_config('download_root', model_config, self.config_schema)
        self.in_memory = _load_config('in_memory', model_config, self.config_schema)

        self.verbose = _load_config('verbose', model_config, self.config_schema)
        self.temperature = _load_config('temperature', model_config, self.config_schema)
        self.compression_ratio_threshold = _load_config('compression_ratio_threshold', model_config, self.config_schema)
        self.logprob_threshold = _load_config('logprob_threshold', model_config, self.config_schema)
        self.no_speech_threshold = _load_config('no_speech_threshold', model_config, self.config_schema)
        self.condition_on_previous_text = _load_config('condition_on_previous_text', model_config, self.config_schema)

        self.decode_options = \
            {config: _load_config(config, model_config, self.config_schema)
             for config in self.config_schema if not hasattr(self, config)}

        self.model = whisper_timestamped.load_model(name=self.model_type,
                                                    device=self.device,
                                                    download_root=self.download_root,
                                                    in_memory=self.in_memory)

    def transcribe(self, media_file) -> str:
        audio = whisper_timestamped.load_audio(media_file)
        results = whisper_timestamped.transcribe(self.model, audio,
                                                 verbose=self.verbose,
                                                 temperature=self.temperature,
                                                 compression_ratio_threshold=self.compression_ratio_threshold,
                                                 logprob_threshold=self.logprob_threshold,
                                                 no_speech_threshold=self.no_speech_threshold,
                                                 condition_on_previous_text=self.condition_on_previous_text,
                                                 **self.decode_options
                                                 )
        subs = SSAFile()
        for segment in results['segments']:
            for word in segment['words']:
                event = SSAEvent(start=pysubs2.make_time(s=word["start"]), end=pysubs2.make_time(s=word["end"]))
                event.plaintext = word["text"].strip()
                subs.append(event)
        return subs


if __name__ == '__main__':
    file = '/home/su/code/subsai/tests/video/test1.mp4'
    model = WhisperTimeStamped(file)
    subs = model.transcribe()
    # for segment in subs['segments']:
    #     print(segment['words'])
    # print(segment["words"])
    # print(subs['segments'])
    for sub in subs:
        print(sub)
    subs.save('test1-words.srt')
    # print(whisper_timestamped.available_models())
