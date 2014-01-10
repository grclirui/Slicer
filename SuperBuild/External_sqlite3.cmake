
set(proj sqlite3)

# Set dependency list
set(${proj}_DEPENDENCIES "")

# Include dependent projects if any
ExternalProject_Include_Dependencies(${proj} PROJECT_VAR proj DEPENDS_VAR ${proj}_DEPENDENCIES)

if(${CMAKE_PROJECT_NAME}_USE_SYSTEM_${proj})
  message(FATAL_ERROR "Should not build agaginst system sqlite3")
  unset(sqlite3_DIR CACHE)
  find_package(sqlite3 REQUIRED)
  set(sqlite3_INCLUDE_DIR ${sqlite3_INCLUDE_DIRS})
  set(sqlite3_LIBRARY ${sqlite3_LIBRARIES})
endif()

#Sanity checks
if(DEFINED sqlite3_DIR AND NOT EXISTS${sqlite3_DIR})
  message(FATAL_ERROR "sqlite3_DIR variable is defined but corresponds to non-existing directory")
endif()

if(NOT DEFINED sqlite3_DIR)
  #message(STATUS "${__indent}Adding project ${proj}")

  SET(EXTERNAL_PROJECT_OPTIONAL_ARGS)

  # Set CMake OSX variable to pass down the external project
  if (APPLE)
    list(APPEND CMAKE_OSX_EXTERNAL_PROJECT_ARGS
      -DCMAKE_OSX_ARCHITECTURES=${CMAKE_OSX_ARCHITECTURES}
      -DCMAKE_OSX_SYSROOT=${CMAKE_OSX_SYSROOT}
      -DCMAKE_OSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET})
  endif()

  if(NOT CMAKE_CONFIGURATION_TYPES)
    list(APPEND EXTERNAL_PROJECT_OPTIONAL_ARGS
      -DCMAKE_BUILD_TYPE:STRING=${CMAKE_BUILD_TYPE})
  endif()

  if(NOT DEFINED git_protocol)
    set(git_protocol "git")
  endif()

  set(EP_SOURCE_DIR ${CMAKE_BINARY_DIR}/${proj})
  set(EP_BINARY_DIR ${CMAKE_BINARY_DIR}/${proj}-build)
  set(EP_INSTALL_DIR ${CMAKE_BINARY_DIR}/${proj}-install)
  
  ExternalProject_Add(${proj}
    GIT_REPOSITORY "${git_protocol}://github.com/grclirui/sqlite3.git"
    GIT_TAG "0b32ad39a1e422a983a5e43354003a0d1df48778" 
    SOURCE_DIR ${EP_SOURCE_DIR}
    BINARY_DIR ${EP_BINARY_DIR}
    INSTALL_DIR ${EP_INSTALL_DIR}
    CMAKE_GENERATOR${gen}
    CMAKE_ARGS
      -DCMAKE_CXX_COMPILER:FILEPATH=${CMAKE_CXX_COMPILER}
      -DCMAKE_CXX_FLAGS:STRING=${ep_common_cxx_flags}
      -DCMAKE_C_COMPILER:FILEPATH=${CMAKE_C_COMPILER}
      -DCMAKE_C_FLAGS:STRING=${ep_common_c_flags}
      -DBUILD_TESTING:BOOL=OFF
      -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR>
      -Dsqlite3_LIBRARY_PROPERTIES:STRING=${Slicer_LIBRARY_PROPERTIES}
      -Dsqlite3_INSTALL_BIN_DIR:PATH=${Slicer_INSTALL_LIB_DIR}
      -Dsqlite3_INSTALL_LIB_DIR:PATH=${Slicer_INSTALL_LIB_DIR}
      -Dsqlite3_INSTALL_NO_DEVELOPMENT:BOOL=${Slicer_INSTALL_NO_DEVELOPMENT}
      INSTALL_COMMAND ""
    DEPENDS
      ${${proj}_DEPENDENCIES}
    )
  set(sqlite3_DIR ${EP_BINARY_DIR})
  set(SLICER_SQLITE3_ROOT ${sqlite3_DIR})
  set(SLICER_SQLITE3_INCLUDE_DIR ${EP_SOURCE_DIR})
  if(WIN32)
    SET(SLICER_SQLITE3_LIBRARY   ${sqlite3_DIR}/sqlite3.lib)
  elseif(APPLE)
    SET(SLICER_SQLITE3_LIBRARY   ${sqlite3_DIR}/libsqlite3.dylib)
  elseif(UNIX)
    SET(SLICER_SQLITE3_LIBRARY   ${sqlite3_DIR}/libsqlite3.so)
  endif()
else()
  ExternalProject_Add_Empty(${proj} DEPENDS ${${proj}_DEPENDENCIES})
endif()

mark_as_superbuild(
  VARS
    SLICER_SQLITE3_INCLUDE_DIR:PATH
    SLICER_SQLITE3_LIBRARY:FILEPATH
    SLICER_SQLITE3_ROOT:PATH
  LABELS "FIND_PACKAGE"
  )
ExternalProject_Message(${proj} "sqlite3_DIR:${sqlite3_DIR}")
ExternalProject_Message(${proj} "SLICER_SQLITE3_INCLUDE_DIR:${SLICER_SQLITE3_INCLUDE_DIR}")
ExternalProject_Message(${proj} "SLICER_SQLITE3_LIBRARY:${SLICER_SQLITE3_LIBRARY}")
