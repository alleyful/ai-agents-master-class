# Technique video assets

Technique lessons work without videos. To add a manually generated clip, save
an MP4 at the `video_asset_path` shown in `content/techniques.py`:

```text
assets/techniques/<technique-slug>/video.mp4
```

The first pilot set is:

- `crochet-chain-stitch/video.mp4`
- `single-crochet/video.mp4`
- `knit-stitch/video.mp4`

Each technique detail page shows its ready-to-copy generation prompt while the
file is absent and switches to the local video automatically when it exists.
