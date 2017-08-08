# voice-command-lifecycle #
Python library to manage the life-cycle of voice commands. Useful working with Alexa Voice Service.

## Installation ##
```bash
pip install git+https://github.com/richtier/voice-command-lifecycle.git@v0.3.0#egg=command_lifecycle
```

### Wakeword detector ###
A wakeword is a specific word that triggers the code to spring into action. It allows your code to be idle until the special word is uttered.

The audio lifecycle uses a third parties library to determine if the wakeworkd was uttered. The library will need to be installed first. Supported libraries:

- [Snowboy](https://github.com/Kitt-AI/snowboy#compile-a-python-wrapper). [default]. Once installed you can use `command_lifecycle.wakeword.SnowboyWakewordDetector` audio detector class with your audio lifecycle.

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

`command_lifecycle` is useful for interacting with voice services. The lifecycle can wait until a wakeword such as "Alexa", or "ok google" was issued and then start streaming the proceeding audio command to the voice service, then do something useful with the response:

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

## Other projects ##
This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.
