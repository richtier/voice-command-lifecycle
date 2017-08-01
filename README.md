# voice-command-lifecycle
Python library to manage the life-cycle of voice commands. Useful working with Alexa Voice Service.

## Installation
```
pip install git+https://github.com/richtier/voice-command-lifecycle.git@v0.1.0#egg=command_lifecycle
```

## Usage

The audio lifecycle will receive a steady stream of audio via `lifecycle.extend_audio()`. If the prescribed wakeword is uttered, `handle_command_started` is called. `handle_command_finised` is then called once the command audio that followed the wakeword has finished. This is useful if you want to stream some audio to Alexa Voice Service once a wakeword has been uttered.

```
import command_lifecycle

class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):

    def handle_command_started(self):
        super().handle_command_started()
        print('The audio contained the wakeword!)

    def handle_command_finised(self):
        super().handle_command_finised()
        print('the command in the audio has finished')


lifecycle = AudioLifecycle()

with open('/path/to/audio.wav') as f:
    for wav_audio in f:
        lifecycle.extend_audio(wav_audio)

```

### A more useful example

`command_lifecycle` is useful for interacting with voice services. The lifecycle can wait until a wakeword such as "Alexa", or "ok google" was issued and then start streaming the proceeding audio command to the voice service, then do something useful with the response:

```
from avs_client.client import AlexaVoiceServiceClient
import command_lifecycle


class AudioLifecycle(command_lifecycle.BaseAudioLifecycle):
    alexa_client = AlexaVoiceServiceClient(
        client_id='my-client-id'
        secret='my-secret',
        refresh_token='my-refresh-token`,
    )

    def __init__(self, reply_channel):
        self.alexa_client.connect()
        super().__init__()

    def handle_command_started(self):
        super().handle_command_started()
        audio_file = LifeCycleFileLike(self)
        alexa_response_audio = self.alexa_client.send_audio_file(audio_file)
        if alexa_response_audio:
            # do something with the AVS audio response, e.g., play it.


lifecycle = AudioLifecycle()

with open('/path/to/audio.wav') as f:
    for wav_audio in f:
        lifecycle.extend_audio(wav_audio)

```

## Other projects
This library is used by [alexa-browser-client](https://github.com/richtier/alexa-browser-client), which allows you to talk to Alexa from your browser.
