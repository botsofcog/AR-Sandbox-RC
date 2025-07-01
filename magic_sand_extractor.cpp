
// Magic-Sand Data Extractor
// Add this to Magic-Sand to export Kinect data

void exportKinectData() {
    if (kinectGrabber.isFrameNew()) {
        // Get depth data
        ofPixels depthPixels = kinectGrabber.getDepthPixels();
        
        // Get RGB data  
        ofPixels colorPixels = kinectGrabber.getColorPixels();
        
        // Export to file or shared memory
        saveDepthData(depthPixels);
        saveColorData(colorPixels);
    }
}

void saveDepthData(ofPixels& pixels) {
    // Save depth data to file for Python bridge
    ofFile depthFile("kinect_depth.raw", ofFile::WriteOnly, true);
    depthFile.writeFromBuffer((char*)pixels.getData(), pixels.size());
    depthFile.close();
}

void saveColorData(ofPixels& pixels) {
    // Save color data to file for Python bridge
    ofFile colorFile("kinect_color.raw", ofFile::WriteOnly, true);
    colorFile.writeFromBuffer((char*)pixels.getData(), pixels.size());
    colorFile.close();
}
