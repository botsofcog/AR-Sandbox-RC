
// Magic-Sand Data Extraction Integration
// Add this to Magic-Sand's main loop for real-time data export

void exportFrameData() {
    if (kinectGrabber.isFrameNew()) {
        // Export depth data
        ofPixels depthPixels = kinectGrabber.getDepthPixels();
        if (depthPixels.isAllocated()) {
            string depthPath = "magic_sand_data/depth/depth_" + ofToString(ofGetFrameNum()) + ".raw";
            ofFile depthFile(depthPath, ofFile::WriteOnly, true);
            depthFile.writeFromBuffer((char*)depthPixels.getData(), depthPixels.size());
            depthFile.close();
        }
        
        // Export RGB data
        ofPixels colorPixels = kinectGrabber.getColorPixels();
        if (colorPixels.isAllocated()) {
            string rgbPath = "magic_sand_data/rgb/rgb_" + ofToString(ofGetFrameNum()) + ".raw";
            ofFile rgbFile(rgbPath, ofFile::WriteOnly, true);
            rgbFile.writeFromBuffer((char*)colorPixels.getData(), colorPixels.size());
            rgbFile.close();
        }
        
        // Export metadata
        ofJson metadata;
        metadata["frame"] = ofGetFrameNum();
        metadata["timestamp"] = ofGetElapsedTimeMillis();
        metadata["depth_width"] = depthPixels.getWidth();
        metadata["depth_height"] = depthPixels.getHeight();
        metadata["rgb_width"] = colorPixels.getWidth();
        metadata["rgb_height"] = colorPixels.getHeight();
        
        string metaPath = "magic_sand_data/metadata_" + ofToString(ofGetFrameNum()) + ".json";
        ofSaveJson(metaPath, metadata);
    }
}
