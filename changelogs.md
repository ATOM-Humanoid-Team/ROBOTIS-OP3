# Changelogs

## ROS2 Migration
- Migrated all modules to ROS2:
  - `op3_action_module`
  - `op3_balance_control`
  - `op3_base_module`
  - `op3_direct_control_module`
  - `op3_head_control_module`
  - `op3_kinematics_dynamics`
  - `op3_localization`
  - `op3_walking_module`
  - `op3_tuning_module`
  - `op3_online_walking_module`
  - `open_cr_module`
  - `op3_manager`
- Standardized module naming (removed `op3_` prefix from internal module names).
- Cleaned up `package.xml` and `CMakeLists.txt` for ROS2 compatibility.
- Added missing exports to `package.xml`.
- Modified `robotis_op3` metapackage and removed unnecessary metapackages.

## Features & Enhancements
- Updated walking parameters and set default `balance_enable` to `true`.
- Added offset initialization pose (Page 255).
- Mapped humanoid kicking motions in `op3_action_module` `motion_4095.bin`: Page 120 (`l_kick_170519`) and Page 121 (`r_kick_170519`).
- Improved walking parameter tuning.
- Changed default offset file location to `op3_manager/data/offset.yaml`.
- Added support for `baudrate` as a parameter in `op3_manager`.
- Renamed `op3_gazebo.launch.py` to `op3_simulation.launch.py`.
- Removed `op3_localization` from `op3_manager.launch.py`.

## Bug Fixes & Optimizations
- Fixed thread management issues in `base_module` when switching between `ini_pose` or `tune_pose`.
- Fixed crash caused by calling `result.get()` twice after `async_send_request`.
- Fixed issues with `spin_until_future_complete()`.
- Corrected mass properties in `op3_kinematics_dynamics`.
- Improved joint gain management (restoring original values when stopped).
- Fixed double-to-int assignment issues.
- Cleaned up dependencies on `eigen` and `cmake_modules`.
- Removed various build warnings.
- Improved code indentation and formatting.
