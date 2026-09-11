# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_amcl_loc_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED amcl_loc_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(amcl_loc_FOUND FALSE)
  elseif(NOT amcl_loc_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(amcl_loc_FOUND FALSE)
  endif()
  return()
endif()
set(_amcl_loc_CONFIG_INCLUDED TRUE)

# output package information
if(NOT amcl_loc_FIND_QUIETLY)
  message(STATUS "Found amcl_loc: 0.0.0 (${amcl_loc_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'amcl_loc' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT amcl_loc_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(amcl_loc_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${amcl_loc_DIR}/${_extra}")
endforeach()
