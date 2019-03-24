from conans import ConanFile, CMake, tools
import os, shutil


class CaffeConan(ConanFile):
    name = "caffe"
    version = "1.0.0"
    git_version = "9453eb00f6073ab9091f8a3a973538c7bdcb6785"
    license = ""
    homepage = " https://github.com/CMU-Perceptual-Computing-Lab/caffe"
    url = " https://github.com/CMU-Perceptual-Computing-Lab/caffe"
    description = ""
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "build_docs": [True, False],
        "build_python": [True, False],
        "build_python_layer": [True, False],
        "build_matlab": [True, False],
    }
    default_options = ("shared=True", "build_docs=False", "build_python=False",
                       "build_python_layer=False", "build_matlab=False")

    generators = "cmake"

    def requirements(self):
        self.requires("opencv/3.4.2@is/stable")
        self.requires("protobuf/3.6.1@bincrafters/stable")
        self.requires("protoc_installer/3.6.1@bincrafters/stable")
        self.requires("boost/1.66.0@conan/stable")

    def system_requirements(self):
        dependencies = [
            "libatlas-base-dev", "libatlas-dev", "libgflags-dev", "libgoogle-glog-dev",
            "libhdf5-dev", "libsnappy-dev", "libleveldb-dev", "liblmdb-dev"
        ]

        installer = tools.SystemPackageTool()
        installer.update()  # Update the package database
        installer.install(" ".join(dependencies))  # Install the package

    def configure(self):
        self.options["protobuf"].shared = True
        self.options["opencv"].shared = True
        self.options["opencv"].with_zlib = False
        self.options["boost"].shared = True

    def source(self):
        tools.get('{}/archive/{}.tar.gz'.format(self.url, self.git_version))
        extracted_dir = self.name + "-" + self.git_version
        os.rename(extracted_dir, self.name)

        def empty_cmake(folder):
            shutil.rmtree(os.path.join(self.name, folder))
            os.mkdir(os.path.join(self.name, folder))
            open(os.path.join(self.name, folder, 'CMakeLists.txt'), 'w').close()

        empty_cmake('examples')
        empty_cmake('tools')

        tools.replace_in_file(
            "caffe/CMakeLists.txt", "project(Caffe C CXX)", '''project(Caffe C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self, set_cmake_flags=True)
        cmake.definitions['CMAKE_CXX_FLAGS'] = '-std=c++11'
        cmake.definitions['BUILD_docs'] = self.options.build_docs
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['USE_CUDNN'] = True
        cmake.definitions['USE_OPENCV'] = True
        cmake.definitions['BUILD_python'] = self.options.build_python
        cmake.definitions['BUILD_python_layer'] = self.options.build_python_layer
        cmake.definitions['BUILD_matlab'] = self.options.build_matlab
        cmake.definitions['CUDA_ARCH_NAME'] = "All"
        cmake.definitions['CUDA_NVCC_FLAGS'] = "-O3"

        cmake.configure(source_folder="caffe")
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["caffe", "caffeproto"]