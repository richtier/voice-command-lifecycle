# voice-command-lifecycle #
Python library to manage the life-cycle of voice commands. Useful working with Alexa Voice Service.

## Installation ##
```bash
pip install git+https://github.com/richtier/voice-command-lifecycle.git@0.4.0#egg=command_lifecycle
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

You should send a steady stream of audio to to the lifecycle by repetitively calling `lifecycle.extend_audio(some_audio_bytes)`. If the prescribed wakeword was uttered, `handle_command_started` is called. `handle_command_finised` is then called once the command audio that followed the wakeword has finished. This is useful if you want to stream some audio to Alexa Voice Service once a wakeword has been uttered.

```py
import wave

import command_lifecycle


class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):

    def handle_command_started(self):
        super().handle_command_started()
        print('The audio contained the wakeword!')

    def handle_command_finised(self):
        super().handle_command_finised()
        print('the command in the audio has finished')


lifecycle = AudioLifecycle()
with wave.open('/path/to/audio.wav', 'rb') as f:
    for i in range(int(f.getnframes()/1024)):
        frame = f.readframes(1024)
        lifecycle.extend_audio(frame)

```

### A more useful example ###

`command_lifecycle` is useful for interacting with voice services. The lifecycle can wait until a wakeword such as "Alexa", or "ok, Google" was issued and then start streaming the proceeding audio command to the voice service (using [Alexa Voice Service Client](https://github.com/richtier/alexa-voice-service-client)), then do something useful with the response:

```py
import wave

from avs_client.client import AlexaVoiceServiceClient
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

    def handle_command_started(self):
        super().handle_command_started()
        audio_file = command_lifecycle.to_audio_file()
        alexa_response_audio = self.alexa_client.send_audio_file(audio_file)
        if alexa_response_audio:
            # do something with the AVS audio response, e.g., play it.


lifecycle = AudioLifecycle()
with wave.open('/path/to/audio.wav', 'rb') as f:
    for i in range(int(f.getnframes()/1024)):
        frame = f.readframes(1024)
        lifecycle.extend_audio(frame)

```

## Customization ##

### Wakeword ###

The default wakeword is "Alexa". This can be changed by sub-classing `command_lifecycle.wakeword.SnowboyWakewordDetector`:

```py

from command_lifecycle import wakeword


class MySnowboyWakewordDetector(wakeword.SnowboyWakewordDetector):
    decoder_model = b'path/to/custom-wakeword-model.umdl'


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    audio_detector_class = MySnowboyWakewordDetector

    def handle_command_started(self):
        super().handle_command_started()
        print('The audio contained the wakeword!')

    def handle_command_finised(self):
        super().handle_command_finised()
        print('the command in the audio has finished')


lifecycle = AudioLifecycle()
# now load the audio into lifecycle

```

See the [Snowboy docs](https://github.com/Kitt-AI/snowboy#hotword-as-a-service) for steps on creating custom wakeword models.

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

    def handle_command_started(self):
        super().handle_command_started()
        print('The audio contained the wakeword!')

    def handle_command_finised(self):
        super().handle_command_finised()
        print('the command in the audio has finished')


lifecycle = AudioLifecycle()
# now load the audio into lifecycle


```

### Expecting slower or faster commands ###

The person giving the audio command might take a moment to collect their thoughts before finishing the command. This silence could be interpreted as the command ending, resulting in `handle_command_finised` being called prematurely.

To avoid this the lifecycle allows the command to contain up to two seconds of silence before the command times out. This silence can happen at the beginning or middle of the command. Note a side-effect of this is `handle_command_finised` will not be called until two seconds after the person has stopped talking.

To change this default behaviour `timeout_manager_class` can be changed. The available timeout managers are:

| Timeout manager         | Notes                                            |
| -------------------------| ------------------------------------------------ |
| `ImmediateTimeoutManager`  | No timeout. Silence ends the command immediately. Use this if you're loading audio from a file instead of streaming in real time from a microphone |
| `ShortTimeoutManager`      | Allows one second of silence.                    |
| `MediumTimeoutManager`     | **default** Allows two seconds of silence.       |
| `LongTimeoutManager`       | Allows four seconds of silence                   |

To make a custom timeout manager create a subclass of `command_lifecycle.timeout.BaseTimeoutManager`:

```py

import wave

from command_lifecycle import timeout, wakeword


class MyCustomTimeoutManager(timeout.BaseTimeoutManager):
    timeout_seconds = 0.5


class AudioLifecycle(lifecycle.BaseAudioLifecycle):
    timeout_manager_class = MyCustomTimeoutManager

```


## Other projects ##
This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.
