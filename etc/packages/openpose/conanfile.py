from conans import ConanFile, CMake, tools
import os, shutil


class OpenPoseConan(ConanFile):
    name = "openpose"
    version = "1.4.0"
    license = ""
    homepage = " https://github.com/CMU-Perceptual-Computing-Lab/openpose"
    url = " https://github.com/CMU-Perceptual-Computing-Lab/openpose"
    description = ""
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "build_docs": [True, False],
        "build_examples": [True, False],
        "build_python": [True, False],
        "build_caffe": [True, False],
        "download_body_mpi_model": [True, False],
        "download_body_coco_model": [True, False],
        "download_body_25_model": [True, False],
        "download_face_model": [True, False],
        "download_hand_model": [True, False],
    }
    default_options = ("shared=True", "build_docs=False", "build_examples=False",
                       "build_python=False", "build_caffe=False", "download_body_mpi_model=False",
                       "download_body_coco_model=False", "download_body_25_model=False",
                       "download_face_model=False", "download_hand_model=False")

    generators = "cmake"

    def requirements(self):
        self.requires("caffe/1.0.0@is/stable")
        self.requires("opencv/3.4.2@is/stable")

    def system_requirements(self):
        pass

    def configure(self):
        self.options["opencv"].shared = True
        self.options["opencv"].with_zlib = False

    def source(self):
        tools.get('{}/archive/v{}.tar.gz'.format(self.url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.name)

        tools.replace_in_file(
            "openpose/CMakeLists.txt", "project(OpenPose VERSION ${OpenPose_VERSION})",
            '''project(OpenPose VERSION ${OpenPose_VERSION})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        tools.replace_in_file(
            "openpose/CMakeLists.txt", "project(OpenPose)", '''project(OpenPose)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        caffe_include_dirs = os.path.join(self.deps_cpp_info["caffe"].rootpath, 'include')
        caffe_libs = os.path.join(self.deps_cpp_info["caffe"].rootpath, 'lib/libcaffe.so')

        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['BUILD_DOCS'] = self.options.build_docs
        cmake.definitions['BUILD_EXAMPLES'] = self.options.build_examples
        cmake.definitions['BUILD_CAFFE'] = self.options.build_caffe
        cmake.definitions['Caffe_INCLUDE_DIRS'] = caffe_include_dirs
        cmake.definitions['Caffe_LIBS'] = caffe_libs
        cmake.definitions['CUDA_ARCH'] = "All"
        cmake.definitions["DOWNLOAD_BODY_MPI_MODEL"] = self.options.download_body_mpi_model
        cmake.definitions["DOWNLOAD_BODY_COCO_MODEL"] = self.options.download_body_coco_model
        cmake.definitions["DOWNLOAD_BODY_25_MODEL"] = self.options.download_body_25_model
        cmake.definitions["DOWNLOAD_FACE_MODEL"] = self.options.download_face_model
        cmake.definitions["DOWNLOAD_HAND_MODEL"] = self.options.download_hand_model

        cmake.configure(source_folder="openpose")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        libs = [
            "openpose",
            "openpose_3d",
            "openpose_calibration",
            "openpose_core",
            "openpose_face",
            "openpose_filestream",
            "openpose_gpu",
            "openpose_gui",
            "openpose_hand",
            "openpose_net",
            "openpose_pose",
            "openpose_producer",
            "openpose_thread",
            "openpose_tracking",
            "openpose_utilities",
            "openpose_wrapper",
        ]
        self.cpp_info.libs = libs