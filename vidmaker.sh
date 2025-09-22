#!/bin/bash
# vidmaker.sh
VIDEO="clean.mp4"
AUDIO="news_voice.mp3"
OUTPUT="final_news.mp4"

# Get durations
video_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO")
audio_dur=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO")

# Calculate loops (ceil) only if audio is longer
loops=1
if (( $(echo "$audio_dur > $video_dur" | bc -l) )); then
    loops=$(awk -v a="$audio_dur" -v v="$video_dur" 'BEGIN {print int((a/v)+0.999)}')
fi

echo "Video duration: $video_dur sec"
echo "Audio duration: $audio_dur sec"
echo "Repeating video $loops times..."

# Make concat list if needed
tmpfile="inputs.txt"
rm -f "$tmpfile"
for i in $(seq 1 $loops); do
    echo "file '$VIDEO'" >> "$tmpfile"
done

# Concat video copies (force re-encode so video + audio are kept)
ffmpeg -y -f concat -safe 0 -i "$tmpfile" -c:v libx264 -c:a aac temp_video.mp4

# Merge original video audio + news narration
ffmpeg -y -i temp_video.mp4 -i "$AUDIO" \
  -filter_complex "[0:a]volume=0.5[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:normalize=1[outa]" \
  -map 0:v:0 -map "[outa]" \
  -c:v libx264 -c:a aac "$OUTPUT"

# Cleanup
rm -f temp_video.mp4 "$tmpfile"

echo "✅ Done! Output saved as $OUTPUT"