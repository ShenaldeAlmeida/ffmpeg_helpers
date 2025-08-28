"""
Version with inherent normalised schema
"""


import ffmpeg
import json
import os
from typing import Dict
from fractions import Fraction

def vidprop(video_path: str) -> Dict:
    """
    Extracts key metadata from video file 

    Key metadata can be specified with optional argument

    Always outputs file name and size

    >>>

    Returns a dictionary with essential fields for surf engine:
        - filename: original filename (str)
        - file_size: in bytes (int)
        - width: video width in pixels (int)
        - height: video height in pixels (int)
        - codec_name: video codec (str)
        - avg_frame_rate: float FPS (float)
        - duration: video duration in seconds (float)

    Raises:
            FileNotFound if file does not exist
            ValueError if no video type file is found 
    """

    #checks if video exists
    if os.path.isfile(video_path) == False:                     
        raise FileNotFoundError(f"{video_path} not found") 
    
    #checks if file is video and gets properties  
    probe = ffmpeg.probe(video_path)                                        
    vidprops = None
    for prop in probe["streams"]:                                           
        if prop["codec_type"] == "video":                                   
            vidprops = prop
            break                                                                  
    if vidprops == None:                                                
        raise ValueError(f"No video stream found in {video_path}")          

    #scheme with metadata we want, outputs none or 0 if it doesn't exists
    metadata = {
        "filename": os.path.basename(video_path) or None,
        "file_size": int(os.path.getsize(video_path)) if os.path.exists(video_path) else 0,
        "width": int(vidprops.get("width", 0)),
        "height": int(vidprops.get("height", 0)),
        "codec_name": vidprops.get("codec_name") or None,
        "avg_frame_rate": 0.0,
        "duration": float(vidprops.get("duration", 0.0))
    }

    #Turn fps to float and insert into metadata 
    try:
        fps_fraction = Fraction(vidprops.get("avg_frame_rate"))
        fps_float = float(fps_fraction)
        metadata["avg_frame_rate"] = fps_float
    except: 
        metadata["avg_frame_rate"] = 0

    return metadata 

print(vidprop("LOL.mp4"))





 