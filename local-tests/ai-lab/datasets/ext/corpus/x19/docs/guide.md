# Stream pipeline

app/stream.py needs the transcoder in lib/transcode.py, which needs
the codec pack in vendor/codecs/. Without the codec pack the
transcoder refuses to start.
