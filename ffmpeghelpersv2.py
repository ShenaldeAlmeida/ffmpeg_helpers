"""
Version with dynamic property list and normalise function
"""

import ffmpeg
import json
import os
from typing import Dict, List
from fractions import Fraction

standard_properties = ["width", "height", "codec_name", "avg_frame_rate", "duration"]

def normalise(metadata: dict, float_precision: int = 2) -> dict:
    """
    Ensure consistent types for metadata:
      - Integers and Floats are rounded to N=2 decimal places
      - Strings remain as-is
    """
    normalised = {}
    for k, v in metadata.items():
        try:
            num = float(v)
            normalised[k] = round(num, float_precision)
        except (ValueError, TypeError):
            normalised[k] = v
    return normalised

def vidprop(video_path: str, properties: List[str] = standard_properties) -> Dict:
    """
    Extracts key metadata from video file 

    Key metadata can be specified with optional argument

    Always outputs file name and size

    >>>

    Returns a dictionary with essential fields for surf engine:
        - width, height: resolution
        - codec_name: video codec
        - avg_frame_rate: float FPS
        - duration: video duration in seconds
        - file_size: in bytes
        - filename: original filename

    Raises:
            FileNotFound if file does not exist
            ValueError if no video type file is found 
    """

    #checks if video exists
    if os.path.isfile(video_path) == False:                     
        raise FileNotFoundError(f"{video_path} not found") 
    
    #gets filename and file size (not in our probe)
    fileprops = {
        "filename": os.path.basename(video_path),
        "file_size": os.path.getsize(video_path),
    }
    
    #gets main properties
    probe = ffmpeg.probe(video_path)                                        #uses ffmpeg method to collate video properties
    vidprops = None
    for prop in probe["streams"]:                                           #the properties sit as a dic in an array under the key "streams"
        if prop["codec_type"] == "video":                                   # checks that it is a video
            vidprops = {k:v for k,v in prop.items() if k in properties}
            break                                                           # avoids overwriting if multiple video streams 
    if vidprops == None:                                                
        raise ValueError(f"No video stream found in {video_path}")          
    
    #Turn fps to float
    try:
        fps_fraction = Fraction(vidprops.get("avg_frame_rate"))
        fps_float = round(float(fps_fraction),2)
        vidprops["avg_frame_rate"] = fps_float
    except: 
        vidprops["avg_frame_rate"] = 0
    
    raw_metadata = (fileprops | vidprops)
    normalised_metadata = normalise(raw_metadata)
    return normalised_metadata

print(vidprop("LOL.mp4"))


'''
suggested changes - add schema, keep integers as integers such as file_size 
'''




 