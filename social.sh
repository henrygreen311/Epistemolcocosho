#!/bin/bash
# movie_maker.sh
# Concatenate clips with normalized aspect ratio and clean audio cuts

OUTPUT="news.mp4"

ffmpeg -y \
  -i assets/intro.mp4 \
  -i final_news.mp4 \
  -i assets/replay.mp4 \
  -i clean.mp4 \
  -filter_complex "
    [0:v]scale=1280:720,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v0];
    [0:a]aresample=async=1,asetpts=PTS-STARTPTS[a0];

    [1:v]scale=1280:720,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v1];
    [1:a]aresample=async=1,asetpts=PTS-STARTPTS[a1];

    [2:v]scale=1280:720,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v2];
    [2:a]aresample=async=1,asetpts=PTS-STARTPTS[a2];

    [3:v]scale=1280:720,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v3];
    [3:a]aresample=async=1,asetpts=PTS-STARTPTS[a3];

    [v0][a0][v1][a1][v2][a2][v3][a3]concat=n=4:v=1:a=1[v][a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset veryfast -crf 23 \
  -c:a aac -b:a 128k -ac 2 \
  "$OUTPUT"

echo "✅ Movie created with hard audio cuts: $OUTPUT"