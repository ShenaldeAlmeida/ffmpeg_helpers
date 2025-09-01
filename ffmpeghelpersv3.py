from datetime import datetime
import ffmpeg
import json
import os
from typing import Dict
from fractions import Fraction
import uuid 

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


def standardise_video(
        video_path:str, 
        filetype: str = "mp4", 
        width: int = 1280, 
        height: int = 720, 
        fps: int = 30,
        user_ID: str = None
        ) -> str:
    """
    Standardise a video to a consistent format

    Standardisation:
      - Resolution: width x height (default 1280x720)
      - Frame rate: fps (default 30)
      - Video Codec: H.264 
      - Audio Codec: AAC
      - Pixel format: yuv420p

    Args:
        video_path (str): Path to input video file
        filetype (str): Output file extension (default mp4)
        width (int): Target width
        height (int): Target height
        fps (int): Target frames per second
        user_id (str, optional): User identifier 

    Returns:
        str: Path to the standardised output file

    Raises:
        FileNotFoundError: If input file does not exist
        RuntimeError: If ffmpeg fails
    """
    
    #checks if input file exists
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"{video_path} not found")
    
    #check if file has audio 
    probe = ffmpeg.probe(video_path)
    has_audio = any([prop["codec_type"] == "audio" for prop in probe["streams"]])
    audioarg = {"acodec" : "aac"} if has_audio else {}

    # scale to fit inside width x height, preserving aspect ratio
    scale_filter = f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease"

# pad to exactly width x height if needed
    pad_filter = f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    
    #takes only the filename root not the ext (eg.mov)
    filename_root, _ = os.path.splitext(os.path.basename(video_path))

    #timestamps the file for uniqueness if reuploads occur 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    #Generates mostly unique UUID
    unique_ID = uuid.uuid4().hex[:8]
    user_tag = f"{user_ID}_" if user_ID else ""

    output_path = f"{user_tag}{filename_root}_std_at_{timestamp}_{unique_ID}.{filetype}"

    try:
        (    
            ffmpeg.input(video_path)
            .filter("scale", f"w={width}:h={height}:force_original_aspect_ratio=decrease")
            .filter("pad", f"{width}:{height}:(ow-iw)/2:(oh-ih)/2")
            .output(output_path, vcodec='libx264', **audioarg, pix_fmt='yuv420p')
            .run()
        )
    #raises ffmpeg error if it fails    
    except ffmpeg.Error as e:
        raise RuntimeError(
            f"FFmpeg failed for {video_path}. "
            f"Error details: {e.stderr.decode(errors='ignore')}"
        )
    
    return output_path

# vidprop("LOL.mov")
# standardise_video("LOL.mov")




# .filter('scale', 'min(iw*720/ih\,1280)', 'min(ih*1280/iw\,720)')



 