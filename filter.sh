#!/bin/bash  

# Check if watermarks.json exists  
if [ ! -f watermarks.json ]; then  
    echo "Error: watermarks.json not found!"  
    exit 1  
fi  

# Check if jq is installed  
if ! command -v jq &> /dev/null; then  
    echo "Error: jq is required to parse JSON. Please install jq."  
    exit 1  
fi  

# Check if vxn.png exists  
if [ ! -f assets/vxn.png ]; then  
    echo "Error: vxn.png not found!"  
    exit 1  
fi  

# Read coordinates from watermarks.json  
coords=($(jq -r '.[] | .[]' watermarks.json))  

# Extract coordinates and sizes (supporting 4 regions as in your example)  
x1=${coords[0]} ; y1=${coords[1]} ; w1=$((coords[2] - coords[0])) ; h1=$((coords[3] - coords[1]))  
x2=${coords[4]} ; y2=${coords[5]} ; w2=$((coords[6] - coords[4])) ; h2=$((coords[7] - coords[5]))  
x3=${coords[8]} ; y3=${coords[9]} ; w3=$((coords[10] - coords[8])) ; h3=$((coords[11] - coords[9]))  
x4=${coords[12]} ; y4=${coords[13]} ; w4=$((coords[14] - coords[12])) ; h4=$((coords[15] - coords[13]))  

# Build filter_complex  
filter_complex="[0:v]split=4[w1][w2][w3][w4];"  
filter_complex+="[w1]crop=$w1:$h1:$x1:$y1,boxblur=10:2[blur1];"  
filter_complex+="[w2]crop=$w2:$h2:$x2:$y2,boxblur=10:2[blur2];"  
filter_complex+="[w3]crop=$w3:$h3:$x3:$y3,boxblur=10:2[blur3];"  
filter_complex+="[w4]crop=$w4:$h4:$x4:$y4,boxblur=10:2[blur4];"  

# Overlay blurred regions back  
filter_complex+="[0:v][blur1]overlay=$x1:$y1[tmp1];"  
filter_complex+="[tmp1][blur2]overlay=$x2:$y2[tmp2];"  
filter_complex+="[tmp2][blur3]overlay=$x3:$y3[tmp3];"  
filter_complex+="[tmp3][blur4]overlay=$x4:$y4[blurred];"  

# Scale vxn.png to each watermark size, then overlay at the right position  
filter_complex+="[1:v]scale=$w1:$h1[v1];"  
filter_complex+="[blurred][v1]overlay=$x1:$y1[o1];"  
filter_complex+="[1:v]scale=$w2:$h2[v2];"  
filter_complex+="[o1][v2]overlay=$x2:$y2[o2];"  
filter_complex+="[1:v]scale=$w3:$h3[v3];"  
filter_complex+="[o2][v3]overlay=$x3:$y3[o3];"  
filter_complex+="[1:v]scale=$w4:$h4[v4];"  
filter_complex+="[o3][v4]overlay=$x4:$y4"  

# Run ffmpeg  
ffmpeg -i vid.MP4 -i assets/vxn.png \
  -filter_complex "$filter_complex" \
  -c:v libx264 -crf 23 -preset fast \
  -c:a copy \
  -metadata:s:v:0 handler_name="" \
  -metadata:s:v:0 vendor_id="" \
  -metadata:s:a:0 handler_name="" \
  -metadata:s:a:0 vendor_id="" \
  clean.mp4