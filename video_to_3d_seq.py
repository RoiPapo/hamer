import glob
from PIL import Image
import os
from moviepy.editor import VideoFileClip
from demo import main as invoke_hamer
from pathlib import Path

def extract_frames(video_path, output_directory, fps=5 ,frame_limit=None):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load the video clip
    clip = VideoFileClip(video_path)

    # Iterate over each frame and save it as an image
    for i, frame in enumerate(clip.iter_frames(fps=fps), start=1):
        if frame_limit and i>frame_limit:
            break
        # Construct the file name for the frame
        filename = os.path.join(output_directory, f"frame-{i:04d}.jpg")
        # Save the frame as an image
        clip = Image.fromarray(frame)
        clip.save(filename)

    # Close the clip
    clip.close()


def parse_3D_objects(folder):
    for filename in os.listdir(folder):
        if not filename.endswith(".obj"):
            continue


import os

def load_obj_file(file_path):
    """Load vertices from an OBJ file."""
    vertices = []
    with open(file_path+'.obj', 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
    return vertices

def calculate_movement_vectors(source_folder):
    """Calculate movement vectors between consecutive frames."""
    files = [Path(file).stem for file in glob.glob(f'{source_folder}/frame-*.obj')]
    
    # Group files by frame number
    frames = {}
    for file in files:
        frame_number = file.split('_')[0].split('-')[1]
        hand_index = file.split('_')[1].split('.')[0]
        
        # Skip faulty frames
        if any(f"frame-{frame_number}_2" in f for f in files):
            continue
        
        if frame_number not in frames:
            frames[frame_number] = {}
        frames[frame_number][hand_index] = os.path.join(source_folder, file)
    
    # Sort frame numbers
    sorted_frames = sorted(frames.keys())
    
    # Calculate vectors for consecutive frames
    for i in range(len(sorted_frames) - 1):
        frame1 = sorted_frames[i]
        frame2 = sorted_frames[i + 1]
        
        # Process right hand first (index '1'), then left hand (index '0')
        vectors = []
        for hand_index in ['1', '0']:
            if hand_index in frames[frame1] and hand_index in frames[frame2]:
                vertices_frame1 = load_obj_file(frames[frame1][hand_index])
                vertices_frame2 = load_obj_file(frames[frame2][hand_index])
                
                # Calculate movement vectors
                for v1, v2 in zip(vertices_frame1, vertices_frame2):
                    dx = v2[0] - v1[0]
                    dy = v2[1] - v1[1]
                    dz = v2[2] - v1[2]
                    vectors.append((dx, dy, dz))
        
        # Write results to a text file
        output_file = Path(f"{source_folder}/movement_vectors_{frame1}_{frame2}.txt")
        with open(output_file, 'w') as f:
            for vector in vectors:
                f.write(f"{vector[0]} {vector[1]} {vector[2]}\n")





if __name__ == "__main__":
    params={
        "video_path": "/data/home/roipapo/datasets/UW_2024/p046_suture.mp4",
        "output_root": "Scalpel_output",
        "fps": 1,
        "frame_limit": 20
    }
    
    output_directory = Path(f"{params['output_root']}/{params['video_path'].split('/')[-1][:-4]}")
    # extract_frames(params["video_path"], output_directory, fps=params["fps"],frame_limit= params["frame_limit"])
    invoke_hamer(custom_frames_path=output_directory.resolve(),custom_output_folder=output_directory.resolve(),custom_focal_length=1000)
    calculate_movement_vectors(output_directory.resolve())



