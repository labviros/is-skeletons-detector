from conans import ConanFile, CMake, tools


class SkeletonsDetectorServiceConan(ConanFile):
    name = "is-skeletons-detector"
    version = "0.0.1"
    license = "MIT"
    url = ""
    description = ""
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_tests": [True, False],
    }
    default_options = "shared=True", "fPIC=True", "build_tests=False"
    generators = "cmake", "cmake_find_package", "cmake_paths", "virtualrunenv"
    requires = (
        "is-msgs/1.1.8@is/stable",
        "is-wire/1.1.4@is/stable",
        "opencv/3.4.2@is/stable",
        "openpose/1.4.0@is/stable",
    )
    exports_sources = "*"

    def build_requirements(self):
        pass

    def configure(self):
        self.options["is-msgs"].shared = True
        self.options["is-wire"].shared = True
        self.options["opencv"].shared = True
        self.options["opencv"].with_qt = False
        self.options["opencv"].with_zlib = False


    def build(self):
        cmake = CMake(self, generator='Ninja')
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = ["is-skeletons-detector"]
