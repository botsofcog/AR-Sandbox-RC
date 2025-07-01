from warnings import warn
import matplotlib.pyplot as plt
import numpy
from scipy.spatial.distance import cdist
from .dummy_aruco import dummy_markers_in_frame
import pandas as pd
from sandbox import set_logger
logger = set_logger(__name__)

pd.options.mode.chained_assignment = None
# default='warn' # TODO: SettingWithCopyWarning appears when using LoadTopoModule with arucos

try:
    import cv2
    from cv2 import aruco
    CV2_IMPORT = True
except ImportError:
    CV2_IMPORT = False
    logger.warning('opencv is not installed. Object detection will not work', exc_info=True)


class ArucoMarkers(object):  # TODO: Include widgets to calibrate arucos
    """
    class to detect Aruco markers in the kinect data (IR and RGB)
    An Area of interest can be specified, markers outside this area will be ignored
    """

    def __init__(self, sensor=None, aruco_dict=None, **kwargs):
        if not aruco_dict:
            if CV2_IMPORT:
                self.aruco_dict = aruco.DICT_4X4_50  # set the default dictionary here
            else:
                self.aruco_dict = None
        else:
            self.aruco_dict = aruco_dict
        # self.area = area  # TODO: set a square Area of interest here (Hot-Area). Need it?
        if sensor is not None:
            if hasattr(sensor.Sensor, "name"):
                name = sensor.Sensor.name
                if name == "dummy":
                    self.kinect = "dummy"
                    logger.info("Using dummy arucos. "
                                "Create your own aruco positions using .set_aruco_position() function")
                elif name == "kinect_v2":
                    self.kinect = sensor.Sensor
                    self.calib = sensor
                    logger.info("KinectV2 loaded")
                elif name == "lidar":
                    self.kinect = sensor.Sensor
                    self.calib = sensor
                    logger.info("LiDAR loaded")
                else:
                    self.kinect = "dummy"
                    logger.warning("%s not recognized as supported sensor for aruco detection. "
                                "Using dummy arucos" % name)
            else:
                if sensor == "dummy":
                    logger.info("Using dummy arucos. "
                                "Create your own aruco positions using .set_aruco_position() function")
                else:
                    logger.warning("No sensor loaded. Detection will only work in color image. Using dummy arucos")
                self.kinect = "dummy"

        self.ir_markers = None
        # if self.calib is not None:
        #    if self.calib.aruco_corners is not None:
        #        self.rgb_markers = pd.read_json(self.calib.aruco_corners)
        #    else:
        #        self.rgb_markers = None
        self.projector_markers = None
        self.dict_markers_current = None  # markers that were detected in the last frame
        # self.dict_markers_all = all markers ever detected with their last known position and timestamp
        self.dict_markers_all = self.dict_markers_current

        self.middle = None
        self.corner_middle = None
        self.point_markers = None

        # dataframes and variables used in the update loop:
        self.markers_in_frame = pd.DataFrame()
        self.aruco_markers = pd.DataFrame()
        self._threshold = 10.0

        # Pose Estimation
        self.mtx = numpy.array([[1977.4905366892494, 0.0, 547.6845435554575],  # Hardcoded distortion parameters
                                [0.0, 2098.757943278828, 962.426967248953],
                                [0.0, 0.0, 1.0]])
        self.dist = numpy.array([[-0.1521704243263453],  # Hard-coded distortion parameters
                                 [-0.5137710352422746],
                                 [-0.010673768065933672],
                                 [0.01065954734833698],
                                 [2.2812034123550817],
                                 [0.15820606213404878],
                                 [0.5618247374672848],
                                 [-2.195963638734801],
                                 [0.0],
                                 [0.0],
                                 [0.0],
                                 [0.0],
                                 [0.0],
                                 [0.0]])
        self._size_of_marker = 0.02  # size of aruco markers in meters
        self._length_of_axis = 0.05  # length of the axis drawn on the frame in meters

        # Automatic calibration #TODO: Deprecated?
        # self.load_corners_ids()
        init_correction_x = 20
        init_correction_y = -80
        self.set_xy_correction(init_correction_x, init_correction_y)
        logger.info('Aruco module loaded')

    def set_xy_correction(self, x: int, y: int):
        self.CoordinateMap = pd.DataFrame()
        if self.kinect == "dummy":
            self.CoordinateMap = None
            logger.info('using dummy aruco module')
            return
        if self.kinect.name == "kinect_v2":
            import platform
            _platform = platform.system()
            if _platform == "Linux":
                from sandbox.markers.aruco_linux import start_mapping, set_correction
                # TODO: correction in x and y direction for the mapping between color space and depth space
                self._correction_x = x
                self._correction_y = y
                set_correction(self._correction_x, self._correction_y)
                while len(self.CoordinateMap) < 5:
                    self.CoordinateMap = start_mapping(self.kinect)
            elif _platform == "Windows":
                from sandbox.markers.aruco_windows import start_mapping, set_correction
                # TODO: correction in x and y direction for the mapping between color space and depth space
                self._correction_x = x
                self._correction_y = y
                set_correction(self._correction_x, self._correction_y)
                while len(self.CoordinateMap) < 5:
                    self.CoordinateMap = start_mapping(self.kinect)
            else:
                logger.warning("%s not supported" % _platform)
        elif self.kinect.name == "lidar":
            from sandbox.markers.lidar_aruco import start_mapping, set_correction
            self._correction_x = x
            self._correction_y = y
            set_correction(self._correction_x, self._correction_y)
            while len(self.CoordinateMap) < 5:
                self.CoordinateMap = start_mapping(self.kinect)
        else:
            logger.warning("%s Not supported for aruco detection" % self.kinect.name)

    def aruco_detect(self, image):
        """ Function to detect an aruco marker in a color image
        Args:
            image: numpy array containing a color image (BGR type)
        Returns:
            corners: x, y location of a detected aruco marker(detect the 4 corners of the aruco)
            ids: id of the detected aruco
            rejectedImgPoints: show x, y coordinates of searches for aruco markers but not successful
       """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(self.aruco_dict)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        return corners, ids, rejectedImgPoints

    def get_location_marker(self, corners):
        """Get the middle position from the detected corners
         Args:
             corners: List containing the position x, y of the aruco marker
         Returns:
             pr1: x location
             pr2: y location
        """
        pr1 = int(numpy.mean(corners[:, 0]))
        pr2 = int(numpy.mean(corners[:, 1]))
        return pr1, pr2

    def search_aruco(self, frame: numpy.ndarray = None, **kwargs) -> pd.DataFrame:
        """
        searches for aruco markers in the current kinect image and writes detected markers to
        self.markers_in_frame. call this first in the update function.
        Args
            frame: gets the color frame to search the markers on
        Returns
            markers_in_frame
        """
        if self.kinect == "dummy":
            dict_position = kwargs.get("dict_position")
            depth_frame = kwargs.get("depth_frame")
            plt.pause(0.15)  # TODO: To avoid problems with the common issue #3 of NoneType dpi
            self.markers_in_frame = dummy_markers_in_frame(dict_position, depth_frame)
            return self.markers_in_frame

        if frame is None:
            frame = self.kinect.get_color()
        corners, ids, rejectedImgPoints = self.aruco_detect(frame)
        if ids is not None:
            labels = {"ids", "x", "y", "Counter"}
            df = pd.DataFrame(columns=labels)
            for j in range(len(ids)):
                if ids[j] not in df.ids.values:
                    x_loc, y_loc = self.get_location_marker(corners[j][0])
                    df_temp = pd.DataFrame(
                        {"ids": [ids[j][0]], "x": [x_loc], "y": [y_loc]})
                    df = pd.concat([df, df_temp], sort=False)

            df = df.reset_index(drop=True)
            self.markers_in_frame = self.convert_color_to_depth(None, self.CoordinateMap, data=df)
            self.markers_in_frame.insert(0, 'counter', 0)
            self.markers_in_frame.insert(1, 'box_x', numpy.NaN)
            self.markers_in_frame.insert(2, 'box_y', numpy.NaN)
            self.markers_in_frame.insert(0, 'is_inside_box', numpy.NaN)
            self.markers_in_frame = self.markers_in_frame.set_index(self.markers_in_frame['ids'], drop=True)
            self.markers_in_frame = self.markers_in_frame.drop(columns=['ids'])
        else:
            labels = {"ids", "x", "y", "Counter"}
            self.markers_in_frame = pd.DataFrame(columns=labels)
        return self.markers_in_frame

    def update_marker_dict(self):
        """
        updates existing marker points in self.aruco_markers. new found markers are automatically added.
        A marker that is not detected for more than *self._threshold* frames is removed from the list.
        call in update after self.search_aruco():
        Returns:
            changes in place
        """
        for j in self.markers_in_frame.index:
            if j not in self.aruco_markers.index:
                # add new aruco
                self.aruco_markers = self.aruco_markers.append(self.markers_in_frame.loc[j])
            else:
                # Update aruco
                df_temp = self.markers_in_frame.loc[j]
                self.aruco_markers.at[j] = df_temp

        for i in self.aruco_markers.index:  # increment counter for not found arucos
            if i not in self.markers_in_frame.index:
                self.aruco_markers.at[i, 'counter'] += 1.0

            if self.aruco_markers.loc[i]['counter'] >= self._threshold:
                self.aruco_markers = self.aruco_markers.drop(i)

        # return self.aruco_markers

    def transform_to_box_coordinates(self):
        """
        checks if aruco markers are within the dimensions of the sandbox (boolean: is_inside_box)
        and converts the location to box coordinates x,y. call after self.update_markers in the update loop
        Returns:
        """
        if self.kinect == "dummy":
            if len(self.aruco_markers) > 0:
                self.aruco_markers['is_inside_box'] = self.aruco_markers['is_inside_box'].astype('bool')
            return

        if len(self.aruco_markers) > 0:
            self.aruco_markers['box_x'] = self.aruco_markers['Depth_x'] - self.calib.s_left
            self.aruco_markers['box_y'] = self.calib.s_height - self.aruco_markers['Depth_y'] - self.calib.s_bottom
            for j in self.aruco_markers.index:
                self.aruco_markers['is_inside_box'].loc[j] = \
                    self.calib.s_frame_width > (self.aruco_markers['Depth_x'].loc[j] - self.calib.s_left) and \
                    (self.aruco_markers['Depth_x'].loc[j] - self.calib.s_left) > 0 and \
                    (self.calib.s_frame_height > (self.calib.s_height - self.aruco_markers['Depth_y'].loc[j] -
                                                  self.calib.s_bottom) and \
                     (self.calib.s_height - self.aruco_markers['Depth_y'].loc[j] - self.calib.s_bottom) > 0)

    ############### Utilities ########################

    def find_markers_ir(self, IR=None, amount=None):
        """ Function to search for a determined amount of arucos in the infrared image. It will continue searching in
        different frames of the image until it finds all the markers
        Args:
            IR= search in the infrared frame. If None then captures a new frame
            amount: specify the number of arucos to search
        Returns:
            ir_marker: DataFrame with the id, x, y coordinates for the location of the aruco
                        And rotation and translation vectors for the pos estimation
        """
        labels = {'ids', 'Corners_IR_x', 'Corners_IR_y', "Rotation_vector", "Translation_vector"}
        df = pd.DataFrame(columns=labels)

        if amount is not None:
            while len(df) < amount:

                minim = 0
                maxim = numpy.arange(1000, 30000, 500)
                if IR is None:
                    IR = self.kinect.get_ir_frame_raw()
                for i in maxim:
                    ir_use = numpy.interp(IR, (minim, i), (0, 255)).astype('uint8')
                    ir3 = numpy.stack((ir_use, ir_use, ir_use), axis=2)
                    corners, ids, rejectedImgPoints = self.aruco_detect(ir3)

                    if not ids is None:
                        for j in range(len(ids)):
                            if ids[j] not in df.ids.values:
                                rvec, tvec, trash = aruco.estimatePoseSingleMarkers([corners[j][0]],
                                                                                    self._size_of_marker,
                                                                                    self.mtx, self.dist)
                                x_loc, y_loc = self.get_location_marker(corners[j][0])
                                df_temp = pd.DataFrame(
                                    {'ids': [ids[j][0]], 'Corners_IR_x': [x_loc], 'Corners_IR_y': [y_loc],
                                     "Rotation_vector": [rvec], "Translation_vector": [tvec]})
                                df = pd.concat([df, df_temp], sort=False)

        self.ir_markers = df.reset_index(drop=True)
        return self.ir_markers

    def find_markers_rgb(self, color=None, amount=None):
        """ Function to search for a determined amount of arucos in the color image. It will continue searching in
        different frames of the image until it finds all the markers
        Args:
            color: search in the color frame. If None then captures a new frame
            amount: specify the number of arucos to search
        Returns:
            rgb_markers: DataFrame with the id, x, y coordinates for the location of the aruco
                        and rotation and translation vectors for the pos estimation
        """

        labels = {"ids", "Corners_RGB_x", "Corners_RGB_y", "Rotation_vector", "Translation_vector"}
        df = pd.DataFrame(columns=labels)

        if amount is not None:
            while len(df) < amount:
                if color is None:
                    color = self.kinect.get_color()
                corners, ids, rejectedImgPoints = self.aruco_detect(color)

                if not ids is None:
                    for j in range(len(ids)):
                        if ids[j] not in df.ids.values:
                            rvec, tvec, trash = aruco.estimatePoseSingleMarkers([corners[j][0]], self._size_of_marker,
                                                                                self.mtx, self.dist)
                            x_loc, y_loc = self.get_location_marker(corners[j][0])
                            df_temp = pd.DataFrame(
                                {"ids": [ids[j][0]], "Corners_RGB_x": [x_loc], "Corners_RGB_y": [y_loc],
                                 "Rotation_vector": [rvec], "Translation_vector": [tvec]})
                            df = pd.concat([df, df_temp], sort=False)

        self.rgb_markers = df.reset_index(drop=True)
        return self.rgb_markers

    def find_markers_projector(self, color=None, amount=None):
        """ Function to search for a determined amount of arucos in the projected image. It will continue searching in
        different frames of the image until it finds all the markers
        Args:
            color: search in the color frame. If None then captures a new frame
            amount: specify the number of arucos to search
        Returns:
            projector_markers: DataFrame with the id, x, y coordinates for the location of the aruco
                                and rotation and translation vectors for the pos estimation
            corner_middle: list that include the location of the central corner aruco with id=20
        """

        labels = {"ids", "Corners_projector_x", "Corners_projector_y", "Rotation_vector", "Translation_vector"}
        df = pd.DataFrame(columns=labels)

        if amount is not None:
            while len(df) < amount:
                if color is None:
                    color = self.kinect.get_color()
                corners, ids, rejectedImgPoints = self.aruco_detect(color)

                if ids is not None:
                    for j in range(len(ids)):
                        if ids[j] == 20:
                            # predefined id value to coincide with the projected aruco for the automatic calibration
                            # method used to calculate the scaling factor
                            self.corner_middle = corners[j][0]
                        if ids[j] not in df.ids.values:
                            rvec, tvec, trash = aruco.estimatePoseSingleMarkers([corners[j][0]], self._size_of_marker,
                                                                                self.mtx, self.dist)
                            x_loc, y_loc = self.get_location_marker(corners[j][0])
                            df_temp = pd.DataFrame(
                                {"ids": [ids[j][0]], "Corners_projector_x": [x_loc], "Corners_projector_y": [y_loc],
                                 "Rotation_vector": [rvec], "Translation_vector": [tvec]})
                            df = pd.concat([df, df_temp], sort=False)

        self.projector_markers = df.reset_index(drop=True)

        return self.projector_markers, self.corner_middle

    def create_aruco_marker(self, id: int = 1, resolution: int = 50, show: bool = False,
                            save: bool = False, path: str = './',
                            fig_filename = None):
        """ Function that creates a single aruco marker providing its id and resolution
        Args:
            id: int indicating the id of the aruco to create
            resolution: int
            show: boolean. Display the created aruco marker
            save: boolean. save the created aruco marker as an image "Aruco_Markers.jpg"
            path: path to where the aruco will be saved. If none specified will be saved in the same direcory of execution the code
            :param fig_filename: filename of arcuo file
        Returns:
            ArucoImage: numpy array with the aruco information

        """
        self.ArucoImage = 0

        aruco_dictionary = aruco.Dictionary_get(self.aruco_dict)
        img = aruco.drawMarker(aruco_dictionary, id, resolution)
        fig, ax = plt.subplots()
        ax.imshow(img, cmap=plt.cm.gray, interpolation="nearest")
        ax.axis("off")
        if show is True:
            fig.show()
        else:
            plt.close(fig)

        if save is True:
            if fig_filename is None:
                fig.savefig(path + "Aruco_Markers.png")
            else:
                fig.savefig(path + fig_filename)

        self.ArucoImage = img
        return self.ArucoImage

    def create_arucos_pdf(self, nx: int = 5, ny: int = 5, resolution: int = 50, path: str = './'):
        """
        Function to create a pdf file with nx X ny number of arucos and save them in specified path
        Args:
            nx: number of rows
            ny: number of columns
            resolution: resolution of the image (arucos)
            path: path to where the aruco will be saved. If none specified will be saved in the same direcory of execution the code
        Returns:
            image of the arucos and the saved pdf
        """
        aruco_dictionary = aruco.Dictionary_get(self.aruco_dict)
        fig = plt.figure()
        for i in range(1, nx * ny + 1):
            ax = fig.add_subplot(ny, nx, i)
            img = aruco.drawMarker(aruco_dictionary, i, resolution)
            ax.imshow(img, cmap='gray')
            ax.axis("off")
        fig.savefig(path + "markers.pdf")
        fig.show()
        return fig

    def plot_aruco_location(self, string_kind='RGB'):
        """ Function to visualize the location of the detected aruco markers in the image.
        Args:
            string_kind: IR -> Infrared detection of aruco and visualization in infrared image
                         RGB -> Detection of aruco in color space and visualization as color image
                         Projector -> Detection of projected arucos inside sandbox and visualization in color image
        Returns:
            image plot
        """
        plt.figure(figsize=(20, 20))
        if string_kind == 'IR':
            plt.imshow(self.kinect.get_ir_frame(), cmap="gray")
            plt.plot(self.ir_markers["Corners_IR_x"], self.ir_markers["Corners_IR_y"], "or")
            plt.show()
        elif string_kind == 'Projector':
            plt.imshow(self.kinect.get_color(), cmap="gray")
            plt.plot(self.projector_markers["Corners_projector_x"],
                     self.projector_markers["Corners_projector_y"], "or")
            plt.show()
        elif string_kind == 'RGB':
            # color = self.kinect.get_color()
            # color = color[self.kinect.calib.s_bottom:-self.kinect.calib.s_top,
            #       self.kinect.calib.s_left:-self.kinect.calib.s_right]
            plt.imshow(self.kinect.get_color())
            plt.plot(self.rgb_markers["Corners_RGB_x"], self.rgb_markers["Corners_RGB_y"], "or")
            plt.show()
        else:
            logger.warning('Select Type of projection -> IR, RGB or Projector')

    def convert_color_to_depth(self, ids, map, strg=None, data=None):
        """ Function to search in the previously created CoordinateMap - "create_CoordinateMap()" - the position of any
        detected aruco marker from the color space to the depth space.
        Args:
            strg: "Proj" or "Real". Select which type of aruco want to be converted
            ids: int. indicate the id of the aruco that want to be converted
            map: DataFrame. From the create_CoordinateMap() function
            data:
        Returns:
            value: Return the line from the CoordinateMap DataFrame showing the equivalence of its position in the color
            space to the depth space
        """
        color_data = map[['Color_x', 'Color_y']]
        if strg is not None:
            if strg == 'Proj':
                rgb = self.projector_markers
                rgb2 = rgb.loc[rgb['ids'] == ids]
                x_rgb = int(rgb2.Corners_projector_x.values)
                y_rgb = int(rgb2.Corners_projector_y.values)
            elif strg == 'Real':
                rgb = self.rgb_markers
                rgb2 = rgb.loc[rgb['ids'] == ids]
                x_rgb = int(rgb2.Corners_RGB_x.values)
                y_rgb = int(rgb2.Corners_RGB_y.values)

            distance = cdist([[x_rgb, y_rgb]], color_data)
            sorted_val = numpy.argsort(distance)[:][0]
            value = map.loc[sorted_val[0]]

        else:
            value = pd.DataFrame()
            if data is not None:
                for i in range(len(data)):
                    x_loc = data.loc[i].x
                    y_loc = data.loc[i].y

                    distance = cdist([[x_loc, y_loc]], color_data)
                    sorted_val = numpy.argsort(distance)[:][0]
                    value_i = pd.DataFrame(map.loc[sorted_val[0]]).T
                    value_i.insert(0, 'ids', data.loc[i].ids)
                    value = pd.concat([value, value_i], sort=False)

        return value

    def location_points(self, amount=None, plot=True):
        """ Function to search for a determined amount of arucos to introduce as a data point to the depth space
        Args:
            amount: specify the number of arucos to search
            plot: boolean to show the plot on color space and depth space if the mapped values are right
        Returns:
            point_markers: DataFrame with the id, x, y coordinates for the location of the aruco
        """
        labels = {"ids", "x", "y"}
        df = pd.DataFrame(columns=labels)

        if amount is not None:
            while len(df) < amount:
                frame = self.kinect.get_color()
                color = frame  # [self.rgb_markers.Corners_RGB_y.min():self.rgb_markers.Corners_RGB_y.max(),
                # self.rgb_markers.Corners_RGB_x.min():self.rgb_markers.Corners_RGB_x.max()]
                corners, ids, rejectedImgPoints = self.aruco_detect(color)

                if ids is not None:
                    for j in range(len(ids)):
                        if ids[j] not in df.ids.values:
                            x_loc, y_loc = self.get_location_marker(corners[j][0])
                            df_temp = pd.DataFrame({"ids": [ids[j][0]], "x": [x_loc], "y": [y_loc]})
                            df = pd.concat([df, df_temp], sort=False)

        df = df.reset_index(drop=True)
        self.point_markers = self.convert_color_to_depth(None, self.CoordinateMap, data=df)

        self.point_markers = self.point_markers.set_index(pd.Index(numpy.arange(len(self.point_markers))))

        if plot:
            color_crop = self.kinect.get_color()
            depth_crop = self.kinect.get_ir_frame()
            plt.figure(figsize=(20, 20))
            plt.subplot(2, 1, 1)
            plt.imshow(color_crop)
            plt.plot(self.point_markers.Color_x, self.point_markers.Color_y, "or")

            plt.subplot(2, 1, 2)
            plt.imshow(depth_crop)
            plt.plot(self.point_markers.Depth_x, self.point_markers.Depth_y, "or")
            plt.xlim(self.calib.s_left, depth_crop.shape[1] - self.calib.s_right)
            plt.ylim(depth_crop.shape[0] - self.calib.s_bottom, self.calib.s_top)
            plt.show()

        return self.point_markers

    def calibrate_camera_charucoBoard(self):
        """
        Method to obtain the camera intrinsic parameters to perform the aruco pose estimation
        Args:
        Returns:
            mtx: cameraMatrix Output 3x3 floating-point camera matrix
            dist: Output vector of distortion coefficient
            rvecs: Output vector of rotation vectors (see Rodrigues ) estimated for each board view
            tvecs: Output vector of translation vectors estimated for each pattern view.
        """

        aruco_dict = aruco.Dictionary_get(self.aruco_dict)
        board = aruco.CharucoBoard_create(7, 5, 1, .8, aruco_dict)
        images = []
        logger.info('Start moving randomly the aruco board')
        n = 400  # number of frames
        for i in range(n):
            frame = self.kinect.get_color()
            images.append(frame)
        logger.info("Stop moving the board")
        img_frame = numpy.array(images)[0::5]

        logger.info("Calculating Aruco location of %s images" % str(img_frame.shape[0]))
        allCorners = []
        allIds = []
        decimator = 0

        for im in img_frame:
            # print("=> Processing image {0}".format(im))
            # frame = cv2.imread(im)
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            res = cv2.aruco.detectMarkers(gray, aruco_dict)

            if len(res[0]) > 0:
                res2 = cv2.aruco.interpolateCornersCharuco(res[0], res[1], gray, board)
                if res2[1] is not None and res2[2] is not None and len(res2[1]) > 3 and decimator % 1 == 0:
                    allCorners.append(res2[1])
                    allIds.append(res2[2])

            decimator += 1
        imsize = gray.shape
        logger.info("Finish")

        logger.info("Calculating camera parameters")
        cameraMatrixInit = numpy.array([[2000., 0., imsize[0] / 2.],
                                        [0., 2000., imsize[1] / 2.],
                                        [0., 0., 1.]])

        distCoeffsInit = numpy.zeros((5, 1))
        flags = (cv2.CALIB_USE_INTRINSIC_GUESS + cv2.CALIB_RATIONAL_MODEL)
        ret, mtx, dist, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors = \
            cv2.aruco.calibrateCameraCharucoExtended(
                charucoCorners=allCorners,
                charucoIds=allIds,
                board=board,
                imageSize=imsize,
                cameraMatrix=cameraMatrixInit,
                distCoeffs=distCoeffsInit,
                flags=flags,
                criteria=(cv2.TERM_CRITERIA_EPS & cv2.TERM_CRITERIA_COUNT, 10000, 1e-9)
            )

        logger.info("Finish")

        self.calib.camera_mtx = mtx.tolist()
        self.calib.camera_dist = dist.tolist()

        return mtx, dist, rvecs, tvecs

    def real_time_poseEstimation(self):
        """
        Method that display real time detection of the aruco markers with the pose estimation and id of each
        Returns:
        """
        cv2.namedWindow("Aruco")
        # frame = self.kinect.get_color()
        frame = self.kinect.get_color()  # [270:900,640:1400]
        rval = True

        while rval:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            parameters = aruco.DetectorParameters_create()
            aruco_dict = aruco.Dictionary_get(self.aruco_dict)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            if ids is not None:
                frame = aruco.drawDetectedMarkers(frame, corners, ids)
                # side lenght of the marker in meter
                rvecs, tvecs, trash = aruco.estimatePoseSingleMarkers(corners, self._size_of_marker, self.mtx,
                                                                      self.dist)
                for i in range(len(tvecs)):
                    frame = aruco.drawAxis(frame, self.mtx, self.dist, rvecs[i], tvecs[i], self._length_of_axis)

            cv2.imshow("Aruco", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            # frame = self.kinect.get_color()
            frame = self.kinect.get_color()  # [270:900,640:1400]

            key = cv2.waitKey(20)
            if key == 27:  # exit on ESC
                break

        cv2.destroyWindow("Aruco")

    def drawPoseEstimation(self, df, frame):
        """
        Method that draws over the frame the coordinate system of each aruco marker in relation to the camera space
        Args:
            df: data frame containing the information of the tranlation and rotation vectors previously detected
            frame: frame to draw the coordinate sytems
        Returns:
            frame: with the resulting coordinate system

        """
        for i in range(len(df)):
            frame = aruco.drawAxis(frame,
                                   self.mtx,
                                   self.dist,
                                   df.loc[i].Rotation_vector[0],
                                   df.loc[i].Translation_vector[0],
                                   self._length_of_axis)
        return frame.get()

    def p_arucoMarker(self):
        """ Method to create an empty frame including 2 aruco markers.
        one in the upper left corner
        second one in the central part of the image.
        The id of the left-upper aruco is determined by the aruco position in the corner with resolution of 50
        The id in the center of the image is set to be 20 and resolution of 100
        Returns:
            Frame as numpy array with the information of the aruco markers
        """
        width = self.calib.p_frame_width
        height = self.calib.p_frame_height

        # Creation of the aruco images as numpy array with size of resolution
        img_LU = self.create_aruco_marker(id=self.corner_id_LU, resolution=50)
        img_c = self.create_aruco_marker(id=self.center_id, resolution=100)

        # creation of empty numpy array with the size of the frame projected
        god = numpy.zeros((height, width))
        god.fill(255)

        # Placement of aruco markers in the image.
        # The Left upper aruco will be placed with a constant offset distance in x and y from the corner
        god[height - img_LU.shape[0] - self.offset:height - self.offset, self.offset:img_LU.shape[1] + self.offset] = \
            numpy.flipud(img_LU)
        # The central aruco will be placed exactly in the middle of the image
        god[int(height / 2) - int(img_c.shape[0] / 2):
            int(height / 2) + int(img_c.shape[0] / 2),
            int(width / 2) - int(img_c.shape[0] / 2):
            int(width / 2) + int(img_c.shape[0] / 2)] = numpy.flipud(img_c)

        return god

    def move_image(self):
        """ Method to determine the distances between the aruco position in the corner of the sandbox in relation
        with the projected frame and the projected aruco marker.
        Returns:
            p_frame_left: new value to update the calib.p_frame_left
            p_frame_top: new value to update the calib.p_frame_top
            p_frame_width: new value to update the calib.p_frame_width
            p_frame_height: new value to update the calib.p_frame_height
        """

        # Find the 2 corners of the projection
        df_p, corner = self.find_markers_projector(amount=2)
        # save the location of the aruco from the calibration file
        df_r = self.aruco_corners

        # extract the position x and y of the projected aruco
        x_p = int(df_p.loc[df_p.ids == self.corner_id_LU].Corners_projector_x.values)
        y_p = int(df_p.loc[df_p.ids == self.corner_id_LU].Corners_projector_y.values)

        # extract the position x and y of the corner sandbox where the projected aruco should be
        x_r = int(df_r.loc[df_r.ids == self.corner_id_LU].Color_x.values)
        y_r = int(df_r.loc[df_r.ids == self.corner_id_LU].Color_y.values)

        # scale factor using the resolution of the central aruco -> 100 pixels represented in reality
        cor = numpy.asarray(corner)
        scale_factor_x = 100 / (cor[:, 0].max() - cor[:, 0].min())
        scale_factor_y = 100 / (cor[:, 1].max() - cor[:, 1].min())

        # move x and y direction the whole frame to make coincide the projected aruco with the corner
        x_move = int(((x_p - x_r) * scale_factor_x)) - self.offset - self.pixel_displacement
        y_move = int(((y_p - y_r) * scale_factor_y)) - self.offset - self.pixel_displacement

        # provide with the location of the
        p_frame_left = self.calib.p_frame_left - x_move
        p_frame_top = self.calib.p_frame_top - y_move

        # Now same procedure with the center aruco by changing the width and height of the frame to make
        # coincide the center projected aruco with the center of the sandbox.
        x_c = df_r.Color_x.mean()
        y_c = df_r.Color_y.mean()

        x_pc = int(df_p.loc[df_p.ids == self.center_id].Corners_projector_x.values)
        y_pc = int(df_p.loc[df_p.ids == self.center_id].Corners_projector_y.values)

        width_move = int((x_c - x_pc) * scale_factor_x) + x_move - self.pixel_displacement
        height_move = int((y_c - y_pc) * scale_factor_y) + y_move - self.pixel_displacement

        p_frame_width = self.calib.p_frame_width + width_move
        p_frame_height = self.calib.p_frame_height + height_move

        return p_frame_left, p_frame_top, p_frame_width, p_frame_height

    def crop_image_aruco(self):
        """ Method that takes the location of the 4 real corners and crop the sensor extensions to this frame
        Returns:
            s_top: new value to update the calib.s_top
            s_left: new value to update the calib.s_left
            s_bottom: new value to update the calib.s_bottom
            s_right: new value to update the calib.s_right
        """
        id_LU = self.aruco_corners.loc[self.aruco_corners.ids == self.corner_id_LU]
        id_DR = self.aruco_corners.loc[self.aruco_corners.ids == self.corner_id_DR]

        s_top = int(id_LU.Depth_y)
        s_left = int(id_LU.Depth_x)
        s_bottom = int(self.calib.s_height - id_DR.Depth_y)
        s_right = int(self.calib.s_width - id_DR.Depth_x)

        return s_top, s_left, s_bottom, s_right

    def load_corners_ids(self):
        """DEPRECATED"""
        if self.calib.aruco_corners is not None:
            self.aruco_corners = pd.read_json(self.calib.aruco_corners)
            temp = self.aruco_corners.loc[numpy.argsort(self.aruco_corners.Color_x)[:2]]
            self.corner_id_LU = int(temp.loc[temp.Color_y == temp.Color_y.min()].ids.values)
            temp1 = self.aruco_corners.loc[numpy.argsort(self.aruco_corners.Color_x)[-2:]]
            self.corner_id_DR = int(temp1.loc[temp1.Color_y == temp1.Color_y.max()].ids.values)
            self.center_id = 20

        # TODO: pixel distance from the frame corner so the aruco is always projected inside the sandbox
        self.offset = 100
        # TODO: move the image this amount of pixels so when moving the image is at this distance from the detected aruco
        self.pixel_displacement = 10
