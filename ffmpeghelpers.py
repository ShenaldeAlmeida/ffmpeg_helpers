import ffmpeg
import json 

properties = ["width", "height", "codec_name", "avg_frame_rate", "duration"]
video = "LOL.mp4"
def vidprop(video, properties):
    """
    The function takes the video as the input and returns a dictionary 
    of the properties we are interested in
     
    >>> {'codec_name': 'h264', 'width': 1080, 'height': 720}
    """
    probe = ffmpeg.probe(video)     #uses ffmpeg method to collate video properties
    for s in probe["streams"]:          #the properties sit as a dic in an array under the key "streams"
        if s["codec_type"] == "video":      # checks that it is a video
            x = {k:v for k,v in s.items() if k in properties}
    return x

print(vidprop(video,properties))