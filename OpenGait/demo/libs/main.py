import os
import os.path as osp
import time
import sys
import glob
sys.path.append(os.path.abspath('.') + "/demo/libs/")
from track import *
from segment import *
from recognise import *

def main(gallery_path=None, probe_paths=None, input_dir=None, threshold=11.5):
    output_dir = "./demo/output/OutputVideos/"
    os.makedirs(output_dir, exist_ok=True)
    current_time = time.localtime()
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", current_time)
    video_save_folder = osp.join(output_dir, timestamp)
    
    save_root = './demo/output/'
    
    # Set default gallery path if not provided
    if gallery_path is None:
        gallery_path = "./demo/output/InputVideos/gallery.mp4"

    # Get probe paths either from arguments, input directory, or default
    if probe_paths is None:
        if input_dir is not None:
            # Get all video files from input directory
            probe_paths = glob.glob(os.path.join(input_dir, "*.mp4"))
            # Filter out gallery video if it's in the same directory
            probe_paths = [p for p in probe_paths if p != gallery_path]
        else:
            # Use default probe paths
            probe_paths = [
                "./demo/output/InputVideos/probe1.mp4",
                "./demo/output/InputVideos/probe2.mp4",
                "./demo/output/InputVideos/probe3.mp4", 
                "./demo/output/InputVideos/probe4.mp4"
            ]
    
    # Process gallery video
    gallery_track_result = track(gallery_path, video_save_folder)
    gallery_video_name = gallery_path.split("/")[-1]
    gallery_video_name = save_root+'/GaitSilhouette/'+gallery_video_name.split(".")[0]
    
    # Process all probe videos
    probe_results = []
    for probe_path in probe_paths:
        # Track the probe video
        probe_track_result = track(probe_path, video_save_folder)
        
        # Get silhouette path
        probe_video_name = probe_path.split("/")[-1]
        probe_silhouette_path = save_root+'/GaitSilhouette/'+probe_video_name.split(".")[0]
        
        # Check if silhouette already exists
        if os.path.exists(gallery_video_name) and os.path.exists(probe_silhouette_path):
            gallery_silhouette = getsil(gallery_path, save_root+'/GaitSilhouette/')
            probe_silhouette = getsil(probe_path, save_root+'/GaitSilhouette/')
        else:
            gallery_silhouette = seg(gallery_path, gallery_track_result, save_root+'/GaitSilhouette/')
            probe_silhouette = seg(probe_path, probe_track_result, save_root+'/GaitSilhouette/')
        
        # Extract features
        gallery_feat = extract_sil(gallery_silhouette, save_root+'/GaitFeatures/')
        probe_feat = extract_sil(probe_silhouette, save_root+'/GaitFeatures/')
        
        # Compare with gallery
        probe_result = compare(probe_feat, gallery_feat, threshold)
        
        # Check if match was found
        if probe_result is None:
            print(f"WARNING: No matches found for {probe_path} within the threshold.")
        
        # Write results to video
        writeresult(probe_result, probe_path, video_save_folder)
        
        # Store results
        probe_results.append({
            'path': probe_path,
            'result': probe_result
        })
    
    # Print summary
    print(f"\n\n===== USING THRESHOLD: {threshold} =====")
    print("Only matches with distances below this threshold will be considered valid.")
    print(f"Processed {len(probe_paths)} probe videos against gallery video {gallery_path}")
    
    return probe_results


if __name__ == "__main__":
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        # Default threshold value
        threshold_val = 11.5
        
        gallery_path = sys.argv[1]
        
        # Check if last argument is a threshold value
        if len(sys.argv) > 2 and sys.argv[-1].startswith("--threshold="):
            threshold_str = sys.argv[-1].split("=")[1]
            try:
                threshold_val = float(threshold_str)
                # Remove threshold from arguments list
                probe_paths = sys.argv[2:-1] if len(sys.argv) > 3 else None
            except ValueError:
                # Not a valid threshold, treat as a probe path
                probe_paths = sys.argv[2:] if len(sys.argv) > 2 else None
        else:
            probe_paths = sys.argv[2:] if len(sys.argv) > 2 else None
            
        main(gallery_path=gallery_path, probe_paths=probe_paths, threshold=threshold_val)
    else:
        main()
