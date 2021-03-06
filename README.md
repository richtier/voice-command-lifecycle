# Voice Command Lifecycle #

[![code-climate-image]][code-climate]
[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

**Python library to manage the life-cycle of voice commands. Useful working with Alexa Voice Service.**

---

## Installation ##
```bash
pip install command_lifecycle
```

### Wakeword detector ###
A wakeword is a specific word that triggers the code to spring into action. It allows your code to be idle until the specific word is uttered.

The audio lifecycle uses [snowboy](https://github.com/Kitt-AI/snowboy#compile-a-python-wrapper) to determine if the wakeword was uttered. The library will need to be installed first.

Once you have compiled snowboy, copy the compiled `snowboy` folder to the top level of you project. By default, the folder structure should be:

```
.
├── ...
├── snowboy
|   ├── snowboy-detect-swig.cc
|   ├── snowboydetect.py
|   └── resources
|       ├── alexa.umdl
|       └── common.res
└── ...
```

If the default structure does not suit your needs can customize the [wakeword detector](#wakeword).

## Usage ##

You should send a steady stream of audio to to the lifecycle by repetitively calling `lifecycle.extend_audio(some_audio_bytes)`. If the wakeword such as "Alexa" (default), or "ok, Google" was uttered then `handle_command_started` is called. `handle_command_finised` is then called once the command audio that followed the wakeword has finished.

### Microphone audio ###

```py
import pyaudio

import command_lifecycle


class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):

    def handle_command_started(self, wakeword_name):
        super().handle_command_started(wakeword_name)
        print(f'The audio contained {wakeword_name}!')

    def handle_command_finised(self):
        super().handle_command_finised()
        print('The command has finished')

lifecycle = AudioLifecycle()

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)

try:
    print('listening. Start by saying "Alexa". Press CTRL + C to exit.')
    while True:
        lifecycle.extend_audio(stream.read(1024))
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
```


### File audio ###

```py
import wave

import command_lifecycle

class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):
    def handle_command_started(self, wakeword_name):
        super().handle_command_started(wakeword_name)
        print(f'The audio contained {wakeword_name}!')


lifecycle = AudioLifecycle()
with wave.open('./tests/resources/alexa_what_time_is_it.wav', 'rb') as f:
    while f.tell() < f.getnframes():
        lifecycle.extend_audio(f.readframes(1024))

print('The command has finished')

```

### Usage with Alexa ###

`command_lifecycle` is useful for interacting with voice services. The lifecycle waits until a wakeword was issued and then start streaming the audio command to the voice service (using [Alexa Voice Service Client](https://github.com/richtier/alexa-voice-service-client)), then do something useful with the response:

```py
from avs_client.avs_client.client import AlexaVoiceServiceClient
import pyaudio

import command_lifecycle


class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):
    alexa_client = AlexaVoiceServiceClient(
        client_id='my-client-id'
        secret='my-secret',
        refresh_token='my-refresh-token',
    )

    def __init__(self):
        self.alexa_client.connect()
        super().__init__()

    def handle_command_started(self, wakeword_name):
        super().handle_command_started(wakeword_name)
        audio_file = command_lifecycle.to_audio_file()
        for directive in self.alexa_client.send_audio_file(audio_file):
            # do something with the AVS audio response, e.g., play it.

lifecycle = AudioLifecycle()

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True)

try:
    print('listening. Start by saying "Alexa". Press CTRL + C to exit.')
    while True:
        lifecycle.extend_audio(stream.read(1024))
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
```

## Customization ##

### Wakeword ###

The default wakeword is "Alexa". This can be changed by sub-classing `command_lifecycle.wakeword.SnowboyWakewordDetector`:

```py

from command_lifecycle import wakeword


class MySnowboyWakewordDetector(wakeword.SnowboyWakewordDetector):
    decoder_models = [
        {
            'name': 'CUSTOM',
            'model': b'path/to/custom-wakeword-model.umdl'
            'sensitivity': b'0.5',
        }
    ]


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    audio_detector_class = MySnowboyWakewordDetector

    def handle_command_started(self, wakeword_name):
        super().handle_command_started(wakeword_name)
        print(f'The audio contained the {wakeword_name}!')

    def handle_command_finised(self):
        super().handle_command_finised()
        print('The command has finished')

lifecycle = AudioLifecycle()

# now load the audio into lifecycle

```

See the [Snowboy docs](https://github.com/Kitt-AI/snowboy#hotword-as-a-service) for steps on creating custom wakeword models.


### Multiple Wakewords ###

Triggering different behaviour for different wakeword may be desirable. To do this use multiple items in `decoder_models`:

```py
from command_lifecycle import wakeword


class MyMultipleWakewordDetector(wakeword.SnowboyWakewordDetector):
    GOOGLE = 'GOOGLE'

    decoder_models = wakeword.SnowboyWakewordDetector.decoder_models + [
        {
            'name': GOOGLE,
            'model': b'path/to/okgoogle.umdl',
            'sensitivity': b'0.5',
        }
    ]


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    audio_detector_class = MyMultipleWakewordDetector

    def handle_command_started(self, wakeword_name):
        if wakeword_name == self.audio_detector.ALEXA:
            print('Alexa standing by')
        elif wakeword_name == self.audio_detector.GOOGLE:
            print('Google at your service')
        super().handle_command_started(wakeword_name)
```

You can download wakewords from [here](https://snowboy.kitt.ai/dashboard).

### Wakeword detector ###

Snowboy is the default wakeword detector. Other wakeword detectors can be used by sub-classing `command_lifecycle.wakeword.BaseWakewordDetector` and setting `wakeword_detector_class` to your custom class:


```py
import wave

from command_lifecycle import lifecycle, wakeword


class MyCustomWakewordDetector(wakeword.BaseWakewordDetector):
    import_error_message = 'Cannot import wakeword library!'
    wakeword_library_import_path = 'path.to.wakeword.Library'

    def was_wakeword_uttered(self, buffer):
        # use the library to check if the audio in the buffer has the wakeword.
        # not `buffer.get()` returns the audio inside the buffer.
        ...

    def is_talking(self, buffer):
        # use the library to check if the audio in the buffer has audible words
        # not `buffer.get()` returns the audio inside the buffer.
        ...


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    audio_detector_class = MyCustomWakewordDetector
    ...


lifecycle = AudioLifecycle()
# now load the audio into lifecycle

```


### Handling input data ###

Three input data formats are supported:

| Converter                     | Notes                                                    |
| ------------------------------| ---------------------------------------------------------|
| `NoOperationConverter`        | **default** Input data is already wav bytes.             |
| `WavIntSamplestoWavConverter` | Input data is list of integers.                          |
| `WebAudioToWavConverter`      | Input data is list of floats generated by a web browser. |

Customize this by setting the lifecycle's `audio_converter_class`:

```

from command_lifecycle.helpers import WebAudioToWavConverter

class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    audio_converter_class = WebAudioToWavConverter

```


### Expecting slower or faster commands ###

The person giving the audio command might take a moment to collect their thoughts before finishing the command. This silence could be interpreted as the command ending, resulting in `handle_command_finised` being called prematurely.

To avoid this the lifecycle tolerates some silence in the command before the lifecycle timesout the command. This silence can happen at the beginning or middle of the command. Note a side-effect of this is there will be a pause between when the person has stopped talking and when `handle_command_finised` is called.

To change this default behaviour `timeout_manager_class` can be changed. The available timeout managers are:

| Timeout manager            | Notes                                            |
| ---------------------------| ------------------------------------------------ |
| `ShortTimeoutManager`      | Allows one second of silence.                    |
| `MediumTimeoutManager`     | **default** Allows 2 seconds of silence.         |
| `LongTimeoutManager`       | Allows three seconds of silence.                 |

To make a custom timeout manager create a subclass of `command_lifecycle.timeout.BaseTimeoutManager`:

```py

import wave

from command_lifecycle import timeout, wakeword


class MyCustomTimeoutManager(timeout.BaseTimeoutManager):
    allowed_silent_seconds = 4


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    timeout_manager_class = MyCustomTimeoutManager

```

## Unit test ##

To run the unit tests, call the following commands:

```sh
make test_requirements
make test
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [PyPI](https://pypi.org/project/command-lifecycle/#history).

## Other projects ##
This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.


[code-climate-image]: https://codeclimate.com/github/richtier/voice-command-lifecycle/badges/gpa.svg
[code-climate]: https://codeclimate.com/github/richtier/voice-command-lifecycle

[circle-ci-image]: https://circleci.com/gh/richtier/voice-command-lifecycle/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/richtier/voice-command-lifecycle/tree/master

[codecov-image]: https://codecov.io/gh/richtier/voice-command-lifecycle/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/richtier/voice-command-lifecycle

