if(MODULES MATCHES "dynamic")
  message(FATAL_ERROR "mod-custom-server Classless integration requires -DMODULES=static.")
endif()
