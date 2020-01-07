SEC_PER_FRAME = 0.3 # seconds
IMAGE_WIDTH = 256
IMAGE_HEIGHT = 256

THRESHOLD_SSIM_AUDIO = 0.4
THRESHOLD_SSIM = 0.6
THRESHOLD_ORB = 0.90
THRESHOLD_ORB_MATCH = 0.95
HASH_CUTOFF = 5

SEQUENCE_THRESHOLD = 4 # seconds
MIN_LENGTH_SEQUENCE = 5 # seconds
FRACTION_SIZE_PREINTRO = 0.35 #35 percentage
PREINTRO_START = 30 # limit for a preintro to start in seconds
DOWNSCALE_FACTOR = 10

MARGIN_BETWEEN_PITCH = 1
MIN_SEQ_LENGTH = 10 #seconds
SEGMENT_LENGTH = 0.1 #seconds

NUMBER_OF_NEIGHBOR_VIDEOS = 6

HASH_NAME = "hashes"
DESCRIPTION_INTRO = "intro"
DESCRIPTION_MATCHES_INTRO = "matches_intro"
DESCRIPTION_MATCHES = "matches"
DESCRIPTION_PITCHES = "pitches"

#HMM
TRAIN_SIZE = 0.7 # fraction of the training set size, rest is test
START_SEED = 0

# Black Detection 
BLACK_DETECTOR_THRESHOLD = 0.1  # 0.0 complete blackness 
BLACK_DETECTOR_MIN_DUR = 0.1    # minimum sequence duration 

# Processing  
VIDEO_GENRES = ["serier"]
VIDEO_START_LEN = 480 
DELETE_VIDEO_AFTER_EXTRACTION = False # Must first perform video comparison before video files are removed...  
APPLY_BLACK_DETECTION = True 
APPLY_SCENE_DETECTION = True  
SAVE_TO_FILE = True 
SAVE_TO_DB = True 

SCHEDULED_PREPROCESSING_START = "01:00"
SCHEDULED_PREPROCESSING_END = "13:00"


