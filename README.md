# jazzy_gz

A ROS 2 **Jazzy** package for simulating and driving a custom differential-drive robot in **Gazebo (`ros_gz`)**, with full support for real-hardware bring-up (RPLidar + USB camera), `ros2_control`, Nav2 autonomous navigation, and SLAM Toolbox mapping.

This package provides the robot description, simulation world, sensor bridges, and launch files needed to run the robot both **in simulation** and **on real hardware**, using the same URDF, controllers, and navigation stack.

---

## What's in this package

| Folder | Contents |
|---|---|
| `description/` | Robot URDF/xacro files — chassis, wheels, casters, LiDAR, camera, `ros2_control` hardware interface, and Gazebo plugin bindings |
| `meshes/` | STL mesh files for the robot's physical links (base, wheels, casters, LiDAR mount) |
| `worlds/` | Gazebo `.sdf` world files, including a custom environment world and an empty world for quick testing |
| `launch/` | All ROS 2 launch files (see below) |
| `config/` | Controller config, ROS–Gazebo topic bridge config, Nav2 parameters, SLAM Toolbox parameters, `twist_mux` config, a saved map, and an RViz view |
| `CMakeLists.txt`, `package.xml` | Standard `ament_cmake` ROS 2 package files |

---

## Robot overview

- **Drive type:** Differential drive (2 driven wheels + front/back casters)
- **Sensors:** 2D LiDAR (RPLidar) + USB camera
- **Simulation:** Spawned into Gazebo via `ros_gz_sim`, controlled through `gz_ros2_control` + `diff_drive_controller`
- **Real hardware:** Same URDF and controllers used with `robot_state_publisher`; LiDAR and camera launched via dedicated real-hardware launch files
- **Navigation:** Nav2 stack (planner/controller/costmaps) + SLAM Toolbox for mapping, with a pre-saved map (`custom_map.yaml` / `.pgm`) available for localization
- **Command arbitration:** `twist_mux` merges velocity commands (e.g. joystick vs. Nav2) into a single `/cmd_vel`

---

## Dependencies

Install these ROS 2 Jazzy packages before building:

```bash
sudo apt install \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-image \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-diff-drive-controller \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-twist-mux \
  ros-jazzy-twist-stamper \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-xacro
```

For real hardware, you'll also need `rplidar_ros` and `usb_cam`.

---

## Building

```bash
# From your ROS 2 workspace root (e.g. ~/ros2_ws)
cd ~/ros2_ws/src
git clone https://github.com/mdabutalharoni/jazzy_gz.git
cd ~/ros2_ws
colcon build --packages-select jazzy_gz
source install/setup.bash
```

---

## Running in simulation

Launch the full simulation stack — Gazebo, robot spawn, controllers, ROS–Gazebo bridge, and `twist_mux`:

```bash
ros2 launch jazzy_gz launch_sim.launch.py
```

Optional arguments:

| Argument | Default | Description |
|---|---|---|
| `world` | `empty.sdf` | Which world file to load (use `jazzy_gz_world.sdf` or `environment_world.sdf` from `worlds/` for the custom environments) |
| `use_ros2_control` | `true` | Whether to use `ros2_control` for the drivetrain |

Example, loading the custom world:

```bash
ros2 launch jazzy_gz launch_sim.launch.py world:=jazzy_gz_world.sdf
```

Drive the robot manually once it's spawned:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel_key
```

*(adjust the remap to match whichever `twist_mux` input topic you're using — check `config/twist_mux.yaml`)*

---

## Running on real hardware

1. **Publish the robot description only** (no Gazebo):
   ```bash
   ros2 launch jazzy_gz rsp.launch.py use_sim_time:=false
   ```

2. **Start the RPLidar:**
   ```bash
   ros2 launch jazzy_gz rplidar.launch.py serial_port:=/dev/ttyUSB0
   ```
   Default serial port and baud rate (256000) are set for a CP2102-based RPLidar — override with `serial_port:=` and `serial_baudrate:=` if yours differs.

3. **Start the USB camera:**
   ```bash
   ros2 launch jazzy_gz usb_camera.launch.py video_device:=/dev/video0
   ```

---

## Mapping (SLAM)

With the robot running (sim or real) and LiDAR active, start SLAM Toolbox using the provided parameters:

```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=$(ros2 pkg prefix jazzy_gz)/share/jazzy_gz/config/mapper_params_online_async.yaml \
  use_sim_time:=true
```

Save the resulting map once you've driven the robot around the environment:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

---

## Autonomous navigation (Nav2)

Once you have a saved map (or use the included `config/custom_map.yaml`), bring up Nav2 for localization + path planning:

```bash
ros2 launch nav2_bringup bringup_launch.py \
  map:=$(ros2 pkg prefix jazzy_gz)/share/jazzy_gz/config/custom_map.yaml \
  params_file:=$(ros2 pkg prefix jazzy_gz)/share/jazzy_gz/config/nav2_params.yaml \
  use_sim_time:=true
```

Visualize everything (robot model, LiDAR scan, costmaps, planned path) using the included RViz config:

```bash
rviz2 -d $(ros2 pkg prefix jazzy_gz)/share/jazzy_gz/config/view_bot.rviz
```

---

## Package structure at a glance

```
jazzy_gz/
├── description/
│   ├── robot.urdf.xacro        # Top-level robot description
│   ├── robot_core.xacro        # Chassis, wheels, casters, links/joints
│   ├── camera.xacro            # Camera sensor + Gazebo plugin
│   ├── lidar.xacro             # LiDAR sensor + Gazebo plugin
│   ├── ros2_control.xacro      # ros2_control hardware interface definitions
│   └── gazebo_control.xacro    # gz_ros2_control Gazebo plugin binding
├── meshes/                     # STL files referenced by robot_core.xacro
├── worlds/                     # empty.world, environment_world.sdf, jazzy_gz_world.sdf
├── launch/
│   ├── launch_sim.launch.py    # Full sim bring-up (Gazebo + spawn + controllers + bridge)
│   ├── rsp.launch.py           # robot_state_publisher only (sim or real)
│   ├── rplidar.launch.py       # Real RPLidar hardware driver
│   └── usb_camera.launch.py    # Real USB camera driver
├── config/
│   ├── gz_bridge.yaml          # ROS <-> Gazebo topic bridge definitions
│   ├── my_controllers.yaml     # diff_drive_controller / joint_state_broadcaster config
│   ├── twist_mux.yaml          # cmd_vel input priority/arbitration
│   ├── mapper_params_online_async.yaml  # SLAM Toolbox params
│   ├── nav2_params.yaml        # Nav2 stack params
│   ├── custom_map.yaml / .pgm  # Pre-saved occupancy map
│   └── view_bot.rviz           # RViz display config
├── CMakeLists.txt
└── package.xml
```

---

## Notes

- This package is based on the `joshnewans/my_bot` ROS 2/Gazebo template structure, adapted for a custom differential-drive robot with real-hardware bring-up support.
- `GZ_SIM_RESOURCE_PATH` is set automatically in `launch_sim.launch.py` so Gazebo can resolve `package://jazzy_gz/meshes/...` paths — no manual environment setup needed for simulation.
- The `use_ros2_control` launch argument lets you toggle between `ros2_control`-driven and legacy Gazebo diff-drive-plugin-driven control, useful for isolating issues during development.

## License

Apache-2.0 — see [LICENSE.md](LICENSE.md).
