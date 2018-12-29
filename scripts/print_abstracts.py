import arxiv
import pandas as pd

ARTICLES = """
URL_ID,Category,Title
1610.09087,cs.CV,Recent advances in content based video copy detection
1610.00838,cs.CV,Image Aesthetic Assessment: An Experimental Survey
1608.03240,cs.CV,Fractional Calculus In Image Processing: A Review
1608.01017,cs.CV,Automated X-ray Image Analysis for Cargo Security: Critical Review and Future Promise
1607.08368,cs.CV,"Local Feature Detectors, Descriptors, and Image Representations: A Survey"
1607.06235,cs.CV,Haze Visibility Enhancement: A Survey and Quantitative Benchmarking
1607.04760,cs.CV,Design and implementation of image processing system for Lumen social robot-humanoid as an exhibition guide for Electrical Engineering Days 2015
1607.01232,cs.CV,A probabilistic tour of visual attention and gaze shift computational models
1607.01092,cs.CV,Incorporating prior knowledge in medical image segmentation: a survey
1607.00331,cs.CV,Machine-based Multimodal Pain Assessment Tool for Infants: A Review
1606.05703,cs.CV,A Survey of Pansharpening Methods with A New Band-Decoupled Variational Model
1606.00185,cs.CV,A Survey on Learning to Hash
1604.07090,cs.CV,"A Review of Co-saliency Detection Technique: Fundamentals, Applications, and Challenges"
1603.06028,cs.CR,"A Survey of Stealth Malware: Attacks, Mitigation Measures, and Steps Toward Autonomous Open World Solutions"
1602.08855,cs.CV,Pandora: Description of a Painting Database for Art Movement Recognition with Baselines and Perspectives
1601.05511,cs.CV,RGB-D-based Action Recognition Datasets: A Survey
1601.01006,cs.CV,Space-Time Representation of People Based on 3D Skeletal Data: A Review
1512.00939,cs.CV,A Literature Survey of various Fingerprint De-noising Techniques to justify the need of a new De-noising model based upon Pixel Component Analysis
1511.01245,cs.CV,Decomposition into Low-rank plus Additive Matrices for Background/Foreground Separation: A Review for a Comparative Evaluation with a Large-Scale Dataset
1510.04585,cs.CV,A Brief Survey of Image Processing Algorithms in Electrical Capacitance Tomography
1510.01077,math.SP,Nonlinear Spectral Analysis via One-homogeneous Functionals - Overview and Future Prospects
1509.06939,cs.RO,Enabling Depth-driven Visual Attention on the iCub Humanoid Robot: Instructions for Use and New Perspectives
1509.05520,cs.CV,An Experimental Survey on Correlation Filter-based Tracking
1506.04472,cs.CV,A Survey of Multithreading Image Analysis
1506.00097,cs.CV,A Review of Feature and Data Fusion with Medical Images
1505.03489,cs.CV,A Review Paper: Noise Models in Digital Image Processing
1505.00523,cs.CV,Modeling Representation of Videos for Anomaly Detection using Deep Learning: A Review
1504.07442,cs.CV,Embedded Platforms for Computer Vision-based Advanced Driver Assistance Systems: a Survey
1504.04531,cs.CV,Hyperspectral pansharpening: a review
1503.07297,cs.CV,A Brief Survey of Recent Edge-Preserving Smoothing Algorithms on Digital Images
1503.00843,cs.MM,A Survey On Video Forgery Detection
1502.05928,cs.CV,Supervised Dictionary Learning and Sparse Representation-A Review
1502.04383,cs.CV,A Comprehensive Survey on Pose-Invariant Face Recognition
1502.02160,cs.CV,"A Survey on Hough Transform, Theory, Techniques and Applications"
1502.01812,cs.CV,Crowded Scene Analysis: A Survey
1501.02825,cs.CV,A Survey on Recent Advances of Computer Vision Algorithms for Egocentric Video
1412.4031,astro-ph.IM,High-level numerical simulations of noise in CCD and CMOS photosensors: review and tutorial
1412.3421,cs.CV,Multi-Atlas Segmentation of Biomedical Images: A Survey
1412.1732,physics.med-ph,Statistical models and regularization strategies in statistical image reconstruction of low-dose X-ray CT: a survey
1410.5894,cs.CV,Vehicle Detection and Tracking Techniques: A Concise Review
1409.7787,cs.SD,Audio Surveillance: a Systematic Review
1409.1484,cs.CV,The Evolution of First Person Vision Methods: A Survey
1408.3985,cs.CV,Offline Signature-Based Fuzzy Vault (OSFV: Review and New Results
1408.2927,cs.DS,Hashing for Similarity Search: A Survey
1407.7626,cs.CV,A Survey on Two Dimensional Cellular Automata and Its Application in Image Processing
1406.7799,cs.MM,Subjective and Objective Quality Assessment of Image: A Survey
1405.2539,cs.CV,A Review of Image Mosaicing Techniques
1403.5869,cs.CV,Block Motion Based Dynamic Texture Analysis: A Review
1405.6133,cs.CV,A review over the applicability of image entropy in analyses of remote sensing datasets
1311.0124,cs.CV,Reconstruction of Complex-Valued Fractional Brownian Motion Fields Based on Compressive Sampling and Its Application to PSF Interpolation in Weak Lensing Survey
1310.2053,cs.CV,The role of RGB-D benchmark datasets: an overview
1310.0315,cs.CV,Computer Vision Systems in Road Vehicles: A Review
1306.1676,cs.CV,Algebraic foundations of split hypercomplex nonlinear adaptive filtering
1302.1326,cs.CV,Cloud Computing framework for Computer Vision Research:An Introduction
1302.0446,cs.CV,Sparse Camera Network for Visual Surveillance -- A Comprehensive Survey
1210.0829,cs.CV,A Survey of Multibiometric Systems
1209.6491,cs.CV,Review of Statistical Shape Spaces for 3D Data with Comparative Analysis for Human Faces
1209.2515,cs.CV,Wavelet Based Image Coding Schemes : A Recent Survey
1208.3670,cs.CV,A Survey of Recent View-based 3D Model Retrieval Methods
1206.3975,cs.GR,The Ultrasound Visualization Pipeline - A Survey
1204.6725,cs.CV,OCT Segmentation Survey and Summary Reviews and a Novel 3D Segmentation Algorithm and a Proof of Concept Implementation
1202.0216,cs.CV,The watershed concept and its use in segmentation : a brief history
1201.1422,cs.CV,Minutiae Extraction from Fingerprint Images - a Review
1105.4058,cs.CV,Human Identity Verification based on Heart Sounds: Recent Advances and Future Directions
1003.4053,cs.CV,A Comprehensive Review of Image Enhancement Techniques
0704.1267,cs.CV,Text Line Segmentation of Historical Documents: a Survey
"""

df = pd.read_csv(pd.compat.StringIO(ARTICLES), dtype={'URL_ID': str, 'Category': 'category'})
url_ids = df['URL_ID'].tolist()
results = arxiv.query(id_list=url_ids, max_results=len(df), sort_by='submittedDate')
assert len(results) == len(df)
for (index, row), result in zip(df.iterrows(), results):
    url_id = result['arxiv_url'].replace('http://arxiv.org/abs/', '', 1).rsplit('v', 1)[0]
    assert url_id == row.URL_ID
    row_str = pd.DataFrame(row).T.to_csv(header=False, index=False, line_terminator='')
    categories = sorted(d['term'] for d in result['tags'])
    categories_str = ', '.join(categories)
    abstract = result['summary']
    print(f'{row_str}\n{categories_str}\n\t{abstract}\n')
