# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.15

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /home/apozanco/Downloads/CLion-2019.3.5/clion-2019.3.5/bin/cmake/linux/bin/cmake

# The command to remove a file.
RM = /home/apozanco/Downloads/CLion-2019.3.5/clion-2019.3.5/bin/cmake/linux/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/apozanco/Desktop/GRS/src

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/apozanco/Desktop/GRS/src/cmake-build-debug

# Utility rule file for translate.

# Include the progress variables for this target.
include CMakeFiles/translate.dir/progress.make

translate: CMakeFiles/translate.dir/build.make
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --blue --bold "Copying translator module into output directory"
	/home/apozanco/Downloads/CLion-2019.3.5/clion-2019.3.5/bin/cmake/linux/bin/cmake -E copy_directory /home/apozanco/Desktop/GRS/src/translate /home/apozanco/Desktop/GRS/src/cmake-build-debug/bin/./translate
.PHONY : translate

# Rule to build all files generated by this target.
CMakeFiles/translate.dir/build: translate

.PHONY : CMakeFiles/translate.dir/build

CMakeFiles/translate.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/translate.dir/cmake_clean.cmake
.PHONY : CMakeFiles/translate.dir/clean

CMakeFiles/translate.dir/depend:
	cd /home/apozanco/Desktop/GRS/src/cmake-build-debug && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/apozanco/Desktop/GRS/src /home/apozanco/Desktop/GRS/src /home/apozanco/Desktop/GRS/src/cmake-build-debug /home/apozanco/Desktop/GRS/src/cmake-build-debug /home/apozanco/Desktop/GRS/src/cmake-build-debug/CMakeFiles/translate.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/translate.dir/depend

