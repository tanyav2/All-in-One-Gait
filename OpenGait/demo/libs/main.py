import os
import os.path as osp
import time
import sys
sys.path.append(os.path.abspath('.') + "/demo/libs/")
from track import *
from segment import *
from recognise import *

def main():
    output_dir = "./demo/output/OutputVideos/"
    os.makedirs(output_dir, exist_ok=True)
    current_time = time.localtime()
    timestamp = time.strftime("%Y_%m_%d_%H_%M_%S", current_time)
    video_save_folder = osp.join(output_dir, timestamp)
    
    save_root = './demo/output/'
    gallery_video_path = "./demo/output/InputVideos/gallery.mp4"
    probe1_video_path  = "./demo/output/InputVideos/probe1.mp4"
    probe2_video_path  = "./demo/output/InputVideos/probe2.mp4"
    probe3_video_path  = "./demo/output/InputVideos/probe3.mp4"
    probe4_video_path  = "./demo/output/InputVideos/probe4.mp4"

    # tracking
    gallery_track_result = track(gallery_video_path, video_save_folder)
    probe1_track_result  = track(probe1_video_path, video_save_folder)
    probe2_track_result  = track(probe2_video_path, video_save_folder)
    probe3_track_result  = track(probe3_video_path, video_save_folder)
    probe4_track_result  = track(probe4_video_path, video_save_folder)

    gallery_video_name = gallery_video_path.split("/")[-1]
    gallery_video_name = save_root+'/GaitSilhouette/'+gallery_video_name.split(".")[0]
    probe1_video_name  = probe1_video_path.split("/")[-1]
    probe1_video_name  = save_root+'/GaitSilhouette/'+probe1_video_name.split(".")[0]
    probe2_video_name  = probe2_video_path.split("/")[-1]
    probe2_video_name  = save_root+'/GaitSilhouette/'+probe2_video_name.split(".")[0]
    probe3_video_name  = probe3_video_path.split("/")[-1]
    probe3_video_name  = save_root+'/GaitSilhouette/'+probe3_video_name.split(".")[0]
    probe4_video_name  = probe4_video_path.split("/")[-1]
    probe4_video_name  = save_root+'/GaitSilhouette/'+probe4_video_name.split(".")[0]
    exist = os.path.exists(gallery_video_name) and os.path.exists(probe1_video_name) \
            and os.path.exists(probe2_video_name) and os.path.exists(probe3_video_name) \
            and os.path.exists(probe4_video_name)
    print(exist)
    if exist:
        gallery_silhouette = getsil(gallery_video_path, save_root+'/GaitSilhouette/')
        probe1_silhouette  = getsil(probe1_video_path , save_root+'/GaitSilhouette/')
        probe2_silhouette  = getsil(probe2_video_path , save_root+'/GaitSilhouette/')
        probe3_silhouette  = getsil(probe3_video_path , save_root+'/GaitSilhouette/')
        probe4_silhouette  = getsil(probe4_video_path , save_root+'/GaitSilhouette/')
    else:
        gallery_silhouette = seg(gallery_video_path, gallery_track_result, save_root+'/GaitSilhouette/')
        probe1_silhouette  = seg(probe1_video_path , probe1_track_result , save_root+'/GaitSilhouette/')
        probe2_silhouette  = seg(probe2_video_path , probe2_track_result , save_root+'/GaitSilhouette/')
        probe3_silhouette  = seg(probe3_video_path , probe3_track_result , save_root+'/GaitSilhouette/')
        probe4_silhouette  = seg(probe4_video_path , probe4_track_result , save_root+'/GaitSilhouette/')

    # recognise
    gallery_feat = extract_sil(gallery_silhouette, save_root+'/GaitFeatures/')
    probe1_feat  = extract_sil(probe1_silhouette , save_root+'/GaitFeatures/')
    probe2_feat  = extract_sil(probe2_silhouette , save_root+'/GaitFeatures/')
    probe3_feat  = extract_sil(probe3_silhouette , save_root+'/GaitFeatures/')
    probe4_feat  = extract_sil(probe4_silhouette , save_root+'/GaitFeatures/')

    # Use a threshold of 9.0 for detection
    threshold = 11.5
    print(f"\n\n===== USING THRESHOLD: {threshold} =====")
    print("Only matches with distances below this threshold will be considered valid.")
    
    gallery_probe1_result = compare(probe1_feat, gallery_feat, threshold)
    gallery_probe2_result = compare(probe2_feat, gallery_feat, threshold)
    gallery_probe3_result = compare(probe3_feat, gallery_feat, threshold)
    gallery_probe4_result = compare(probe4_feat, gallery_feat, threshold)

    # Check if any matches were found
    if gallery_probe1_result is None:
        print("WARNING: No matches found for probe1 within the threshold.")
    if gallery_probe2_result is None:
        print("WARNING: No matches found for probe2 within the threshold.")
    if gallery_probe3_result is None:
        print("WARNING: No matches found for probe3 within the threshold.")
    if gallery_probe4_result is None:
        print("WARNING: No matches found for probe4 within the threshold.")

    # write the result back to the video
    writeresult(gallery_probe1_result, probe1_video_path, video_save_folder)
    writeresult(gallery_probe2_result, probe2_video_path, video_save_folder)
    writeresult(gallery_probe3_result, probe3_video_path, video_save_folder)
    writeresult(gallery_probe4_result, probe4_video_path, video_save_folder)


if __name__ == "__main__":
    main()
