#!/usr/bin/env python
"""Define the Bullet Simulator API.

This is the main interface that communicates with the PyBullet simulator [1]. By defining this interface, it allows to
decouple the PyRoboLearn framework from the simulator. It also converts some data types to the ones required by
PyBullet. For instance, some methods in PyBullet do not accepts numpy arrays but only lists. The interface provided
here makes the necessary conversions.

The signature of each method defined here are inspired by [1,2] but in accordance with the PEP8 style guide [3].
Parts of the documentation for the methods have been copied-pasted from [2] for completeness purposes.

Dependencies in PRL:
* `pyrobolearn.simulators.simulator.Simulator`

References:
    [1] PyBullet: https://pybullet.org
    [2] PyBullet Quickstart Guide: https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA
    [3] PEP8: https://www.python.org/dev/peps/pep-0008/
"""

import time
import numpy as np
import quaternion
from pyrobolearn.utils.converter import NumpyListConverter, QuaternionListConverter

import pybullet
from pybullet_envs.bullet.bullet_client import BulletClient

from simulator import Simulator


__author__ = "Brian Delhaisse"
__copyright__ = "Copyright 2018, PyRoboLearn"
__credits__ = ["Brian Delhaisse"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Brian Delhaisse"
__email__ = "briandelhaisse@gmail.com"
__status__ = "Development"


class Bullet(Simulator):
    r"""PyBullet simulator.

    This is a wrapper around the PyBullet API [1]. For many methods, it is just the same as calling directly the
    original methods. However for several ones, it converts the data into the correct data type.
    For instance, some methods in PyBullet returns a matrix :math:`NxM` in a list format with length :math:`NxM`,
    instead of a numpy array. Other data types includes vectors, quaternions, and others which are all returned as
    list. The problem with this approach is that we first have to convert the data in our code in order to operate
    on it. A converter can be specified which converts into the desired format. If none, it will convert the data
    into numpy arrays instead of lists.

    Also, this wrapper enforces consistency. For instance, all the given and produced angles are represented in
    radians, and not in degrees. Some original `pybullet` methods require angles expressed in radians, and others in
    degrees.

    The class also presents the documentation of each method which relieve us to check the user guide [1].
    Most of the documentation has been copied-pasted from [1], written by Erwin Coumans and Yunfei Bai.
    Also, Some extra methods have been defined.

    Finally, note that this API is incompatible with the original `pybullet`, i.e. it is not interchangeable in the
    code! In addition, using this interface allows us to easily switch with other `Simulator` APIs, and make it more
    modular if the signature of the original PyBullet library change.

    In the following documentation:
    * `vec3` specifies a list/tuple/np.array of 3 floats
    * `quat` specifies a list/tuple/np.quaternion of 4 floats

    Examples:
        sim = Bullet()

    References:
        [1] PyBullet Quickstart Guide: https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA
            Erwin Coumans and Yunfei Bai, 2017/2018
    """

    def __init__(self, render=True):  # , converter=None):
        super(Bullet, self).__init__()

        # Connect to pybullet
        if render:
            self.sim = BulletClient(connection_mode=pybullet.GUI)
        else:
            self.sim = BulletClient(connection_mode=pybullet.DIRECT)
        self.id = self.sim._client

        # Converters
        # if converter is None:
        self.conv = NumpyListConverter()
        self.quat_conv = QuaternionListConverter(convention=1)

    # def __del__(self):
    #     """Clean up connection if not already done.
    #
    #     Copied-pasted from `pybullet_envs/bullet/bullet_client.py`.
    #     """
    #     try:
    #         pybullet.disconnect(physicsClientId=self._client)
    #     except pybullet.error:
    #         pass
    #
    # def __getattr__(self, name):
    #     """Inject the client id into Bullet functions.
    #
    #     Copied-pasted from `pybullet_envs/bullet/bullet_client.py`.
    #     """
    #     attribute = getattr(pybullet, name)
    #     if inspect.isbuiltin(attribute):
    #         attribute = functools.partial(attribute, physicsClientId=self._client)
    #     return attribute

    ##############
    # Properties #
    ##############

    @property
    def version(self):
        """Return the version of the simulator in a year-month-day format."""
        return self.sim.getAPIVersion()

    ###########
    # Methods #
    ###########

    ##############
    # Simulators #
    ##############

    def reset(self):
        """Reset the simulator.

        "It will remove all objects from the world and reset the world to initial conditions." [1]
        """
        self.sim.resetSimulation()

    def step(self, sleep_time=0.):
        """Perform a step in the simulator.

        "stepSimulation will perform all the actions in a single forward dynamics simulation step such as collision
        detection, constraint solving and integration. The default timestep is 1/240 second, it can be changed using
        the setTimeStep or setPhysicsEngineParameter API." [1]
        """
        self.sim.stepSimulation()
        time.sleep(sleep_time)

    def render(self, flag=True):
        """Render the GUI.

        Args:
            flag (bool): If True, it will render the simulator by enabling the GUI.
        """
        if flag:
            self.sim.configureDebugVisualizer(self.sim.COV_ENABLE_RENDERING,  1)
        else:
            self.sim.configureDebugVisualizer(self.sim.COV_ENABLE_RENDERING, 0)

    def set_time_step(self, time_step):
        """Set the specified time step in the simulator.

        "Warning: in many cases it is best to leave the timeStep to default, which is 240Hz. Several parameters are
        tuned with this value in mind. For example the number of solver iterations and the error reduction parameters
        (erp) for contact, friction and non-contact joints are related to the time step. If you change the time step,
        you may need to re-tune those values accordingly, especially the erp values.
        You can set the physics engine timestep that is used when calling 'stepSimulation'. It is best to only call
        this method at the start of a simulation. Don't change this time step regularly. setTimeStep can also be
        achieved using the new setPhysicsEngineParameter API." [1]

        Args:
            time_step (float): Each time you call 'step' the time step will proceed with 'time_step'.
        """
        self.sim.setTimeStep(timeStep=time_step)

    def set_real_time(self, flag=True):
        """Enable/disable real time in the simulator.

        "By default, the physics server will not step the simulation, unless you explicitly send a 'stepSimulation'
        command. This way you can maintain control determinism of the simulation. It is possible to run the simulation
        in real-time by letting the physics server automatically step the simulation according to its real-time-clock
        (RTC) using the setRealTimeSimulation command. If you enable the real-time simulation, you don't need to call
        'stepSimulation'.

        Note that setRealTimeSimulation has no effect in DIRECT mode: in DIRECT mode the physics server and client
        happen in the same thread and you trigger every command. In GUI mode and in Virtual Reality mode, and TCP/UDP
        mode, the physics server runs in a separate thread from the client (PyBullet), and setRealTimeSimulation
        allows the physicsserver  thread to add additional calls to stepSimulation." [1]

        Args:
            flag (bool): If True, it will enable the real-time simulation. If False, it will disable it.
        """
        self.sim.setRealTimeSimulation(enableRealTimeSimulation=int(flag))

    def pause(self):
        """Pause the simulator if in real-time."""
        self.set_real_time(False)

    def unpause(self):
        """Unpause the simulator if in real-time."""
        self.set_real_time(True)

    def get_physics_properties(self):
        """Get the physics engine parameters.

        Returns:
            dict: dictionary containing the following tags with their corresponding values: ['gravityAccelerationX',
                'useRealTimeSimulation', 'gravityAccelerationZ', 'numSolverIterations', 'gravityAccelerationY',
                'numSubSteps', 'fixedTimeStep']
        """
        return self.sim.getPhysicsEngineParameters()

    def set_physics_properties(self, time_step=None, num_solver_iterations=None, use_split_impulse=None,
                               split_impulse_penetration_threshold=None, num_sub_steps=None,
                               collision_filter_mode=None, contact_breaking_threshold=None, max_num_cmd_per_1ms=None,
                               enable_file_caching=None, restitution_velocity_threshold=None, erp=None,
                               contact_erp=None, friction_erp=None, enable_cone_friction=None,
                               deterministic_overlapping_pairs=None, solver_residual_threshold=None):
        """Set the physics engine parameters.

        Args:
            time_step (float): See the warning in the `set_time_step` section. Physics engine timestep in
                fraction of seconds, each time you call `step` simulated time will progress this amount.
                Same as `set_time_step`. Default to 1./240.
            num_solver_iterations (int): Choose the maximum number of constraint solver iterations. If the
                `solver_residual_threshold` is reached, the solver may terminate before the `num_solver_iterations`.
                Default to 50.
            use_split_impulse (int): Advanced feature, only when using maximal coordinates: split the positional
                constraint solving and velocity constraint solving in two stages, to prevent huge penetration recovery
                forces.
            split_impulse_penetration_threshold (float): Related to 'useSplitImpulse': if the penetration for a
                particular contact constraint is less than this specified threshold, no split impulse will happen for
                that contact.
            num_sub_steps (int): Subdivide the physics simulation step further by 'numSubSteps'. This will trade
                performance over accuracy.
            collision_filter_mode (int): Use 0 for default collision filter: (group A&maskB) AND (groupB&maskA).
                Use 1 to switch to the OR collision filter: (group A&maskB) OR (groupB&maskA).
            contact_breaking_threshold (float): Contact points with distance exceeding this threshold are not
                processed by the LCP solver. In addition, AABBs are extended by this number. Defaults to 0.02 in
                Bullet 2.x.
            max_num_cmd_per_1ms (int): Experimental: add 1ms sleep if the number of commands executed exceed this
                threshold
            enable_file_caching (bool): Set to 0 to disable file caching, such as .obj wavefront file loading
            restitution_velocity_threshold (float): If relative velocity is below this threshold, restitution will be
                zero.
            erp (float): constraint error reduction parameter (non-contact, non-friction)
            contact_erp (float): contact error reduction parameter
            friction_erp (float): friction error reduction parameter (when positional friction anchors are enabled)
            enable_cone_friction (bool): Set to False to disable implicit cone friction and use pyramid approximation
                (cone is default)
            deterministic_overlapping_pairs (bool): Set to True to enable and False to disable sorting of overlapping
                pairs (backward compatibility setting).
            solver_residual_threshold (float): velocity threshold, if the maximum velocity-level error for each
                constraint is below this threshold the solver will terminate (unless the solver hits the
                numSolverIterations). Default value is 1e-7.
        """
        kwargs = {}
        if time_step is not None:
            kwargs['fixedTimeStep'] = time_step
        if num_solver_iterations is not None:
            kwargs['numSolverIterations'] = num_solver_iterations
        if use_split_impulse is not None:
            kwargs['useSplitImpulse'] = use_split_impulse
        if split_impulse_penetration_threshold is not None:
            kwargs['splitImpulsePenetrationThreshold'] = split_impulse_penetration_threshold
        if num_sub_steps is not None:
            kwargs['numSubSteps'] = num_sub_steps
        if collision_filter_mode is not None:
            kwargs['collisionFilterMode'] = collision_filter_mode
        if contact_breaking_threshold is not None:
            kwargs['contactBreakingThreshold'] = contact_breaking_threshold
        if max_num_cmd_per_1ms is not None:
            kwargs['maxNumCmdPer1ms'] = max_num_cmd_per_1ms
        if enable_file_caching is not None:
            kwargs['enableFileCaching'] = enable_file_caching
        if restitution_velocity_threshold is not None:
            kwargs['restitutionVelocityThreshold'] = restitution_velocity_threshold
        if erp is not None:
            kwargs['erp'] = erp
        if contact_erp is not None:
            kwargs['contactERP'] = contact_erp
        if friction_erp is not None:
            kwargs['frictionERP'] = friction_erp
        if enable_cone_friction is not None:
            kwargs['enableConeFriction'] = int(enable_cone_friction)
        if deterministic_overlapping_pairs is not None:
            kwargs['deterministicOverlappingPairs'] = int(deterministic_overlapping_pairs)
        if solver_residual_threshold is not None:
            kwargs['solverResidualThreshold'] = solver_residual_threshold

        self.sim.setPhysicsEngineParameter(**kwargs)

    def start_logging(self, logging_type, filename, object_unique_ids, max_log_dof, body_unique_id_A, body_unique_id_B,
                      link_index_A, link_index_B, device_type_filter, log_flags):
        """
        Start the logging.

        Args:
            logging_type (int): There are various types of logging implemented.
                - STATE_LOGGING_MINITAUR (=0): This will require to load the `quadruped/quadruped.urdf` and object
                    unique id from the quadruped. It logs the timestamp, IMU roll/pitch/yaw, 8 leg motor positions
                    (q0-q7), 8 leg motor torques (u0-u7), the forward speed of the torso and mode (unused in
                    simulation).
                - STATE_LOGGING_GENERIC_ROBOT (=1): This will log a log of the data of either all objects or selected
                    ones (if `object_unique_ids` is provided).
                - STATE_LOGGING_VIDEO_MP4 (=3): this will open an MP4 file and start streaming the OpenGL 3D
                    visualizer pixels to the file using an ffmpeg pipe. It will require ffmpeg installed. You can
                    also use avconv (default on Ubuntu), just create a symbolic link so that ffmpeg points to avconv.
                - STATE_LOGGING_CONTACT_POINTS (=5)
                - STATE_LOGGING_VR_CONTROLLERS (=2)
                - STATE_LOGGING_PROFILE_TIMINGS (=6): This will dump a timings file in JSON format that can be opened
                    using Google Chrome about://tracing LOAD.
            filename (str): file name (absolute or relative path) to store the log file data
            object_unique_ids (list of int): If left empty, the logger may log every object, otherwise the logger just
                logs the objects in the object_unique_ids list.
            max_log_dof (int): Maximum number of joint degrees of freedom to log (excluding the base dofs).
                This applies to STATE_LOGGING_GENERIC_ROBOT_DATA. Default value is 12. If a robot exceeds the number
                of dofs, it won't get logged at all.
            body_unique_id_A (int): Applies to STATE_LOGGING_CONTACT_POINTS (=5). If provided,only log contact points
                involving body_unique_id_A.
            body_unique_id_B (int): Applies to STATE_LOGGING_CONTACT_POINTS (=5). If provided,only log contact points
                involving body_unique_id_B.
            link_index_A (int): Applies to STATE_LOGGING_CONTACT_POINTS (=5). If provided, only log contact points
                involving link_index_A for body_unique_id_A.
            link_index_B (int): Applies to STATE_LOGGING_CONTACT_POINTS (=5). If provided, only log contact points
                involving link_index_B for body_unique_id_B.
            device_type_filter (int): deviceTypeFilter allows you to select what VR devices to log:
                VR_DEVICE_CONTROLLER (=1), VR_DEVICE_HMD (=2), VR_DEVICE_GENERIC_TRACKER (=4) or any combination of
                them. Applies to STATE_LOGGING_VR_CONTROLLERS (=2). Default values is VR_DEVICE_CONTROLLER (=1).
            log_flags (int): (upcoming PyBullet 1.3.1). STATE_LOG_JOINT_TORQUES (=3), to log joint torques due to
                joint motors.

        Returns:
            int: non-negative logging unique id.
        """
        kwargs = {}
        if object_unique_ids is not None:
            kwargs['objectUniqueIds'] = object_unique_ids
        if max_log_dof is not None:
            kwargs['maxLogDof'] = max_log_dof
        if body_unique_id_A is not None:
            kwargs['bodyUniqueIdA'] = body_unique_id_A
        if body_unique_id_B is not None:
            kwargs['bodyUniqueIdB'] = body_unique_id_B
        if link_index_A is not None:
            kwargs['linkIndexA'] = link_index_A
        if link_index_B is not None:
            kwargs['linkIndexB'] = link_index_B
        if device_type_filter is not None:
            kwargs['deviceTypeFilter'] = device_type_filter
        if log_flags is not None:
            kwargs['logFlags'] = log_flags

        self.sim.startStateLogging(logging_type, filename, **kwargs)

    def stop_logging(self, logger_id):
        """Stop the logging.

        Args:
            logger_id (int): unique logger id.
        """
        self.sim.stopStateLogging(logger_id)

    def set_gravity(self, gravity=(0, 0, -9.81)):
        """Set the gravity in the simulator with the given acceleration.

        By default, there is no gravitational force enabled in the simulator.

        Args:
            gravity (list, tuple of 3 floats): acceleration in the x, y, z directions.
        """
        self.sim.setGravity(gravity[0], gravity[1], gravity[2])

    def save(self, filename=None):
        """
        Save the state of the simulator.

        Args:
            filename (None, str): path to file to store the state of the simulator. If None, it will save it in
                memory instead of the disk.

        Returns:
            int: unique state id. This id can be used to load the state.
        """
        if filename is None:
            return self.sim.saveState()
        return self.sim.saveBullet(filename)

    def load(self, state):
        """
        Load/Restore the simulator to a previous state.

        Args:
            state (int, str): unique state id, or path to the file containing the state.
        """
        if isinstance(state, int):
            self.sim.restoreState(stateId=state)
        elif isinstance(state, str):
            self.sim.restoreState(fileName=state)

    def load_plugin(self, plugin_path, name):
        """Load a certain plugin in the simulator.

        Few examples can be found at: https://github.com/bulletphysics/bullet3/tree/master/examples/SharedMemory/plugins

        Args:
            plugin_path (str): path, location on disk where to find the plugin
            name (str): postfix name of the plugin that is appended to each API

        Returns:
             int: unique plugin id. If this id is negative, the plugin is not loaded. Once a plugin is loaded, you can
                send commands to the plugin using `execute_plugin_commands`
        """
        return self.sim.loadPlugin(plugin_path, name)

    def execute_plugin_command(self, plugin_id, *args):
        """Execute the commands on the specified plugin.

        Args:
            plugin_id (int): unique plugin id.
            args (list): list of argument values to be interpreted by the plugin. One can be a string, while the
                others must be integers or float.
        """
        kwargs = {}
        for arg in args:
            if isinstance(arg, str):
                kwargs['textArgument'] = arg
            elif isinstance(arg, int):
                kwargs.setdefault('intArgs', []).append(arg)
            elif isinstance(arg, float):
                kwargs.setdefault('floatArgs', []).append(arg)
        self.sim.executePluginCommand(plugin_id, **kwargs)

    def unload_plugin(self, plugin_id):
        """Unload the specified plugin from the simulator.

        Args:
            plugin_id (int): unique plugin id.
        """
        self.sim.unloadPlugin(plugin_id)

    ######################################
    # loading URDFs, SDFs, MJCFs, meshes #
    ######################################

    def load_urdf(self, filename, position=None, orientation=None, use_maximal_coordinates=0,
                  use_fixed_base=0, flags=0, scale=1.0):
        """Load the given URDF file.

        The loadURDF will send a command to the physics server to load a physics model from a Universal Robot
        Description File (URDF). The URDF file is used by the ROS project (Robot Operating System) to describe robots
        and other objects, it was created by the WillowGarage and the Open Source Robotics Foundation (OSRF).
        Many robots have public URDF files, you can find a description and tutorial here:
        http://wiki.ros.org/urdf/Tutorials

        Important note:
            most joints (slider, revolute, continuous) have motors enabled by default that prevent free
            motion. This is similar to a robot joint with a very high-friction harmonic drive. You should set the joint
            motor control mode and target settings using `pybullet.setJointMotorControl2`. See the
            `setJointMotorControl2` API for more information.

        Warning:
            by default, PyBullet will cache some files to speed up loading. You can disable file caching using
            `setPhysicsEngineParameter(enableFileCaching=0)`.

        Args:
            filename (str): a relative or absolute path to the URDF file on the file system of the physics server.
            position (vec3): create the base of the object at the specified position in world space coordinates [X,Y,Z]
            orientation (quat): create the base of the object at the specified orientation as world space quaternion
                [X,Y,Z,W]
            use_maximal_coordinates (int): Experimental. By default, the joints in the URDF file are created using the
                reduced coordinate method: the joints are simulated using the Featherstone Articulated Body algorithm
                (btMultiBody in Bullet 2.x). The useMaximalCoordinates option will create a 6 degree of freedom rigid
                body for each link, and constraints between those rigid bodies are used to model joints.
            use_fixed_base (bool): force the base of the loaded object to be static
            flags (int): URDF_USE_INERTIA_FROM_FILE (val=2): by default, Bullet recomputed the inertia tensor based on
                mass and volume of the collision shape. If you can provide more accurate inertia tensor, use this flag.
                URDF_USE_SELF_COLLISION (val=8): by default, Bullet disables self-collision. This flag let's you
                enable it.
                You can customize the self-collision behavior using the following flags:
                    * URDF_USE_SELF_COLLISION_EXCLUDE_PARENT (val=16) will discard self-collision between links that
                        are directly connected (parent and child).
                    * URDF_USE_SELF_COLLISION_EXCLUDE_ALL_PARENTS (val=32) will discard self-collisions between a
                        child link and any of its ancestors (parents, parents of parents, up to the base).
                    * URDF_USE_IMPLICIT_CYLINDER (val=128), will use a smooth implicit cylinder. By default, Bullet
                        will tessellate the cylinder into a convex hull.
            scale (float): scale factor to the URDF model.

        Returns:
            int (non-negative): unique id associated to the load model.
        """
        if position is not None:
            if isinstance(position, np.ndarray):
                position = position.ravel().tolist()
        if orientation is not None:
            if isinstance(orientation, np.ndarray):
                orientation = orientation.ravel().tolist()
            elif isinstance(orientation, quaternion.quaternion):
                orientation = self.quat_conv.convertFrom(orientation)

        return self.sim.loadURDF(filename, position, orientation, use_maximal_coordinates, int(use_fixed_base), flags,
                                 scale)

    def load_sdf(self, filename, scaling=1.):
        """Load the given SDF file.

        The loadSDF command only extracts some essential parts of the SDF related to the robot models and geometry,
        and ignores many elements related to cameras, lights and so on.

        Args:
            filename (str): a relative or absolute path to the SDF file on the file system of the physics server.
            scaling (float): scale factor for the object

        Returns:
            list(int): list of object unique id for each object loaded
        """
        return self.sim.loadSDF(filename, globalScaling=scaling)

    def load_mjcf(self, filename, scaling=1.):
        """Load the given MJCF file.

        "The loadMJCF command performs basic import of MuJoCo MJCF xml files, used in OpenAI Gym". [1]
        It will load all the object described in a MJCF file.

        Args:
            filename (str): a relative or absolute path to the MJCF file on the file system of the physics server.
            scaling (float): scale factor for the object

        Returns:
            list(int): list of object unique id for each object loaded
        """
        return self.sim.loadMJCF(filename, globalScaling=scaling)

    def load_mesh(self, filename, position, orientation=(0, 0, 0, 1), mass=1., scale=(1., 1., 1.),
                  color=None, flags=None):
        """
        Load a mesh in the world (only available in the simulator).

        Args:
            filename (str): path to file for the mesh. Currently, only Wavefront .obj. It will create convex hulls
                for each object (marked as 'o') in the .obj file.
            position (float[3]): position of the mesh in the Cartesian world space (in meters)
            orientation (float[4], np.quaternion): orientation of the mesh using quaternion.
                If np.quaternion then it uses the convention (w,x,y,z). If float[4], it uses the convention (x,y,z,w)
            mass (float): mass of the mesh (in kg). If mass = 0, it won't move even if there is a collision.
            scale (float[3]): scale the mesh in the (x,y,z) directions
            color (int[4]): color of the mesh (by default: white and opaque)
            flags (int, None): if flag = `sim.GEOM_FORCE_CONCAVE_TRIMESH` (=1), this will create a concave static
                triangle mesh. This should not be used with dynamic/moving objects, only for static (mass=0) terrain.

        Returns:
            int: unique id of the mesh in the world
        """
        kwargs = {}
        if flags is not None:
            kwargs['flags'] = flags

        # create collision shape
        collision_shape = self.sim.createCollisionShape(pybullet.GEOM_MESH, fileName=filename, meshScale=scale,
                                                        **kwargs)

        if color is not None:
            kwargs['rgbaColor'] = color

        # create visual shape
        visual_shape = self.sim.createVisualShape(pybullet.GEOM_MESH, fileName=filename, meshScale=scale, **kwargs)

        # create body
        mesh = self.sim.createMultiBody(baseMass=mass,
                                        baseCollisionShapeIndex=collision_shape,
                                        baseVisualShapeIndex=visual_shape,
                                        basePosition=position,
                                        baseOrientation=orientation)

        return mesh

    ##########
    # Bodies #
    ##########

    # TODO: add the other arguments
    def create_body(self, visual_shape_id=-1, collision_shape_id=-1, mass=0, position=(0., 0., 0.),
                    orientation=(0., 0., 0., 1.)):
        """Create a body in the simulator.

        Args:
            visual_shape_id (int): unique id from createVisualShape or -1. You can reuse the visual shape (instancing)
            collision_shape_id (int): unique id from createCollisionShape or -1. You can re-use the collision shape
                for multiple multibodies (instancing)
            mass (int): mass of the base, in kg (if using SI units)
            position (np.float[3]): Cartesian world position of the base
            orientation (np.float[4]): Orientation of base as quaternion [x,y,z,w]

        Returns:
            int: non-negative unique id or -1 for failure.
        """
        if isinstance(position, np.ndarray):
            position = position.ravel().tolist()
        if isinstance(orientation, np.ndarray):
            orientation = orientation.ravel().tolist()
        elif isinstance(orientation, quaternion.quaternion):
            orientation = self.quat_conv.convertFrom(orientation)
        return self.sim.createMultiBody(baseMass=mass, baseCollisionShapeIndex=collision_shape_id,
                                        baseVisualShapeIndex=visual_shape_id, basePosition=position,
                                        baseOrientation=orientation)

    def remove_body(self, body_id):
        """Remove a particular body in the simulator.

        Args:
            body_id (int): unique body id.
        """
        self.sim.removeBody(body_id)

    def num_bodies(self):
        """Return the number of bodies present in the simulator.

        Returns:
            int: number of bodies
        """
        return self.sim.getNumBodies()

    def get_body_info(self, body_id):
        """Get the specified body information.

        Specifically, it returns the base name extracted from the URDF, SDF, MJCF, or other file.

        Args:
            body_id (int): unique body id.

        Returns:
            str: base name
        """
        return self.sim.getBodyInfo(body_id)

    def get_body_id(self, index):
        """
        Get the body id associated to the index which is between 0 and `num_bodies()`.

        Args:
            index (int): index between [0, `num_bodies()`]

        Returns:
            int: unique body id.
        """
        return self.sim.getBodyUniqueId(index)

    ###############
    # constraints #
    ###############

    def create_constraint(self, parent_body_id, parent_link_id, child_body_id, child_link_id, joint_type,
                          joint_axis, parent_frame_position, child_frame_position,
                          parent_frame_orientation=(0., 0., 0., 1.), child_frame_orientation=(0., 0., 0., 1.)):
        """
        Create a constaint.

        "URDF, SDF and MJCF specify articulated bodies as a tree-structures without loops. The 'createConstraint'
        allows you to connect specific links of bodies to close those loops. In addition, you can create arbitrary
        constraints between objects, and between an object and a specific world frame.
        It can also be used to control the motion of physics objects, driven by animated frames, such as a VR
        controller. It is better to use constraints, instead of setting the position or velocity directly for
        such purpose, since those constraints are solved together with other dynamics constraints." [1]

        Args:
            parent_body_id (int): parent body unique id
            parent_link_id (int): parent link index (or -1 for the base)
            child_body_id (int): child body unique id, or -1 for no body (specify a non-dynamic child frame in world
                coordinates)
            child_link_id (int): child link index, or -1 for the base
            joint_type (int): joint type: JOINT_PRISMATIC (=1), JOINT_FIXED (=4), JOINT_POINT2POINT (=5),
                JOINT_GEAR (=6)
            joint_axis (np.float[3]): joint axis, in child link frame
            parent_frame_position (np.float[3]): position of the joint frame relative to parent CoM frame.
            child_frame_position (np.float[3]): position of the joint frame relative to a given child CoM frame (or
                world origin if no child specified)
            parent_frame_orientation (np.float[4]): the orientation of the joint frame relative to parent CoM
                coordinate frame
            child_frame_orientation (np.float[4]): the orientation of the joint frame relative to the child CoM
                coordinate frame (or world origin frame if no child specified)

        Examples:
            - `pybullet/examples/quadruped.py`
            - `pybullet/examples/constraint.py`

        Returns:
            int: constraint unique id.
        """
        return self.sim.createConstraint(parent_body_id, parent_link_id, child_body_id, child_link_id, joint_type,
                                         joint_axis, parent_frame_position, child_frame_position,
                                         parent_frame_orientation, child_frame_orientation)

    def remove_constraint(self, constraint_id):
        """
        Remove the specified constraint.

        Args:
            constraint_id (int): constraint unique id.
        """
        self.sim.removeConstraint(constraint_id)

    def change_constraint(self, constraint_id, child_joint_pivot=None, child_frame_orientation=None, max_force=None,
                          gear_ratio=None, gear_auxiliary_link=None, relative_position_target=None, erp=None):
        """
        Change the parameters of an existing constraint.

        Args:
            constraint_id (int): constraint unique id.
            child_joint_pivot (np.float[3]): updated position of the joint frame relative to a given child CoM frame
                (or world origin if no child specified)
            child_frame_orientation (np.float[4]): updated child frame orientation as quaternion [x,y,z,w]
            max_force (float): maximum force that constraint can apply
            gear_ratio (float): the ratio between the rates at which the two gears rotate
            gear_auxiliary_link (int): In some cases, such as a differential drive, a third (auxilary) link is used as
                reference pose. See `racecar_differential.py`
            relative_position_target (float): the relative position target offset between two gears
            erp (float): constraint error reduction parameter
        """
        kwargs = {}
        if child_joint_pivot is not None:
            kwargs['jointChildPivot'] = child_joint_pivot
        if child_frame_orientation is not None:
            kwargs['jointChildFrameOrientation'] = child_frame_orientation
        if max_force is not None:
            kwargs['maxForce'] = max_force
        if gear_ratio is not None:
            kwargs['gearRatio'] = gear_ratio
        if gear_auxiliary_link is not None:
            kwargs['gearAuxLink'] = gear_auxiliary_link
        if relative_position_target is not None:
            kwargs['relativePositionTarget'] = relative_position_target
        if erp is not None:
            kwargs['erp'] = erp

        self.sim.changeConstraint(constraint_id, **kwargs)

    def num_constraints(self):
        """
        Get the number of constraints created.

        Returns:
            int: number of constraints created.
        """
        return self.sim.getNumConstraints()

    def get_constraint_id(self, index):
        """
        Get the constraint unique id associated with the index which is between 0 and `num_constraints()`.

        Args:
            index (int): index between [0, `num_constraints()`]

        Returns:
            int: constraint unique id.
        """
        return self.sim.getConstraintUniqueId(index)

    def get_constraint_info(self, constraint_id):
        """
        Get information about the given constaint id.

        Args:
            constraint_id (int): constraint unique id.

        Returns:
            int: parent_body_id
            int: parent_joint_id  (if -1, it is the base)
            int: child_body_id    (if -1, no body; specify a non-dynamic child frame in world coordinates)
            int: child_link_id    (if -1, it is the base)
            int: constraint/joint type
            np.float[3]: joint axis
            np.float[3]: joint pivot (position) in parent CoM frame
            np.float[3]: joint pivot (position) in specified child CoM frame (or world frame if no specified child)
            np.float[4]: joint frame orientation relative to parent CoM coordinate frame
            np.float[4]: joint frame orientation relative to child CoM frame (or world frame if no specified child)
            float: maximum force that constraint can apply
        """
        return self.sim.getConstraintInfo(constraint_id)

    def get_constraint_state(self, constraint_id):
        """
        Get the state of the given constraint.

        Args:
            constraint_id (int): constraint unique id.

        Returns:
            np.float[D]: applied constraint forces. Its dimension is the degrees of freedom that are affected by
                the constraint (a fixed constraint affects 6 DoF for example)
        """
        return self.sim.getConstraintState(constraint_id)

    ###########
    # objects #
    ###########

    def get_mass(self, body_id):
        """
        Return the total mass of the robot (=sum of all mass links).

        Args:
            body_id (int): unique object id, as returned from `load_urdf`.

        Returns:
            float: total mass of the robot [kg]
        """
        return np.sum(self.get_link_masses(body_id, [-1] + list(range(self.num_links(body_id)))))

    def get_base_mass(self, body_id):
        """Return the base mass of the robot."""
        return self.get_link_masses(body_id, -1)

    def get_base_name(self, body_id):
        """
        Return the base name.

        Args:
            body_id (int): unique object id.

        Returns:
            str: base name
        """
        return self.sim.getBodyInfo(body_id)[0]

    def get_center_of_mass(self, body_id, link_ids=None):
        """
        Return the center of mass position.

        Args:
            body_id (int): unique body id.
            link_ids (list of int): link ids associated with the given body id. If None, it will take all the links
                of the specified body.

        Returns:
            np.float[3]: center of mass position in the Cartesian world coordinates
        """
        if link_ids is None:
            link_ids = list(range(self.num_links(body_id)))

        pos = self.get_link_world_positions(body_id, link_ids)
        mass = self.get_link_masses(body_id, link_ids)

        com = np.sum(pos.T * mass, axis=1) / np.sum(mass)

        return com

    def get_base_pose(self, body_id):
        """
        Get the current position and orientation of the base (or root link) of the body in Cartesian world coordinates.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[3]: base position
            np.float[4]: base orientation (quaternion [x,y,z,w])
        """
        pos, orientation = self.sim.getBasePositionAndOrientation(body_id)
        return np.array(pos), np.array(orientation)

    def get_base_position(self, body_id):
        """
        Return the base position of the specified body.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[3]: base position.
        """
        return self.get_base_pose(body_id)[0]

    def get_base_orientation(self, body_id):
        """
        Get the base orientation of the specified body.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[4]: base orientation in the form of a quaternion (x,y,z,w)
        """
        return self.get_base_pose(body_id)[1]

    def reset_base_pose(self, body_id, position, orientation):
        """
        Reset the base position and orientation of the specified object id.

        "It is best only to do this at the start, and not during a running simulation, since the command will override
        the effect of all physics simulation. The linear and angular velocity is set to zero. You can use
        `reset_base_velocity` to reset to a non-zero linear and/or angular velocity." [1]

        Args:
            body_id (int): unique object id.
            position (np.float[3]): new base position.
            orientation (np.float[4]): new base orientation (expressed as a quaternion [x,y,z,w])
        """
        self.sim.resetBasePositionAndOrientation(body_id, position, orientation)

    def reset_base_position(self, body_id, position):
        """
        Reset the base position of the specified body/object id while preserving its orientation.

        Args:
            body_id (int): unique object id.
            position (np.float[3]): new base position.
        """
        orientation = self.get_base_orientation(body_id)
        self.reset_base_pose(body_id, position, orientation)

    def reset_base_orientation(self, body_id, orientation):
        """
        Reset the base orientation of the specified body/object id while preserving its position.

        Args:
            body_id (int): unique object id.
            orientation (np.float[4]): new base orientation (expressed as a quaternion [x,y,z,w])
        """
        position = self.get_base_position(body_id)
        self.reset_base_pose(body_id, position, orientation)

    def get_base_velocity(self, body_id):
        """
        Return the base linear and angular velocities.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[3]: linear velocity of the base in Cartesian world space coordinates
            np.float[3]: angular velocity of the base in Cartesian world space coordinates
        """
        lin_vel, ang_vel = self.sim.getBaseVelocity(body_id)
        return np.array(lin_vel), np.array(ang_vel)

    def get_base_linear_velocity(self, body_id):
        """
        Return the linear velocity of the base.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[3]: linear velocity of the base in Cartesian world space coordinates
        """
        return self.get_base_velocity(body_id)[0]

    def get_base_angular_velocity(self, body_id):
        """
        Return the angular velocity of the base.

        Args:
            body_id (int): object unique id, as returned from `load_urdf`.

        Returns:
            np.float[3]: angular velocity of the base in Cartesian world space coordinates
        """
        return self.get_base_velocity(body_id)[1]

    def reset_base_velocity(self, body_id, linear_velocity=None, angular_velocity=None):
        """
        Reset the base velocity.

        Args:
            body_id (int): unique object id.
            linear_velocity (np.float[3]): new linear velocity of the base.
            angular_velocity (np.float[3]): new angular velocity of the base.
        """
        if linear_velocity is not None and angular_velocity is not None:
            self.sim.resetBaseVelocity(body_id, linearVelocity=linear_velocity, angularVelocity=angular_velocity)
        elif linear_velocity is not None:
            self.sim.resetBaseVelocity(body_id, linearVelocity=linear_velocity)
        elif angular_velocity is not None:
            self.sim.resetBaseVelocity(body_id, angularVelocity=angular_velocity)

    def reset_base_linear_velocity(self, body_id, linear_velocity):
        """
        Reset the base linear velocity.

        Args:
            body_id (int): unique object id.
            linear_velocity (np.float[3]): new linear velocity of the base
        """
        self.sim.resetBaseVelocity(body_id, linearVelocity=linear_velocity)

    def reset_base_angular_velocity(self, body_id, angular_velocity):
        """
        Reset the base angular velocity.

        Args:
            body_id (int): unique object id.
            angular_velocity (np.float[3]): new angular velocity of the base
        """
        self.sim.resetBaseVelocity(body_id, angularVelocity=angular_velocity)

    def apply_external_force(self, body_id, link_id=-1, force=(0., 0., 0.), position=(0., 0., 0.),
                             flags=pybullet.LINK_FRAME):
        """
        Apply the specified external force on the specified position on the body / link.

        "This method will only work when explicitly stepping the simulation using stepSimulation, in other words:
        setRealTimeSimulation(0). After each simulation step, the external forces are cleared to zero. If you are
        using 'setRealTimeSimulation(1), applyExternalForce/Torque will have undefined behavior (either 0, 1 or
        multiple force/torque applications)" [1]

        Args:
            body_id (int): unique body id.
            link_id (int): unique link id. If -1, it will be the base.
            force (np.float[3]): external force to be applied.
            position (np.float[3]): position on the link where the force is applied. See `flags` for coordinate
                systems.
            flags (int): Specify the coordinate system of force/position: either `pybullet.WORLD_FRAME` (=2) for
                Cartesian world coordinates or `pybullet.LINK_FRAME` (=1) for local link coordinates.
        """
        self.sim.applyExternalForce(body_id, link_id, force, position, flags)

    def apply_external_torque(self, body_id, link_id=-1, torque=(0., 0., 0.)):
        """
        Apply an external torque on a body, or a link of the body. Note that after each simulation step, the external
        torques are cleared to 0.

        Warnings: This does not work when using `sim.setRealTimeSimulation(1)`.

        Args:
            body_id (int): unique body id.
            link_id (int): link id to apply the torque, if -1 it will apply the torque on the base
            torque (float[3]): Cartesian torques to be applied on the body
        """
        self.sim.applyExternalTorque(body_id, link_id, torque)

    ###################
    # transformations #
    ###################

    #############################
    # robots (joints and links) #
    #############################

    def num_joints(self, body_id):
        """
        Return the total number of joints of the specified body. This is the same as calling `num_links`.

        Args:
            body_id (int): unique body id.

        Returns:
            int: number of joints with the associated body id.
        """
        return self.sim.getNumJoints(body_id)

    def num_links(self, body_id):
        """
        Return the total number of links of the specified body. This is the same as calling `num_joints`.

        Args:
            body_id (int): unique body id.

        Returns:
            int: number of links with the associated body id.
        """
        return self.num_joints(body_id)

    def get_joint_info(self, body_id, joint_id):
        """
        Return information about the given joint about the specified body.

        Note that this method returns a lot of information, so specific methods have been implemented that return
        only the desired information. Also, note that we do not convert the data here.

        Args:
            body_id (int): unique body id.
            joint_id (int): joint id is included in [0..`num_joints(body_id)`].

        Returns:
            [0] int:        the same joint id as the input parameter
            [1] str:        name of the joint (as specified in the URDF/SDF/etc file)
            [2] int:        type of the joint which implie the number of position and velocity variables.
                            The types include JOINT_REVOLUTE (=0), JOINT_PRISMATIC (=1), JOINT_SPHERICAL (=2),
                            JOINT_PLANAR (=3), and JOINT_FIXED (=4).
            [3] int:        q index - the first position index in the positional state variables for this body
            [4] int:        dq index - the first velocity index in the velocity state variables for this body
            [5] int:        flags (reserved)
            [6] float:      the joint damping value (as specified in the URDF file)
            [7] float:      the joint friction value (as specified in the URDF file)
            [8] float:      the positional lower limit for slider and revolute joints
            [9] float:      the positional upper limit for slider and revolute joints
            [10] float:     maximum force specified in URDF. Note that this value is not automatically used.
                            You can use maxForce in 'setJointMotorControl2'.
            [11] float:     maximum velocity specified in URDF. Note that this value is not used in actual
                            motor control commands at the moment.
            [12] str:       name of the link (as specified in the URDF/SDF/etc file)
            [13] np.float[3]:  joint axis in local frame (ignored for JOINT_FIXED)
            [14] np.float[3]:  joint position in parent frame
            [15] np.float[4]:  joint orientation in parent frame
            [16] int:       parent link index, -1 for base
        """
        return self.sim.getJointInfo(body_id, joint_id)

    def get_joint_state(self, body_id, joint_id):
        """
        Get the joint state.

        Args:
            body_id (int): body unique id as returned by `load_urdf`, etc.
            joint_id (int): joint index in range [0..num_joints(body_id)]

        Returns:
            float: The position value of this joint.
            float: The velocity value of this joint.
            np.float[6]: These are the joint reaction forces, if a torque sensor is enabled for this joint it is
                [Fx, Fy, Fz, Mx, My, Mz]. Without torque sensor, it is [0, 0, 0, 0, 0, 0].
            float: This is the motor torque applied during the last stepSimulation. Note that this only applies in
                VELOCITY_CONTROL and POSITION_CONTROL. If you use TORQUE_CONTROL then the applied joint motor torque
                is exactly what you provide, so there is no need to report it separately.
        """
        pos, vel, forces, torque = self.sim.getJointState(body_id, joint_id)
        return pos, vel, np.array(forces), torque

    def get_joint_states(self, body_id, joint_ids):
        """
        Get the joint state of the specified joints.

        Args:
            body_id (int): body unique id.
            joint_ids (list of int): list of joint ids.

        Returns:
            list:
                float: The position value of this joint.
                float: The velocity value of this joint.
                np.float[6]: These are the joint reaction forces, if a torque sensor is enabled for this joint it is
                    [Fx, Fy, Fz, Mx, My, Mz]. Without torque sensor, it is [0, 0, 0, 0, 0, 0].
                float: This is the motor torque applied during the last `step`. Note that this only applies in
                    VELOCITY_CONTROL and POSITION_CONTROL. If you use TORQUE_CONTROL then the applied joint motor
                    torque is exactly what you provide, so there is no need to report it separately.
        """
        return self.sim.getJointStates(body_id, joint_ids)

    def reset_joint_state(self, body_id, joint_id, target_position, target_velocity=0.):
        """
        Reset the state of the joint. It is best only to do this at the start, while not running the simulation:
        `reset_joint_state` overrides all physics simulation. Note that we only support 1-DOF motorized joints at
        the moment, sliding joint or revolute joints.

        Args:
            body_id (int): body unique id as returned by `load_urdf`, etc.
            joint_id (int): joint index in range [0..num_joints(body_id)]
            target_position (float): the joint position (angle in radians [rad] or position [m])
            target_velocity (float): the joint velocity (angular [rad/s] or linear velocity [m/s])
        """
        self.sim.resetJointState(body_id, joint_id, target_position, target_velocity)

    def enable_joint_force_torque_sensor(self, body_id, joint_id, enable=True):
        """
        You can enable or disable a joint force/torque sensor in each joint. Once enabled, if you perform a
        `step`, the 'get_joint_state' will report the joint reaction forces in the fixed degrees of freedom: a fixed
        joint will measure all 6DOF joint forces/torques. A revolute/hinge joint force/torque sensor will measure
        5DOF reaction forces along all axis except the hinge axis. The applied force by a joint motor is available
        in the `applied_joint_motor_torque` of `get_joint_state`.

        Args:
            body_id (int): body unique id as returned by `load_urdf`, etc.
            joint_id (int): joint index in range [0..num_joints(body_id)]
            enable (bool): True to enable, False to disable the force/torque sensor
        """
        self.sim.enableJointForceTorqueSensor(body_id, joint_id, enable)

    def set_joint_motor_control(self, body_id, joint_id, control_mode=pybullet.POSITION_CONTROL, position=None,
                                velocity=None, force=None, kp=None, kd=None, max_velocity=None):
        """
        Set the joint motor control.

        In position control:
        .. math:: error = Kp (x_{des} - x) + Kd (\dot{x}_{des} - \dot{x})

        In velocity control:
        .. math:: error = \dot{x}_{des} - \dot{x}

        Note that the maximum forces and velocities are not automatically used for the different control schemes.

        "We can control a robot by setting a desired control mode for one or more joint motors. During the `step`,
        the physics engine will simulate the motors to reach the given target value that can be reached within
        the maximum motor forces and other constraints. Each revolute joint and prismatic joint is motorized
        by default. There are 3 different motor control modes: position control, velocity control and torque control.

        You can effectively disable the motor by using a force of 0. You need to disable motor in order to use direct
        torque control: `set_joint_motor_control(body_id, joint_id, control_mode=pybullet.VELOCITY_CONTROL,
        force=force)`"

        Args:
            body_id (int): body unique id.
            joint_id (int): joint/link id.
            control_mode (int): POSITION_CONTROL (=2) (which is in fact CONTROL_MODE_POSITION_VELOCITY_PD),
                VELOCITY_CONTROL (=0), TORQUE_CONTROL (=1) and PD_CONTROL (=3).
            position (float): target joint position (used in POSITION_CONTROL).
            velocity (float): target joint velocity. In VELOCITY_CONTROL and POSITION_CONTROL, the target velocity is
                the desired velocity of the joint. Note that the target velocity is not the maximum joint velocity.
                In PD_CONTROL and POSITION_CONTROL/CONTROL_MODE_POSITION_VELOCITY_PD, the final target velocity is
                computed using:
                `kp*(erp*(desiredPosition-currentPosition)/dt)+currentVelocity+kd*(m_desiredVelocity - currentVelocity)`
            force (float): in POSITION_CONTROL and VELOCITY_CONTROL, this is the maximum motor force used to reach the
                target value. In TORQUE_CONTROL this is the force/torque to be applied each simulation step.
            kp (float): position (stiffness) gain (used in POSITION_CONTROL).
            kd (float): velocity (damping) gain (used in POSITION_CONTROL).
            max_velocity (float): in POSITION_CONTROL this limits the velocity to a maximum.
        """
        kwargs = {}
        if position is not None:
            kwargs['targetPosition'] = position
        if velocity is not None:
            kwargs['targetVelocity'] = velocity
        if force is not None:
            kwargs['force'] = force
        if kp is not None:
            kwargs['positionGain'] = kp
        if kd is not None:
            kwargs['velocityGain'] = kd
        if max_velocity is not None:
            kwargs['maxVelocity'] = max_velocity
        self.sim.setJointMotorControl2(body_id, joint_id, controlMode=control_mode, **kwargs)

    def set_joint_motor_control_array(self, body_id, joint_ids, control_mode=pybullet.POSITION_CONTROL, positions=None,
                                      velocities=None, forces=None, kps=None, kds=None):
        """
        Instead of making individual calls for each joint, you can pass arrays for all inputs to reduce calling
        overhead dramatically.

        Args:
            body_id (int): body unique id.
            joint_ids (list of int): list of joint id.
            control_mode (int): POSITION_CONTROL (=2) (which is in fact CONTROL_MODE_POSITION_VELOCITY_PD),
                VELOCITY_CONTROL (=0), TORQUE_CONTROL (=1) and PD_CONTROL (=3).
            positions (list of float): list of target joint positions (used in POSITION_CONTROL) the target value is target position of the joint.
            velocities (list of float): list of target joint velocities (used in PD_CONTROL, VELOCITY_CONTROL and
                POSITION_CONTROL).
            forces (list of float): list of forces. In POSITION_CONTROL and VELOCITY_CONTROL, these are the maximum
                motor forces used to reach the target values. In TORQUE_CONTROL these are the forces/torques to be
                applied each simulation step.
            kps (list of float): list of position (stiffness) gains (used in POSITION_CONTROL).
            kds (list of float): list of velocity (damping) gains (used in POSITION_CONTROL).
        """
        kwargs = {}
        if positions is not None:
            kwargs['targetPositions'] = positions
        if velocities is not None:
            kwargs['targetVelocities'] = velocities
        if forces is not None:
            kwargs['forces'] = forces
        if kps is not None:
            kwargs['positionGains'] = kps
        if kds is not None:
            kwargs['velocityGains'] = kds
        self.sim.setJointMotorControlArray(body_id, joint_ids, controlMode=control_mode, **kwargs)

    def get_link_state(self, body_id, link_id, compute_velocity=False, compute_forward_kinematics=False):
        """
        Get the state of the associated link.

        Args:
            body_id (int): body unique id.
            link_id (int): link index.
            compute_velocity (bool): If True, the Cartesian world velocity will be computed and returned.
            compute_forward_kinematics (bool): if True, the Cartesian world position/orientation will be recomputed
                using forward kinematics.

        Returns:
            np.float[3]: Cartesian position of CoM
            np.float[4]: Cartesian orientation of CoM, in quaternion [x,y,z,w]
            np.float[3]: local position offset of inertial frame (center of mass) expressed in the URDF link frame
            np.float[4]: local orientation (quaternion [x,y,z,w]) offset of the inertial frame expressed in URDF link
                frame
            np.float[3]: world position of the URDF link frame
            np.float[4]: world orientation of the URDF link frame
            np.float[3]: Cartesian world linear velocity. Only returned if `compute_velocity` is True.
            np.float[3]: Cartesian world angular velocity. Only returned if `compute_velocity` is True.
        """
        results = self.sim.getLinkState(body_id, link_id, computeLinkVelocity=compute_velocity,
                                        computeForwardKinematics=compute_forward_kinematics)
        return [np.array(result) for result in results]

    def get_link_states(self, body_id, link_ids, compute_velocity=False, compute_forward_kinematics=False):
        """
        Get the state of the associated links.

        Args:
            body_id (int): body unique id.
            link_ids (list of int): list of link index.
            compute_velocity (bool): If True, the Cartesian world velocity will be computed and returned.
            compute_forward_kinematics (bool): if True, the Cartesian world position/orientation will be recomputed
                using forward kinematics.

        Returns:
            list:
                np.float[3]: Cartesian position of CoM
                np.float[4]: Cartesian orientation of CoM, in quaternion [x,y,z,w]
                np.float[3]: local position offset of inertial frame (center of mass) expressed in the URDF link frame
                np.float[4]: local orientation (quaternion [x,y,z,w]) offset of the inertial frame expressed in URDF
                    link frame
                np.float[3]: world position of the URDF link frame
                np.float[4]: world orientation of the URDF link frame
                np.float[3]: Cartesian world linear velocity. Only returned if `compute_velocity` is True.
                np.float[3]: Cartesian world angular velocity. Only returned if `compute_velocity` is True.
        """
        return [self.get_link_state(body_id, link_id, compute_velocity, compute_forward_kinematics)
                for link_id in link_ids]

    def get_link_names(self, body_id, link_ids):
        """
        Return the name of the given link(s).

        Args:
            body_id (int): unique body id.
            link_ids (int, list of int): link id, or list of link ids.

        Returns:
            if 1 link:
                str: link name
            if multiple links:
                str[N]: link names
        """
        if isinstance(link_ids, int):
            return self.sim.getJointInfo(body_id, link_ids)[12]
        return [self.sim.getJointInfo(body_id, link_id)[12] for link_id in link_ids]

    def get_link_masses(self, body_id, link_ids):
        """
        Return the mass of the given link(s).

        Args:
            body_id (int): unique body id.
            link_ids (int, list of int): link id, or list of link ids.

        Returns:
            if 1 link:
                float: mass of the given link
            else:
                float[N]: mass of each link
        """
        if isinstance(link_ids, int):
            return self.sim.getDynamicsInfo(body_id, link_ids)[0]
        return np.array([self.sim.getDynamicsInfo(body_id, link_id)[0] for link_id in link_ids])

    def get_link_frames(self, body_id, link_ids):
        pass

    def get_link_world_positions(self, body_id, link_ids):
        """
        Return the CoM position (in the Cartesian world space coordinates) of the given link(s).

        Args:
            body_id (int): unique body id.
            link_ids (list of int): list of link indices.

        Returns:
            if 1 link:
                np.float[3]: the link CoM position in the world space
            if multiple links:
                np.float[N,3]: CoM position of each link in world space
        """
        if isinstance(link_ids, int):
            if link_ids == -1:
                return self.get_base_position(body_id)
            return np.array(self.sim.getLinkState(body_id, link_ids)[0])
        positions = []
        for link_id in link_ids:
            if link_id == -1:
                positions.append(self.get_base_position(body_id))
            else:
                positions.append(np.array(self.sim.getLinkState(body_id, link_id)[0]))
        return np.array(positions)

    def get_link_positions(self, body_id, link_ids):
        pass

    def get_link_world_orientations(self, body_id, link_ids):
        """
        Return the CoM orientation (in the Cartesian world space) of the given link(s).

        Args:
            body_id (int): unique body id.
            link_ids (list of int): list of link indices.

        Returns:
            if 1 link:
                np.float[4]: Cartesian orientation of the link CoM (x,y,z,w)
            if multiple links:
                np.float[N,4]: CoM orientation of each link (x,y,z,w)
        """
        if isinstance(link_ids, int):
            if link_ids == -1:
                return self.get_base_orientation(body_id)
            return np.array(self.sim.getLinkState(body_id, link_ids)[1])
        orientations = []
        for link_id in link_ids:
            if link_id == -1:
                orientations.append(self.get_base_orientation(body_id))
            else:
                orientations.append(np.array(self.sim.getLinkState(body_id, link_id)[1]))
        return np.array(orientations)

    def get_link_orientations(self, body_id, link_ids):
        pass

    def get_link_world_linear_velocities(self, body_id, link_ids):
        """
        Return the linear velocity of the link(s) expressed in the Cartesian world space coordinates.

        Args:
            body_id (int): unique body id.
            link_ids (list of int): list of link indices.

        Returns:
            if 1 link:
                np.float[3]: linear velocity of the link in the Cartesian world space
            if multiple links:
                np.float[N,3]: linear velocity of each link
        """
        if isinstance(link_ids, int):
            if link_ids == -1:
                return self.get_base_linear_velocity(body_id)
            return np.array(self.sim.getLinkState(body_id, link_ids, computeLinkVelocity=1)[6])
        velocities = []
        for link_id in link_ids:
            if link_id == -1:
                velocities.append(self.get_base_linear_velocity(body_id))
            else:
                velocities.append(np.array(self.sim.getLinkState(body_id, link_id, computeLinkVelocity=1)[6]))
        return np.array(velocities)

    def get_link_world_angular_velocities(self, body_id, link_ids):
        """
        Return the angular velocity of the link(s) in the Cartesian world space coordinates.

        Args:
            body_id (int): unique body id.
            link_ids (list of int): list of link indices.

        Returns:
            if 1 link:
                np.float[3]: angular velocity of the link in the Cartesian world space
            if multiple links:
                np.float[N,3]: angular velocity of each link
        """
        if isinstance(link_ids, int):
            if link_ids == -1:
                return self.get_base_linear_velocity(body_id)
            return np.array(self.sim.getLinkState(body_id, link_ids, computeLinkVelocity=1)[7])
        velocities = []
        for link_id in link_ids:
            if link_id == -1:
                velocities.append(self.get_base_linear_velocity(body_id))
            else:
                velocities.append(np.array(self.sim.getLinkState(body_id, link_id, computeLinkVelocity=1)[7]))
        return np.array(velocities)

    def get_link_world_velocities(self, body_id, link_ids):
        """
        Return the linear and angular velocities (expressed in the Cartesian world space coordinates) for the given
        link(s).

        Args:
            body_id (int): unique body id.
            link_ids (list of int): list of link indices.

        Returns:
            if 1 link:
                np.float[6]: linear and angular velocity of the link in the Cartesian world space
            if multiple links:
                np.float[N,6]: linear and angular velocity of each link
        """
        if isinstance(link_ids, int):
            if link_ids == -1:
                lin_vel, ang_vel = self.get_base_velocity(body_id)
                return np.concatenate((lin_vel, ang_vel))
            lin_vel, ang_vel = self.sim.getLinkState(body_id, link_ids, computeLinkVelocity=1)[6:8]
            return np.array(lin_vel + ang_vel)
        velocities = []
        for link_id in link_ids:
            if link_id == -1:  # base link
                lin_vel, ang_vel = self.get_base_velocity(body_id)
            else:
                lin_vel, ang_vel = self.sim.getLinkState(body_id, link_id, computeLinkVelocity=1)[6:8]
            velocities.append(np.concatenate((lin_vel, ang_vel)))
        return np.array(velocities)

    def get_link_velocities(self, body_id, link_ids):
        pass

    def get_qindex(self, body_id, joint_ids):
        """
        Get the corresponding q index of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                int: q index
            if multiple joints:
                np.int[N]: q indices
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[3] - 7
        return np.array([self.sim.getJointInfo(body_id, joint_id)[3] for joint_id in joint_ids]) - 7

    def get_actuated_joint_ids(self, body_id):
        """
        Get the actuated joint ids associated with the given body id.

        Warnings: this checks through the list of all joints each time it is called. It might be a good idea to call
        this method one time and cache the actuated joint ids.

        Args:
            body_id (int): unique body id.

        Returns:
            list of int: actuated joint ids.
        """
        joint_ids = []
        for joint_id in range(self.num_joints(body_id)):
            # Get joint info
            jnt = self.get_joint_info(body_id, joint_id)
            if jnt[2] != self.sim.JOINT_FIXED:  # if not a fixed joint
                joint_ids.append(jnt[0])
        return joint_ids

    def get_joint_names(self, body_id, joint_ids):
        """
        Return the name of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                str: name of the joint
            if multiple joints:
                str[N]: name of each joint
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[1]
        return [self.sim.getJointInfo(body_id, joint_id)[1] for joint_id in joint_ids]

    def get_joint_dampings(self, body_id, joint_ids):
        """
        Get the damping coefficient of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: damping coefficient of the given joint
            if multiple joints:
                np.float[N]: damping coefficient for each specified joint
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[6]
        return np.array([self.sim.getJointInfo(body_id, joint_id)[6] for joint_id in joint_ids])

    def get_joint_frictions(self, body_id, joint_ids):
        """
        Get the friction coefficient of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: friction coefficient of the given joint
            if multiple joints:
                float[N]: friction coefficient for each specified joint
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[7]
        return np.array([self.sim.getJointInfo(body_id, joint_id)[7] for joint_id in joint_ids])

    def get_joint_limits(self, body_id, joint_ids):
        """
        Get the joint limits of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                np.float[2]: lower and upper limit
            if multiple joints:
                np.float[N,2]: lower and upper limit for each specified joint
        """
        if isinstance(joint_ids, int):
            return np.array(self.sim.getJointInfo(body_id, joint_ids)[8:10])
        return np.array([self.sim.getJointInfo(body_id, joint_id)[8:10] for joint_id in joint_ids])

    def get_joint_max_forces(self, body_id, joint_ids):
        """
        Get the maximum force that can be applied on the given joint(s).

        Warning: Note that this is not automatically used in position, velocity, or torque control.

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: maximum force [N]
            if multiple joints:
                float[N]: maximum force for each specified joint [N]
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[10]
        return np.array([self.sim.getJointInfo(body_id, joint_id)[10] for joint_id in joint_ids])

    def get_joint_max_velocities(self, body_id, joint_ids):
        """
        Get the maximum velocity that can be applied on the given joint(s).

        Warning: Note that this is not automatically used in position, velocity, or torque control.

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: maximum velocity [rad/s]
            if multiple joints:
                np.float[N]: maximum velocities for each specified joint [rad/s]
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointInfo(body_id, joint_ids)[11]
        return np.array([self.sim.getJointInfo(body_id, joint_id)[11] for joint_id in joint_ids])

    def get_joint_axes(self, body_id, joint_ids):
        """
        Get the joint axis about the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                np.float[3]: joint axis
            if multiple joint:
                np.float[N,3]: list of joint axis
        """
        if isinstance(joint_ids, int):
            return np.array(self.sim.getJointInfo(body_id, joint_ids)[-4])
        return np.array([self.sim.getJointInfo(body_id, joint_id)[-4] for joint_id in joint_ids])

    def set_joint_positions(self, body_id, joint_ids, positions, velocities=None, kps=None, kds=None, forces=None):
        """
        Set the position of the given joint(s) (using position control).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.
            positions (float, np.float[N]): desired position, or list of desired positions [rad]
            velocities (None, float, np.float[N]): desired velocity, or list of desired velocities [rad/s]
            kps (None, float, np.float[N]): position gain(s)
            kds (None, float, np.float[N]): velocity gain(s)
            forces (float): maximum motor force(s)/torque(s) used to reach the target values.
        """
        if isinstance(joint_ids, int):
            self.set_joint_motor_control(body_id, joint_ids, control_mode=pybullet.POSITION_CONTROL, position=positions,
                                         velocity=velocities, force=forces, kp=kps, kd=kds)
        else:
            self.set_joint_motor_control_array(body_id, joint_ids, control_mode=pybullet.POSITION_CONTROL,
                                               positions=positions, velocities=velocities, forces=forces, kps=kps,
                                               kds=kds)

    def get_joint_positions(self, body_id, joint_ids):
        """
        Get the position of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: joint position [rad]
            if multiple joints:
                np.float[N]: joint positions [rad]
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointState(body_id, joint_ids)[0]
        return np.array([state[0] for state in self.sim.getJointStates(body_id, joint_ids)])

    def set_joint_velocities(self, body_id, joint_ids, velocities, max_force=None):
        """
        Set the velocity of the given joint(s) (using velocity control).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.
            velocities (float, np.float[N]): desired velocity, or list of desired velocities [rad/s]
            max_force (bool, float, float[N]): maximum motor forces/torques
        """
        if isinstance(joint_ids, int):
            if max_force is None:
                self.sim.setJointMotorControl2(body_id, joint_ids, self.sim.VELOCITY_CONTROL, targetVelocity=velocities)
            self.sim.setJointMotorControl2(body_id, joint_ids, self.sim.VELOCITY_CONTROL, targetVelocity=velocities,
                                           force=max_force)
        if max_force is None:
            self.sim.setJointMotorControlArray(body_id, joint_ids, self.sim.VELOCITY_CONTROL,
                                               targetVelocities=velocities)
        self.sim.setJointMotorControlArray(body_id, joint_ids, self.sim.VELOCITY_CONTROL,
                                           targetVelocities=velocities, forces=max_force)

    def get_joint_velocities(self, body_id, joint_ids):
        """
        Get the velocity of the given joint(s).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: joint velocity [rad/s]
            if multiple joints:
                np.float[N]: joint velocities [rad/s]
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointState(body_id, joint_ids)[1]
        return np.array([state[1] for state in self.sim.getJointStates(body_id, joint_ids)])

    def set_joint_accelerations(self, body_id, joint_ids, accelerations, q=None, dq=None):
        """
        Set the acceleration of the given joint(s) (using force control). This is achieved by performing inverse
        dynamic which given the joint accelerations compute the joint torques to be applied.

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.
            accelerations (float, np.float[N]): desired joint acceleration, or list of desired joint accelerations
                [rad/s^2]
        """
        # check joint ids
        if isinstance(joint_ids, int):
            joint_ids = [joint_ids]
        if isinstance(accelerations, (int, float)):
            accelerations = [accelerations]
        if len(accelerations) != len(joint_ids):
            raise ValueError("Expecting the desired accelerations to be of the same size as the number of joints; "
                             "{} != {}".format(len(accelerations), len(joint_ids)))

        # get position and velocities
        if q is None or dq is None:
            joints = self.get_actuated_joint_ids(body_id)
            if q is None:
                q = self.get_joint_positions(body_id, joints)
            if dq is None:
                dq = self.get_joint_velocities(body_id, joints)

        num_actuated_joints = len(q)

        # if joint accelerations vector is not the same size as the actuated joints
        if len(accelerations) != num_actuated_joints:
            q_idx = self.get_qindex(joint_ids)
            acc = np.zeros(num_actuated_joints)
            acc[q_idx] = accelerations
            accelerations = acc

        # compute joint torques from Inverse Dynamics
        torques = self.calculate_inverse_dynamics(body_id, q, dq, accelerations)

        # get corresponding torques
        if len(torques) != len(joint_ids):
            q_idx = self.get_qindex(joint_ids)
            torques = torques[q_idx]

        # set the joint torques
        self.set_joint_torques(body_id, joint_ids, torques)

    def get_joint_accelerations(self, body_id, joint_ids, q=None, dq=None):
        """
        Get the acceleration at the given joint(s). This is carried out by first getting the joint torques, then
        performing forward dynamics to get the joint accelerations from the joint torques.

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.
            q (list of int, None): all the joint positions. If None, it will compute it.
            dq (list of int, None): all the joint velocities. If None, it will compute it.

        Returns:
            if 1 joint:
                float: joint acceleration [rad/s^2]
            if multiple joints:
                np.float[N]: joint accelerations [rad/s^2]
        """
        # get the torques
        torques = self.get_joint_torques(body_id, joint_ids)

        # get position and velocities
        if q is None or dq is None:
            joints = self.get_actuated_joint_ids(body_id)
            if q is None:
                q = self.get_joint_positions(body_id, joints)
            if dq is None:
                dq = self.get_joint_velocities(body_id, joints)

        # compute the accelerations
        accelerations = self.calculate_forward_dynamics(body_id, q, dq, torques=torques)

        # return the specified accelerations
        q_idx = self.get_qindex(body_id, joint_ids)
        return accelerations[q_idx]

    def set_joint_torques(self, body_id, joint_ids, torques):
        """
        Set the torque/force to the given joint(s) (using force/torque control).

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): joint id, or list of joint ids.
            torque (float, list of float): desired torque(s) to apply to the joint(s) [N].
        """
        if isinstance(joint_ids, int):
            self.sim.setJointMotorControl2(body_id, joint_ids, self.sim.TORQUE_CONTROL, force=torques)
        self.sim.setJointMotorControlArray(body_id, joint_ids, self.sim.TORQUE_CONTROL, forces=torques)

    def get_joint_torques(self, body_id, joint_ids):
        """
        Get the applied torque(s) on the given joint(s). "This is the motor torque applied during the last `step`.
        Note that this only applies in VELOCITY_CONTROL and POSITION_CONTROL. If you use TORQUE_CONTROL then the
        applied joint motor torque is exactly what you provide, so there is no need to report it separately." [1]

        Args:
            body_id (int): unique body id.
            joint_ids (int, list of int): a joint id, or list of joint ids.

        Returns:
            if 1 joint:
                float: torque [Nm]
            if multiple joints:
                np.float[N]: torques associated to the given joints [Nm]
        """
        if isinstance(joint_ids, int):
            return self.sim.getJointState(body_id, joint_ids)[3]
        return np.array([state[3] for state in self.sim.getJointStates(body_id, joint_ids)])

    def get_joint_reaction_forces(self, body_id, joint_ids):
        """
        Return the joint reaction forces at the given joint. Note that the torque sensor must be enabled, otherwise
        it will always return [0,0,0,0,0,0].

        Args:
            body_id (int): unique body id.
            joint_ids (int, int[N]): joint id, or list of joint ids

        Returns:
            if 1 joint:
                np.float[6]: joint reaction force (fx,fy,fz,mx,my,mz) [N,Nm]
            if multiple joints:
                np.float[N,6]: joint reaction forces [N, Nm]
        """
        if isinstance(joint_ids, int):
            return np.array(self.sim.getJointState(body_id, joint_ids)[2])
        return np.array([state[2] for state in self.sim.getJointStates(body_id, joint_ids)])

    def get_joint_powers(self, body_id, joint_ids):
        """
        Return the applied power at the given joint(s). Power = torque * velocity.

        Args:
            body_id (int): unique body id.
            joint_ids (int, int[N]): joint id, or list of joint ids

        Returns:
            if 1 joint:
                float: joint power [W]
            if multiple joints:
                np.float[N]: power at each joint [W]
        """
        torque = self.get_joint_torques(body_id, joint_ids)
        velocity = self.get_joint_velocities(body_id, joint_ids)
        return torque * velocity

    #################
    # visualization #
    #################

    def create_visual_shape(self, shape_type, radius=0.5, half_extents=(1., 1., 1.), length=1., filename=None,
                            mesh_scale=(1., 1., 1.), plane_normal=(0., 0., 1.), flags=-1, rgba_color=None,
                            specular_color=None, visual_frame_position=None, vertices=None, indices=None, uvs=None,
                            normals=None, visual_frame_orientation=None):
        """
        Create a visual shape in the simulator.

        Args:
            shape_type (int): type of shape; GEOM_SPHERE (=2), GEOM_BOX (=3), GEOM_CAPSULE (=7), GEOM_CYLINDER (=4),
                GEOM_PLANE (=6), GEOM_MESH (=5)
            radius (float): only for GEOM_SPHERE, GEOM_CAPSULE, GEOM_CYLINDER
            half_extents (np.float[3], list/tuple of 3 floats): only for GEOM_BOX.
            length (float): only for GEOM_CAPSULE, GEOM_CYLINDER (length = height).
            filename (str): Filename for GEOM_MESH, currently only Wavefront .obj. Will create convex hulls for each
                object (marked as 'o') in the .obj file.
            mesh_scale (np.float[3], list/tuple of 3 floats): scale of mesh (only for GEOM_MESH).
            plane_normal (np.float[3], list/tuple of 3 floats): plane normal (only for GEOM_PLANE).
            flags (int): unused / to be decided
            rgba_color (list/tuple of 4 floats): color components for red, green, blue and alpha, each in range [0..1].
            specular_color (list/tuple of 3 floats): specular reflection color, red, green, blue components in range
                [0..1]
            visual_frame_position (np.float[3]): translational offset of the visual shape with respect to the link frame
            vertices (list of np.float[3]): Instead of creating a mesh from obj file, you can provide vertices, indices,
                uvs and normals
            indices (list of int): triangle indices, should be a multiple of 3.
            uvs (list of np.float[2]): uv texture coordinates for vertices. Use changeVisualShape to choose the
                texture image. The number of uvs should be equal to number of vertices
            normals (list of np.float[3]): vertex normals, number should be equal to number of vertices.
            visual_frame_orientation (np.float[4]): rotational offset (quaternion x,y,z,w) of the visual shape with
                respect to the link frame

        Returns:
            int: The return value is a non-negative int unique id for the visual shape or -1 if the call failed.
        """
        # add few variables
        kwargs = {}
        if rgba_color is not None:
            kwargs['rgbaColor'] = rgba_color
        if specular_color is not None:
            kwargs['specularColor'] = specular_color
        if visual_frame_position is not None:
            kwargs['visualFramePosition'] = visual_frame_position
        if visual_frame_orientation is not None:
            kwargs['visualFrameOrientation'] = visual_frame_orientation

        if shape_type == self.sim.GEOM_SPHERE:
            return self.sim.createVisualShape(shape_type, radius=radius, **kwargs)
        elif shape_type == self.sim.GEOM_BOX:
            return self.sim.createVisualShape(shape_type, halfExtents=half_extents, **kwargs)
        elif shape_type == self.sim.GEOM_CAPSULE or shape_type == self.sim.GEOM_CYLINDER:
            return self.sim.createVisualShape(shape_type, radius=radius, length=length, **kwargs)
        elif shape_type == self.sim.GEOM_PLANE:
            return self.sim.createVisualShape(shape_type, planeNormal=plane_normal, **kwargs)
        elif shape_type == self.sim.GEOM_MESH:
            if filename is not None:
                kwargs['fileName'] = filename
            else:
                if vertices is not None:
                    kwargs['vertices'] = vertices
                if indices is not None:
                    kwargs['indices'] = indices
                if uvs is not None:
                    kwargs['uvs'] = uvs
                if normals is not None:
                    kwargs['normals'] = normals
            return self.sim.createVisualShape(shape_type, **kwargs)
        else:
            raise ValueError("Unknown visual shape type.")

    def get_visual_shape_data(self, object_id, flags=-1):
        """
        Get the visual shape data associated with the given object id.

        Args:
            object_id (int): object unique id.
            flags (int, None): VISUAL_SHAPE_DATA_TEXTURE_UNIQUE_IDS (=1) will also provide `texture_unique_id`.

        Returns:
            int: object unique id.
            int: link index or -1 for the base
            int: visual geometry type (TBD)
            np.float[3]: dimensions (size, local scale) of the geometry
            str: path to the triangle mesh, if any. Typically relative to the URDF, SDF or MJCF file location, but
                could be absolute
            np.float[3]: position of local visual frame, relative to link/joint frame
            np.float[4]: orientation of local visual frame relative to link/joint frame
            list of 4 floats: URDF color (if any specified) in Red / Green / Blue / Alpha
            int: texture unique id of the shape or -1 if None. This field only exists if using
                VISUAL_SHAPE_DATA_TEXTURE_UNIQUE_IDS (=1) flag.
        """
        return self.sim.getVisualShapeData(object_id, flags=flags)

    def change_visual_shape(self, object_id, link_id, shape_id=None, texture_id=None, rgba_color=None,
                            specular_color=None):
        """
        Allows to change the texture of a shape, the RGBA color and other properties.

        Args:
            object_id (int): unique object id.
            link_id (int): link id.
            shape_id (int): shape id.
            texture_id (int): texture id.
            rgba_color (float[4]): RGBA color. Each is in the range [0..1]. Alpha has to be 0 (invisible) or 1
                (visible) at the moment.
            specular_color (int[3]): specular color components, RED, GREEN and BLUE, can be from 0 to large number
                (>100).
        """
        kwargs = {}
        if shape_id is not None:
            kwargs['shapeIndex'] = shape_id
        if texture_id is not None:
            kwargs['textureUniqueId'] = texture_id
        if rgba_color is not None:
            kwargs['rgbaColor'] = rgba_color
        if specular_color is not None:
            kwargs['specularColor'] = specular_color
        self.sim.changeVisualShape(object_id, link_id, **kwargs)

    def load_texture(self, filename):
        """
        Load a texture from file and return a non-negative texture unique id if the loading succeeds.
        This unique id can be used with changeVisualShape.

        Args:
            filename (str): path to the file.

        Returns:
            int: texture unique id. If non-negative, the texture was loaded successfully.
        """
        return self.sim.loadTexture(filename)

    def compute_view_matrix(self, eye_position, target_position, up_vector):
        """Compute the view matrix.

        The view matrix is the 4x4 matrix that maps the world coordinates into the camera coordinates. Basically,
        it applies a rotation and translation such that the world is in front of the camera. That is, instead
        of turning the camera to capture what we want in the world, we keep the camera fixed and turn the world.

        Args:
            eye_position (np.float[3]): eye position in Cartesian world coordinates
            target_position (np.float[3]): position of the target (focus) point in Cartesian world coordinates
            up_vector (np.float[3]): up vector of the camera in Cartesian world coordinates

        Returns:
            np.float[4,4]: the view matrix

        More info:
            [1] http://www.codinglabs.net/article_world_view_projection_matrix.aspx
            [2] http://www.thecodecrate.com/opengl-es/opengl-transformation-matrices/
        """
        view = self.sim.computeViewMatrix(eyePosition=eye_position, targetPosition=target_position, upVector=up_vector)
        return np.array(view).reshape(4, 4).T

    def compute_view_matrix_from_ypr(self, target_position, distance, yaw, pitch, roll, up_axis_index=2):
        """Compute the view matrix from the yaw, pitch, and roll angles.

        The view matrix is the 4x4 matrix that maps the world coordinates into the camera coordinates. Basically,
        it applies a rotation and translation such that the world is in front of the camera. That is, instead
        of turning the camera to capture what we want in the world, we keep the camera fixed and turn the world.

        Args:
            target_position (np.float[3]): target focus point in Cartesian world coordinates
            distance (float): distance from eye to focus point
            yaw (float): yaw angle in radians left/right around up-axis
            pitch (float): pitch in radians up/down.
            roll (float): roll in radians around forward vector
            up_axis_index (int): either 1 for Y or 2 for Z axis up.

        Returns:
            np.float[4,4]: the view matrix

        More info:
            [1] http://www.codinglabs.net/article_world_view_projection_matrix.aspx
            [2] http://www.thecodecrate.com/opengl-es/opengl-transformation-matrices/
        """
        view = self.sim.computeViewMatrixFromYawPitchRoll(targetPosition=target_position, distance=distance,
                                                          yaw=np.rad2deg(yaw), pitch=np.rad2deg(pitch),
                                                          roll=np.rad2deg(roll), upAxisIndex=up_axis_index)
        return np.array(view).reshape(4, 4).T

    def compute_projection_matrix(self, left, right, bottom, top, near, far):
        """Compute the orthographic projection matrix.

        The projection matrix is the 4x4 matrix that maps from the camera/eye coordinates to clipped coordinates.
        It is applied after the view matrix.

        There are 2 projection matrices:
        * orthographic projection
        * perspective projection

        For the perspective projection, see `computeProjectionMatrixFOV(self)

        Args:
            left (float): left screen (canvas) coordinate
            right (float): right screen (canvas) coordinate
            bottom (float): bottom screen (canvas) coordinate
            top (float): top screen (canvas) coordinate
            near (float): near plane distance
            far (float): far plane distance

        Returns:
            np.float[4,4]: the perspective projection matrix

        More info:
            [1] http://www.codinglabs.net/article_world_view_projection_matrix.aspx
            [2] http://www.thecodecrate.com/opengl-es/opengl-transformation-matrices/
        """
        proj = self.sim.computeProjectionMatrix(left, right, bottom, top, near, far)
        return np.array(proj).reshape(4, 4).T

    def compute_projection_matrix_fov(self, fov, aspect, near, far):
        """Compute the perspective projection matrix using the field of view (FOV).

        Args:
            fov (float): field of view
            aspect (float): aspect ratio
            near (float): near plane distance
            far (float): far plane distance

        Returns:
            np.float[4,4]: the perspective projection matrix

        More info:
            [1] http://www.codinglabs.net/article_world_view_projection_matrix.aspx
            [2] http://www.thecodecrate.com/opengl-es/opengl-transformation-matrices/
        """
        proj = self.sim.computeProjectionMatrixFOV(fov, aspect, near, far)
        return np.array(proj).reshape(4, 4).T

    def get_camera_image(self, width, height, view_matrix=None, projection_matrix=None, light_direction=None,
                         light_color=None, light_distance=None, shadow=None, light_ambient_coeff=None,
                         light_diffuse_coeff=None, light_specular_coeff=None, renderer=None, flags=None):
        """
        The `get_camera_image` API will return a RGB image, a depth buffer and a segmentation mask buffer with body
        unique ids of visible objects for each pixel. Note that PyBullet can be compiled using the numpy option:
        using numpy will improve the performance of copying the camera pixels from C to Python.

        Note that copying pixels from C/C++ to Python can be really slow for large images, unless you compile PyBullet
        using NumPy. You can check if NumPy is enabled using `PyBullet.isNumpyEnabled()`. `pip install pybullet` has
        NumPy enabled, if available on the system.

        Args:
            width (int): horizontal image resolution in pixels
            height (int): vertical image resolution in pixels
            view_matrix (np.float[4,4]): 4x4 view matrix, see `compute_view_matrix`
            projection_matrix (np.float[4,4]): 4x4 projection matrix, see `compute_projection`
            light_direction (np.float[3]): `light_direction` specifies the world position of the light source,
                the direction is from the light source position to the origin of the world frame.
            light_color (np.float[3]): directional light color in [RED,GREEN,BLUE] in range 0..1
            light_distance (float): distance of the light along the normalized `light_direction`
            shadow (bool): True for shadows, False for no shadows
            light_ambient_coeff (float): light ambient coefficient
            light_diffuse_coeff (float): light diffuse coefficient
            light_specular_coeff (float): light specular coefficient
            renderer (int): ER_BULLET_HARDWARE_OPENGL (=131072) or ER_TINY_RENDERER (=65536). Note that DIRECT (=2)
                mode has no OpenGL, so it requires ER_TINY_RENDERER (=65536).
            flags (int): ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1), See below in description of
                segmentationMaskBuffer and example code. Use ER_NO_SEGMENTATION_MASK (=4) to avoid calculating the
                segmentation mask.

        Returns:
            int: width image resolution in pixels (horizontal)
            int: height image resolution in pixels (vertical)
            np.int[width, height, 4]: RBGA pixels (each pixel is in the range [0..255] for each channel R, G, B, A)
            np.float[width, heigth]: Depth buffer. Bullet uses OpenGL to render, and the convention is non-linear
                z-buffer. See https://stackoverflow.com/questions/6652253/getting-the-true-z-value-from-the-depth-buffer
                Using the projection matrix, the depth is computed as:
                `depth = far * near / (far - (far - near) * depthImg)`, where `depthImg` is the depth from Bullet
                `getCameraImage`, far=1000. and near=0.01.
            np.int[width, height]: Segmentation mask buffer. For each pixels the visible object unique id.
                If ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1) is used, the segmentationMaskBuffer combines the
                object unique id and link index as follows: value = objectUniqueId + (linkIndex+1)<<24.
                So for a free floating body without joints/links, the segmentation mask is equal to its body unique id,
                since its link index is -1.
        """
        kwargs = {}
        if view_matrix is not None:
            if isinstance(view_matrix, np.ndarray):
                kwargs['viewMatrix'] = view_matrix.T.ravel().tolist()
            else:
                kwargs['viewMatrix'] = view_matrix
        if projection_matrix is not None:
            if isinstance(projection_matrix, np.ndarray):
                kwargs['projectionMatrix'] = projection_matrix.T.ravel().tolist()
            else:
                kwargs['projectionMatrix'] = projection_matrix
        if light_direction is not None:
            if isinstance(light_direction, np.ndarray):
                kwargs['lightDirection'] = light_direction.ravel().tolist()
            else:
                kwargs['lightDirection'] = light_direction
        if light_color is not None:
            if isinstance(light_color, np.ndarray):
                kwargs['lightColor'] = light_color
            else:
                kwargs['lightColor'] = light_color
        if light_distance is not None:
            kwargs['lightDistance'] = light_distance
        if shadow is not None:
            kwargs['shadow'] = int(shadow)
        if light_ambient_coeff is not None:
            kwargs['lightAmbientCoeff'] = light_ambient_coeff
        if light_diffuse_coeff is not None:
            kwargs['lightDiffuseCoeff'] = light_diffuse_coeff
        if light_specular_coeff is not None:
            kwargs['lightSpecularCoeff'] = light_specular_coeff
        if renderer is not None:
            kwargs['renderer'] = renderer
        if flags is not None:
            kwargs['flags'] = flags

        width, height, rgba, depth, segmentation = self.sim.getCameraImage(width, height, **kwargs)
        rgba = np.array(rgba).reshape(width, height, 4)
        depth = np.array(depth).reshape(width, height)
        segmentation = np.array(segmentation).reshape(width, height)
        return width, height, rgba, depth, segmentation

    def get_rgba_image(self, width, height, view_matrix=None, projection_matrix=None, light_direction=None,
                       light_color=None, light_distance=None, shadow=None, light_ambient_coeff=None,
                       light_diffuse_coeff=None, light_specular_coeff=None, renderer=None, flags=None):
        """
        The `get_rgba_image` API will return a RGBA image. Note that PyBullet can be compiled using the numpy option:
        using numpy will improve the performance of copying the camera pixels from C to Python.

        Note that copying pixels from C/C++ to Python can be really slow for large images, unless you compile PyBullet
        using NumPy. You can check if NumPy is enabled using `PyBullet.isNumpyEnabled()`. `pip install pybullet` has
        NumPy enabled, if available on the system.

        Args:
            width (int): horizontal image resolution in pixels
            height (int): vertical image resolution in pixels
            view_matrix (np.float[4,4]): 4x4 view matrix, see `compute_view_matrix`
            projection_matrix (np.float[4,4]): 4x4 projection matrix, see `compute_projection`
            light_direction (np.float[3]): `light_direction` specifies the world position of the light source,
                the direction is from the light source position to the origin of the world frame.
            light_color (np.float[3]): directional light color in [RED,GREEN,BLUE] in range 0..1
            light_distance (float): distance of the light along the normalized `light_direction`
            shadow (bool): True for shadows, False for no shadows
            light_ambient_coeff (float): light ambient coefficient
            light_diffuse_coeff (float): light diffuse coefficient
            light_specular_coeff (float): light specular coefficient
            renderer (int): ER_BULLET_HARDWARE_OPENGL (=131072) or ER_TINY_RENDERER (=65536). Note that DIRECT (=2)
                mode has no OpenGL, so it requires ER_TINY_RENDERER (=65536).
            flags (int): ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1), See below in description of
                segmentationMaskBuffer and example code. Use ER_NO_SEGMENTATION_MASK (=4) to avoid calculating the
                segmentation mask.

        Returns:
            np.int[width, height, 4]: RBGA pixels (each pixel is in the range [0..255] for each channel R, G, B, A)
        """
        kwargs = {}
        if view_matrix is not None:
            if isinstance(view_matrix, np.ndarray):
                kwargs['viewMatrix'] = view_matrix.T.ravel().tolist()
            else:
                kwargs['viewMatrix'] = view_matrix
        if projection_matrix is not None:
            if isinstance(projection_matrix, np.ndarray):
                kwargs['projectionMatrix'] = projection_matrix.T.ravel().tolist()
            else:
                kwargs['projectionMatrix'] = projection_matrix
        if light_direction is not None:
            if isinstance(light_direction, np.ndarray):
                kwargs['lightDirection'] = light_direction.ravel().tolist()
            else:
                kwargs['lightDirection'] = light_direction
        if light_color is not None:
            if isinstance(light_color, np.ndarray):
                kwargs['lightColor'] = light_color
            else:
                kwargs['lightColor'] = light_color
        if light_distance is not None:
            kwargs['lightDistance'] = light_distance
        if shadow is not None:
            kwargs['shadow'] = int(shadow)
        if light_ambient_coeff is not None:
            kwargs['lightAmbientCoeff'] = light_ambient_coeff
        if light_diffuse_coeff is not None:
            kwargs['lightDiffuseCoeff'] = light_diffuse_coeff
        if light_specular_coeff is not None:
            kwargs['lightSpecularCoeff'] = light_specular_coeff
        if renderer is not None:
            kwargs['renderer'] = renderer
        if flags is not None:
            kwargs['flags'] = flags

        img = np.array(self.sim.getCameraImage(width, height, **kwargs)[2])
        img = img.reshape(width, height, 4)  # RGBA
        return img

    def get_depth_image(self, width, height, view_matrix=None, projection_matrix=None, light_direction=None,
                        light_color=None, light_distance=None, shadow=None, light_ambient_coeff=None,
                        light_diffuse_coeff=None, light_specular_coeff=None, renderer=None, flags=None):
        """
        The `get_depth_image` API will return a depth buffer. Note that PyBullet can be compiled using the numpy option:
        using numpy will improve the performance of copying the camera pixels from C to Python.

        Note that copying pixels from C/C++ to Python can be really slow for large images, unless you compile PyBullet
        using NumPy. You can check if NumPy is enabled using `PyBullet.isNumpyEnabled()`. `pip install pybullet` has
        NumPy enabled, if available on the system.

        Args:
            width (int): horizontal image resolution in pixels
            height (int): vertical image resolution in pixels
            view_matrix (np.float[4,4]): 4x4 view matrix, see `compute_view_matrix`
            projection_matrix (np.float[4,4]): 4x4 projection matrix, see `compute_projection`
            light_direction (np.float[3]): `light_direction` specifies the world position of the light source,
                the direction is from the light source position to the origin of the world frame.
            light_color (np.float[3]): directional light color in [RED,GREEN,BLUE] in range 0..1
            light_distance (float): distance of the light along the normalized `light_direction`
            shadow (bool): True for shadows, False for no shadows
            light_ambient_coeff (float): light ambient coefficient
            light_diffuse_coeff (float): light diffuse coefficient
            light_specular_coeff (float): light specular coefficient
            renderer (int): ER_BULLET_HARDWARE_OPENGL (=131072) or ER_TINY_RENDERER (=65536). Note that DIRECT (=2)
                mode has no OpenGL, so it requires ER_TINY_RENDERER (=65536).
            flags (int): ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1), See below in description of
                segmentationMaskBuffer and example code. Use ER_NO_SEGMENTATION_MASK (=4) to avoid calculating the
                segmentation mask.

        Returns:
            np.float[width, heigth]: Depth buffer. Bullet uses OpenGL to render, and the convention is non-linear
                z-buffer. See https://stackoverflow.com/questions/6652253/getting-the-true-z-value-from-the-depth-buffer
                Using the projection matrix, the depth is computed as:
                `depth = far * near / (far - (far - near) * depthImg)`, where `depthImg` is the depth from Bullet
                `getCameraImage`, far=1000. and near=0.01.
        """
        kwargs = {}
        if view_matrix is not None:
            if isinstance(view_matrix, np.ndarray):
                kwargs['viewMatrix'] = view_matrix.T.ravel().tolist()
            else:
                kwargs['viewMatrix'] = view_matrix
        if projection_matrix is not None:
            if isinstance(projection_matrix, np.ndarray):
                kwargs['projectionMatrix'] = projection_matrix.T.ravel().tolist()
            else:
                kwargs['projectionMatrix'] = projection_matrix
        if light_direction is not None:
            if isinstance(light_direction, np.ndarray):
                kwargs['lightDirection'] = light_direction.ravel().tolist()
            else:
                kwargs['lightDirection'] = light_direction
        if light_color is not None:
            if isinstance(light_color, np.ndarray):
                kwargs['lightColor'] = light_color
            else:
                kwargs['lightColor'] = light_color
        if light_distance is not None:
            kwargs['lightDistance'] = light_distance
        if shadow is not None:
            kwargs['shadow'] = int(shadow)
        if light_ambient_coeff is not None:
            kwargs['lightAmbientCoeff'] = light_ambient_coeff
        if light_diffuse_coeff is not None:
            kwargs['lightDiffuseCoeff'] = light_diffuse_coeff
        if light_specular_coeff is not None:
            kwargs['lightSpecularCoeff'] = light_specular_coeff
        if renderer is not None:
            kwargs['renderer'] = renderer
        if flags is not None:
            kwargs['flags'] = flags

        img = np.array(self.sim.getCameraImage(width, height, **kwargs)[3])
        img = img.reshape(width, height)
        return img

    def get_segmentation_image(self, width, height, view_matrix=None, projection_matrix=None, light_direction=None,
                               light_color=None, light_distance=None, shadow=None, light_ambient_coeff=None,
                               light_diffuse_coeff=None, light_specular_coeff=None, renderer=None, flags=None):
        """
        The `get_segmentation_image` API will return a segmentation mask buffer with body unique ids of visible objects
        for each pixel. Note that PyBullet can be compiled using the numpy option: using numpy will improve
        the performance of copying the camera pixels from C to Python.

        Note that copying pixels from C/C++ to Python can be really slow for large images, unless you compile PyBullet
        using NumPy. You can check if NumPy is enabled using `PyBullet.isNumpyEnabled()`. `pip install pybullet` has
        NumPy enabled, if available on the system.

        Args:
            width (int): horizontal image resolution in pixels
            height (int): vertical image resolution in pixels
            view_matrix (np.float[4,4]): 4x4 view matrix, see `compute_view_matrix`
            projection_matrix (np.float[4,4]): 4x4 projection matrix, see `compute_projection`
            light_direction (np.float[3]): `light_direction` specifies the world position of the light source,
                the direction is from the light source position to the origin of the world frame.
            light_color (np.float[3]): directional light color in [RED,GREEN,BLUE] in range 0..1
            light_distance (float): distance of the light along the normalized `light_direction`
            shadow (bool): True for shadows, False for no shadows
            light_ambient_coeff (float): light ambient coefficient
            light_diffuse_coeff (float): light diffuse coefficient
            light_specular_coeff (float): light specular coefficient
            renderer (int): ER_BULLET_HARDWARE_OPENGL (=131072) or ER_TINY_RENDERER (=65536). Note that DIRECT (=2)
                mode has no OpenGL, so it requires ER_TINY_RENDERER (=65536).
            flags (int): ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1), See below in description of
                segmentationMaskBuffer and example code. Use ER_NO_SEGMENTATION_MASK (=4) to avoid calculating the
                segmentation mask.

        Returns:
            np.int[width, height]: Segmentation mask buffer. For each pixels the visible object unique id.
                If ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX (=1) is used, the segmentationMaskBuffer combines the
                object unique id and link index as follows: value = objectUniqueId + (linkIndex+1)<<24.
                So for a free floating body without joints/links, the segmentation mask is equal to its body unique id,
                since its link index is -1.
        """
        kwargs = {}
        if view_matrix is not None:
            if isinstance(view_matrix, np.ndarray):
                kwargs['viewMatrix'] = view_matrix.T.ravel().tolist()
            else:
                kwargs['viewMatrix'] = view_matrix
        if projection_matrix is not None:
            if isinstance(projection_matrix, np.ndarray):
                kwargs['projectionMatrix'] = projection_matrix.T.ravel().tolist()
            else:
                kwargs['projectionMatrix'] = projection_matrix
        if light_direction is not None:
            if isinstance(light_direction, np.ndarray):
                kwargs['lightDirection'] = light_direction.ravel().tolist()
            else:
                kwargs['lightDirection'] = light_direction
        if light_color is not None:
            if isinstance(light_color, np.ndarray):
                kwargs['lightColor'] = light_color
            else:
                kwargs['lightColor'] = light_color
        if light_distance is not None:
            kwargs['lightDistance'] = light_distance
        if shadow is not None:
            kwargs['shadow'] = int(shadow)
        if light_ambient_coeff is not None:
            kwargs['lightAmbientCoeff'] = light_ambient_coeff
        if light_diffuse_coeff is not None:
            kwargs['lightDiffuseCoeff'] = light_diffuse_coeff
        if light_specular_coeff is not None:
            kwargs['lightSpecularCoeff'] = light_specular_coeff
        if renderer is not None:
            kwargs['renderer'] = renderer
        if flags is not None:
            kwargs['flags'] = flags

        img = np.array(self.sim.getCameraImage(width, height, **kwargs)[4])
        img = img.reshape(width, height)
        return img

    ##############
    # Collisions #
    ##############

    def create_collision_shape(self, shape_type, radius=0.5, half_extents=(1., 1., 1.), height=1., filename=None,
                               mesh_scale=(1., 1., 1.), plane_normal=(0., 0., 1.), flags=-1,
                               collision_frame_position=None, collision_frame_orientation=None):
        """
        Create collision shape in the simulator.

        Args:
            shape_type (int): type of shape; GEOM_SPHERE (=2), GEOM_BOX (=3), GEOM_CAPSULE (=7), GEOM_CYLINDER (=4),
                GEOM_PLANE (=6), GEOM_MESH (=5)
            radius (float): only for GEOM_SPHERE, GEOM_CAPSULE, GEOM_CYLINDER
            half_extents (np.float[3], list/tuple of 3 floats): only for GEOM_BOX.
            height (float): only for GEOM_CAPSULE, GEOM_CYLINDER (length = height).
            filename (str): Filename for GEOM_MESH, currently only Wavefront .obj. Will create convex hulls for each
                object (marked as 'o') in the .obj file.
            mesh_scale (np.float[3], list/tuple of 3 floats): scale of mesh (only for GEOM_MESH).
            plane_normal (np.float[3], list/tuple of 3 floats): plane normal (only for GEOM_PLANE).
            flags (int): unused / to be decided
            collision_frame_position (np.float[3]): translational offset of the collision shape with respect to the
                link frame
            collision_frame_orientation (np.float[4]): rotational offset (quaternion x,y,z,w) of the collision shape
                with respect to the link frame

        Returns:
            int: The return value is a non-negative int unique id for the collision shape or -1 if the call failed.
        """
        # add few variables
        kwargs = {}
        if collision_frame_position is not None:
            kwargs['collisionFramePosition'] = collision_frame_position
        if collision_frame_orientation is not None:
            kwargs['collisionFrameOrientation'] = collision_frame_orientation

        if shape_type == self.sim.GEOM_SPHERE:
            return self.sim.createCollisionShape(shape_type, radius=radius, **kwargs)
        elif shape_type == self.sim.GEOM_BOX:
            return self.sim.createCollisionShape(shape_type, halfExtents=half_extents, **kwargs)
        elif shape_type == self.sim.GEOM_CAPSULE or shape_type == self.sim.GEOM_CYLINDER:
            return self.sim.createCollisionShape(shape_type, radius=radius, height=height, **kwargs)
        elif shape_type == self.sim.GEOM_PLANE:
            return self.sim.createCollisionShape(shape_type, planeNormal=plane_normal, **kwargs)
        elif shape_type == self.sim.GEOM_MESH:
            return self.sim.createCollisionShape(shape_type, fileName=filename, **kwargs)
        else:
            raise ValueError("Unknown collision shape type.")

    def get_collision_shape_data(self, object_id, link_id=-1):
        """
        Get the collision shape data associated with the specified object id and link id.

        Args:
            object_id (int): object unique id.
            link_id (int): link index or -1 for the base.

        Returns:
            int: object unique id.
            int: link id.
            int: geometry type; GEOM_BOX (=3), GEOM_SPHERE (=2), GEOM_CAPSULE (=7), GEOM_MESH (=5), GEOM_PLANE (=6)
            np.float[3]: depends on geometry type:
                for GEOM_BOX: extents,
                for GEOM_SPHERE: dimensions[0] = radius,
                for GEOM_CAPSULE and GEOM_CYLINDER: dimensions[0] = height (length), dimensions[1] = radius.
                For GEOM_MESH: dimensions is the scaling factor.
            str: Only for GEOM_MESH: file name (and path) of the collision mesh asset.
            np.float[3]: Local position of the collision frame with respect to the center of mass/inertial frame
            np.float[4]: Local orientation of the collision frame with respect to the inertial frame
        """
        object_id, link_id, geom_type, dimensions, filename, \
            position, orientation = self.sim.getCollisionShapeData(object_id, link_id)
        return object_id, link_id, geom_type, np.array(dimensions), filename, np.array(position), np.array(orientation)

    def get_overlapping_objects(self, aabb_min, aabb_max):
        """
        This query will return all the unique ids of objects that have Axis Aligned Bounding Box (AABB) overlap with
        a given axis aligned bounding box. Note that the query is conservative and may return additional objects that
        don't have actual AABB overlap. This happens because the acceleration structures have some heuristic that
        enlarges the AABBs a bit (extra margin and extruded along the velocity vector).

        Args:
            aabb_min (np.float[3]): minimum coordinates of the aabb
            aabb_max (np.float[3]): maximum coordinates of the aabb

        Returns:
            list of int: list of object unique ids.
        """
        return self.sim.getOverlappingObjects(aabb_min, aabb_max)

    def get_aabb(self, body_id, link_id=-1):
        """
        You can query the axis aligned bounding box (in world space) given an object unique id, and optionally a link
        index. (when you don't pass the link index, or use -1, you get the AABB of the base).

        Args:
            body_id (int): object unique id as returned by creation methods
            link_id (int): link index in range [0..`getNumJoints(..)]

        Returns:
            np.float[3]: minimum coordinates of the axis aligned bounding box
            np.float[3]: maximum coordinates of the axis aligned bounding box
        """
        aabb_min, aabb_max = self.sim.getAABB(body_id, link_id)
        return np.array(aabb_min), np.array(aabb_max)

    def get_contact_points(self, body_a, body_b, link_id_a=None, link_id_b=None):
        """
        Returns the contact points computed during the most recent call to `step`.

        Args:
            body_a (int): only report contact points that involve body A
            body_b (int): only report contact points that involve body B. Important: you need to have a valid body A
                if you provide body B
            link_id_a (int): only report contact points that involve link index of body A
            link_id_b (int): only report contact points that involve link index of body B

        Returns:
            list:
                int: contact flag (reserved)
                int: body unique id of body A
                int: body unique id of body B
                int: link index of body A, -1 for base
                int: link index of body B, -1 for base
                np.float[3]: contact position on A, in Cartesian world coordinates
                np.float[3]: contact position on B, in Cartesian world coordinates
                np.float[3]: contact normal on B, pointing towards A
                float: contact distance, positive for separation, negative for penetration
                float: normal force applied during the last `step`
                float: lateral friction force in the first lateral friction direction (see next returned value)
                np.float[3]: first lateral friction direction
                float: lateral friction force in the second lateral friction direction (see next returned value)
                np.float[3]: second lateral friction direction
        """
        kwargs = {}
        if body_a is not None:
            kwargs['bodyA'] = body_a
            if link_id_a is not None:
                kwargs['linkIndexA'] = link_id_a
        if body_b is not None:
            kwargs['bodyB'] = body_b
            if link_id_b is not None:
                kwargs['linkIndexB'] = link_id_b

        results = self.sim.getContactPoints(**kwargs)
        if len(results) == 0:
            return results
        return [[r[0], r[1], r[2], r[3], r[4], np.array(r[5]), np.array(r[6]), np.array(r[7]), r[8], r[9], r[10],
                 np.array(r[11]), r[12], np.array(r[13])] for r in results]

    def get_closest_points(self, body_a, body_b, distance, link_id_a=None, link_id_b=None):
        """
        Computes the closest points, independent from `step`. This also lets you compute closest points of objects
        with an arbitrary separating distance. In this query there will be no normal forces reported.

        Args:
            body_a (int): only report contact points that involve body A
            body_b (int): only report contact points that involve body B. Important: you need to have a valid body A
                if you provide body B
            distance (float): If the distance between objects exceeds this maximum distance, no points may be returned.
            link_id_a (int): only report contact points that involve link index of body A
            link_id_b (int): only report contact points that involve link index of body B

        Returns:
            list:
                int: contact flag (reserved)
                int: body unique id of body A
                int: body unique id of body B
                int: link index of body A, -1 for base
                int: link index of body B, -1 for base
                np.float[3]: contact position on A, in Cartesian world coordinates
                np.float[3]: contact position on B, in Cartesian world coordinates
                np.float[3]: contact normal on B, pointing towards A
                float: contact distance, positive for separation, negative for penetration
                float: normal force applied during the last `step`. Always equal to 0.
                float: lateral friction force in the first lateral friction direction (see next returned value)
                np.float[3]: first lateral friction direction
                float: lateral friction force in the second lateral friction direction (see next returned value)
                np.float[3]: second lateral friction direction
        """
        kwargs = {}
        if link_id_a is not None:
            kwargs['linkIndexA'] = link_id_a
        if link_id_b is not None:
            kwargs['linkIndexB'] = link_id_b

        results = self.sim.getContactPoints(body_a, body_b, distance, **kwargs)
        if len(results) == 0:
            return results
        return [[r[0], r[1], r[2], r[3], r[4], np.array(r[5]), np.array(r[6]), np.array(r[7]), r[8], r[9], r[10],
                 np.array(r[11]), r[12], np.array(r[13])] for r in results]

    def ray_test(self, from_position, to_position):
        """
        Performs a single raycast to find the intersection information of the first object hit.

        Args:
            from_position (np.float[3]): start of the ray in world coordinates
            to_position (np.float[3]): end of the ray in world coordinates

        Returns:
            int: object unique id of the hit object
            int: link index of the hit object, or -1 if none/parent
            float: hit fraction along the ray in range [0,1] along the ray.
            np.float[3]: hit position in Cartesian world coordinates
            np.float[3]: hit normal in Cartesian world coordinates
        """
        if isinstance(from_position, np.ndarray):
            from_position = from_position.ravel().tolist()
        if isinstance(to_position, np.ndarray):
            to_position = to_position.ravel().tolist()
        object_id, link_id, hit_fraction, position, normal = self.sim.rayTest(from_position, to_position)
        return object_id, link_id, hit_fraction, np.array(position), np.array(normal)

    def ray_test_batch(self, from_positions, to_positions, parent_object_id=None, parent_link_id=None):
        """Perform a batch of raycasts to find the intersection information of the first objects hit.

        This is similar to the rayTest, but allows you to provide an array of rays, for faster execution. The size of
        'rayFromPositions' needs to be equal to the size of 'rayToPositions'. You can one ray result per ray, even if
        there is no intersection: you need to use the objectUniqueId field to check if the ray has hit anything: if
        the objectUniqueId is -1, there is no hit. In that case, the 'hit fraction' is 1. The maximum number of rays
        per batch is `pybullet.MAX_RAY_INTERSECTION_BATCH_SIZE`.

        Args:
            from_positions (np.array[N,3]): list of start points for each ray, in world coordinates
            to_positions (np.array[N,3]): list of end points for each ray in world coordinates
            parent_object_id (int): ray from/to is in local space of a parent object
            parent_link_id (int): ray from/to is in local space of a parent object

        Returns:
            list:
                int: object unique id of the hit object
                int: link index of the hit object, or -1 if none/parent
                float: hit fraction along the ray in range [0,1] along the ray.
                np.float[3]: hit position in Cartesian world coordinates
                np.float[3]: hit normal in Cartesian world coordinates
        """
        if isinstance(from_positions, np.ndarray):
            from_positions = from_positions.tolist()
        if isinstance(to_positions, np.ndarray):
            to_positions = to_positions.tolist()

        kwargs = {}
        if parent_object_id is not None:
            kwargs['parentObjectUniqueId'] = parent_object_id
            if parent_link_id is not None:
                kwargs['parentLinkIndex'] = parent_link_id

        results = self.sim.rayTestBatch(from_positions, to_positions, **kwargs)
        if len(results) == 0:
            return results
        return [[r[0], r[1], r[2], np.array(r[3]), np.array(r[4])] for r in results]

    def set_collision_filter_group_mask(self, body_id, link_id, filter_group, filter_mask):
        """
        Enable/disable collision detection between groups of objects. Each body is part of a group. It collides with
        other bodies if their group matches the mask, and vise versa. The following check is performed using the group
        and mask of the two bodies involved. It depends on the collision filter mode.

        Args:
            body_id (int): unique id of the body to be configured
            link_id (int): link index of the body to be configured
            filter_group (int): bitwise group of the filter
            filter_mask (int): bitwise mask of the filter
        """
        self.sim.setCollisionFilterGroupMask(body_id, link_id, filter_group, filter_mask)

    def set_collision_filter_pair(self, body_a, body_b, link_a=-1, link_b=-1, enable=True):
        """
        Enable/disable collision between two bodies/links.

        Args:
            body_a (int): unique id of body A to be filtered
            body_b (int): unique id of body B to be filtered, A==B implies self-collision
            link_a (int): link index of body A
            link_b (int): link index of body B
            enable (bool): True to enable collision, False to disable collision
        """
        self.sim.setCollisionFilterPair(body_a, body_b, link_a, link_b, int(enable))

    ###########################
    # Kinematics and Dynamics #
    ###########################

    def get_dynamics_info(self, body_id, link_id=-1):
        """
        Get dynamic information about the mass, center of mass, friction and other properties of the base and links.

        Args:
            body_id (int): body/object unique id.
            link_id (int): link/joint index or -1 for the base.

        Returns:
            float: mass in kg
            float: friction coefficient
            np.float[3]: local inertia diagonal. Note that links and base are centered around the center of mass and
                aligned with the principal axes of inertia.
            np.float[3]: position of inertial frame in local coordinates of the joint frame
            np.float[4]: orientation of inertial frame in local coordinates of joint frame
            float: coefficient of restitution
            float: rolling friction coefficient orthogonal to contact normal
            float: spinning friction coefficient around contact normal
            float: damping of contact constraints. -1 if not available.
            float: stiffness of contact constraints. -1 if not available.
        """
        mass, friction, inertia, pos, quat, restitution, roll, spin, kd, kp = self.sim.getDynamicsInfo(body_id, link_id)
        return mass, friction, np.array(inertia), np.array(pos), np.array(quat), restitution, roll, spin, kd, kp

    def change_dynamics(self, body_id, link_id=-1, mass=None, lateral_friction=None, spinning_friction=None,
                        rolling_friction=None, restitution=None, linear_damping=None, angular_damping=None,
                        contact_stiffness=None, contact_damping=None, friction_anchor=None,
                        local_inertia_diagonal=None, joint_damping=None):
        """
        Change dynamic properties such as mass, friction and restitution coefficients .

        Args:
            body_id (int): object unique id, as returned by `load_urdf`, etc.
            link_id (int): link index or -1 for the base.
            mass (float): change the mass of the link (or base for link index -1)
            lateral_friction (float): lateral (linear) contact friction
            spinning_friction (float): torsional friction around the contact normal
            rolling_friction (float): torsional friction orthogonal to contact normal
            restitution (float): bouncyness of contact. Keep it a bit less than 1.
            linear_damping (float): linear damping of the link (0.04 by default)
            angular_damping (float): angular damping of the link (0.04 by default)
            contact_stiffness (float): stiffness of the contact constraints, used together with `contact_damping`
            contact_damping (float): damping of the contact constraints for this body/link. Used together with
                `contact_stiffness`. This overrides the value if it was specified in the URDF file in the contact
                section.
            friction_anchor (int): enable or disable a friction anchor: positional friction correction (disabled by
                default, unless set in the URDF contact section)
            local_inertia_diagonal (np.float[3]): diagonal elements of the inertia tensor. Note that the base and
                links are centered around the center of mass and aligned with the principal axes of inertia so there
                are no off-diagonal elements in the inertia tensor.
            joint_damping (float): joint damping coefficient applied at each joint. This coefficient is read from URDF
                joint damping field. Keep the value close to 0.
                `joint_damping_force = -damping_coefficient * joint_velocity`.
        """
        kwargs = {}
        if mass is not None:
            kwargs['mass'] = mass
        if lateral_friction is not None:
            kwargs['lateralFriction'] = lateral_friction
        if spinning_friction is not None:
            kwargs['spinningFriction'] = spinning_friction
        if rolling_friction is not None:
            kwargs['rollingFriction'] = rolling_friction
        if restitution is not None:
            kwargs['restitution'] = restitution
        if linear_damping is not None:
            kwargs['linearDamping'] = linear_damping
        if angular_damping is not None:
            kwargs['angularDamping'] = angular_damping
        if contact_stiffness is not None:
            kwargs['contactStiffness'] = contact_stiffness
        if contact_damping is not None:
            kwargs['contactDamping'] = contact_damping
        if friction_anchor is not None:
            kwargs['frictionAnchor'] = friction_anchor
        if local_inertia_diagonal is not None:
            kwargs['localInertiaDiagonal'] = local_inertia_diagonal
        if joint_damping is not None:
            kwargs['jointDamping'] = joint_damping

        self.sim.changeDynamics(body_id, link_id, **kwargs)

    def calculate_jacobian(self, body_id, link_id, local_position, q, dq, des_ddq):
        """
        Return the full geometric Jacobian matrix :math:`J(q) = [J_{lin}(q), J_{ang}(q)]^T`, such that:

        .. math:: v = [\dot{p}, \omega]^T = J(q) \dot{q}

        where :math:`\dot{p}` is the Cartesian linear velocity of the link, and :math:`\omega` is its angular velocity.

        Warnings: if we have a floating base then the Jacobian will also include columns corresponding to the root
            link DoFs (at the beginning). If it is a fixed base, it will only have columns associated with the joints.

        Args:
            body_id (int): unique body id.
            link_id (int): link id.
            local_position (np.float[3]): the point on the specified link to compute the Jacobian (in link local
                coordinates around its center of mass). If None, it will use the CoM position (in the link frame).
            q (np.float[N]): joint positions of size N, where N is the number of DoFs.
            dq (np.float[N]): joint velocities of size N, where N is the number of DoFs.
            des_ddq (np.float[N]): desired joint accelerations of size N.

        Returns:
            np.float[6,N], np.float[6,(6+N)]: full geometric (linear and angular) Jacobian matrix. The number of
                columns depends if the base is fixed or floating.
        """
        # Note that q, dq, ddq have to be lists in PyBullet (it doesn't work with numpy arrays)
        if isinstance(local_position, np.ndarray):
            local_position = local_position.ravel().tolist()
        if isinstance(q, np.ndarray):
            q = q.ravel().tolist()
        if isinstance(dq, np.ndarray):
            dq = dq.ravel().tolist()
        if isinstance(des_ddq, np.ndarray):
            des_ddq = des_ddq.ravel().tolist()

        # calculate full jacobian
        lin_jac, ang_jac = self.sim.calculateJacobian(body_id, link_id, localPosition=local_position,
                                                      objPositions=q, objVelocities=dq, objAccelerations=des_ddq)

        return np.vstack((lin_jac, ang_jac))

    def calculate_mass_matrix(self, body_id, q):
        """
        Return the mass/inertia matrix :math:`H(q)`, which is used in the rigid-body equation of motion (EoM) in joint
        space given by (see [1]):

        .. math:: \tau = H(q)\ddot{q} + C(q,\dot{q})

        where :math:`\tau` is the vector of applied torques, :math:`H(q)` is the inertia matrix, and
        :math:`C(q,\dot{q}) \dot{q}` is the vector accounting for Coriolis, centrifugal forces, gravity, and any
        other forces acting on the system except the applied torques :math:`\tau`.

        Warnings: If the base is floating, it will return a [6+N,6+N] inertia matrix, where N is the number of actuated
            joints. If the base is fixed, it will return a [N,N] inertia matrix

        Args:
            body_id (int): body unique id.
            q (np.float[N]): joint positions of size N, where N is the total number of DoFs.

        Returns:
            np.float[N,N], np.float[6+N,6+N]: inertia matrix
        """
        if isinstance(q, np.ndarray):
            q = q.ravel().tolist()
        return np.array(self.sim.calculateMassMatrix(body_id, q))

    def calculate_inverse_kinematics(self, body_id, link_id, position, orientation=None, lower_limits=None,
                                     upper_limits=None, joint_ranges=None, rest_poses=None, joint_dampings=None,
                                     solver=None, q_curr=None, max_iters=None, threshold=None):
        """
        Compute the FULL Inverse kinematics; it will return a position for all the actuated joints.

        "You can compute the joint angles that makes the end-effector reach a given target position in Cartesian world
        space. Internally, Bullet uses an improved version of Samuel Buss Inverse Kinematics library. At the moment
        only the Damped Least Squares method with or without Null Space control is exposed, with a single end-effector
        target. Optionally you can also specify the target orientation of the end effector. In addition, there is an
        option to use the null-space to specify joint limits and rest poses. This optional null-space support requires
        all 4 lists (lower_limits, upper_limits, joint_ranges, rest_poses), otherwise regular IK will be used." [1]

        Args:
            body_id (int): body unique id, as returned by `load_urdf`, etc.
            link_id (int): end effector link index.
            position (np.float[3]): target position of the end effector (its link coordinate, not center of mass
                coordinate!). By default this is in Cartesian world space, unless you provide `q_curr` joint angles.
            orientation (np.float[4]): target orientation in Cartesian world space, quaternion [x,y,w,z]. If not
                specified, pure position IK will be used.
            lower_limits (np.float[N], list of N floats): lower joint limits. Optional null-space IK.
            upper_limits (np.float[N], list of N floats): upper joint limits. Optional null-space IK.
            joint_ranges (np.float[N], list of N floats): range of value of each joint.
            rest_poses (np.float[N], list of N floats): joint rest poses. Favor an IK solution closer to a given rest
                pose.
            joint_dampings (np.float[N], list of N floats): joint damping factors. Allow to tune the IK solution using
                joint damping factors.
            solver (int): p.IK_DLS (=0) or p.IK_SDLS (=1), Damped Least Squares or Selective Damped Least Squares, as
                described in the paper by Samuel Buss "Selectively Damped Least Squares for Inverse Kinematics".
            q_curr (np.float[N]): list of joint positions. By default PyBullet uses the joint positions of the body.
                If provided, the targetPosition and targetOrientation is in local space!
            max_iters (int): maximum number of iterations. Refine the IK solution until the distance between target
                and actual end effector position is below this threshold, or the `max_iters` is reached.
            threshold (float): residual threshold. Refine the IK solution until the distance between target and actual
                end effector position is below this threshold, or the `max_iters` is reached.

        Returns:
            np.float[N]: joint positions (for each actuated joint).
        """
        kwargs = {}
        if orientation is not None:
            if isinstance(orientation, np.ndarray):
                orientation = orientation.ravel().tolist()
            kwargs['targetOrientation'] = orientation
        if lower_limits is not None and upper_limits is not None and joint_ranges is not None and \
                rest_poses is not None:
            kwargs['lowerLimits'], kwargs['upperLimits'] = lower_limits, upper_limits
            kwargs['jointRanges'], kwargs['restPoses'] = joint_ranges, rest_poses

        if q_curr is not None:
            if isinstance(q_curr, np.ndarray):
                q_curr = q_curr.ravel().tolist()
            kwargs['currentPosition'] = q_curr
        if joint_dampings is not None:
            if isinstance(joint_dampings, np.ndarray):
                joint_dampings = joint_dampings.ravel().tolist()
            kwargs['jointDamping'] = joint_dampings

        if solver is not None:
            kwargs['solver'] = solver
        if max_iters is not None:
            kwargs['maxNumIterations'] = max_iters
        if threshold is not None:
            kwargs['residualThreshold'] = threshold

        return np.array(self.sim.calculateInverseKinematics(body_id, link_id, position, **kwargs))

    def calculate_inverse_dynamics(self, body_id, q, dq, des_ddq):
        r"""
        Starting from the specified joint positions :math:`q` and velocities :math:`\dot{q}`, it computes the joint
        torques :math:`\tau` required to reach the desired joint accelerations :math:`\ddot{q}_{des}`. That is,
        :math:`\tau = ID(model, q, \dot{q}, \ddot{q}_{des})`.

        Specifically, it uses the rigid-body equation of motion in joint space given by (see [1]):

        .. math:: \tau = H(q)\ddot{q} + C(q,\dot{q})

        where :math:`\tau` is the vector of applied torques, :math:`H(q)` is the inertia matrix, and
        :math:`C(q,\dot{q}) \dot{q}` is the vector accounting for Coriolis, centrifugal forces, gravity, and any
        other forces acting on the system except the applied torques :math:`\tau`.

        Normally, a more popular form of this equation of motion (in joint space) is given by:

        .. math:: H(q) \ddot{q} + S(q,\dot{q}) \dot{q} + g(q) = \tau + J^T(q) F

        which is the same as the first one with :math:`C = S\dot{q} + g(q) - J^T(q) F`. However, this last formulation
        is useful to understand what happens when we set some variables to 0.
        Assuming that there are no forces acting on the system, and giving desired joint accelerations of 0, this
        method will return :math:`\tau = S(q,\dot{q}) \dot{q} + g(q)`. If in addition joint velocities are also 0,
        it will return :math:`\tau = g(q)` which can for instance be useful for gravity compensation.

        For forward dynamics, which computes the joint accelerations given the joint positions, velocities, and
        torques (that is, :math:`\ddot{q} = FD(model, q, \dot{q}, \tau)`, this can be computed using
        :math:`\ddot{q} = H^{-1} (\tau - C)` (see also `computeFullFD`). For more information about different
        control schemes (position, force, impedance control and others), or about the formulation of the equation
        of motion in task/operational space (instead of joint space), check the references [1-4].

        Args:
            body_id (int): body unique id.
            q (np.float[N]): joint positions
            dq (np.float[N]): joint velocities
            des_ddq (np.float[N]): desired joint accelerations

        Returns:
            np.float[N]: joint torques computed using the rigid-body equation of motion

        References:
            [1] "Rigid Body Dynamics Algorithms", Featherstone, 2008, chap1.1
            [2] "Robotics: Modelling, Planning and Control", Siciliano et al., 2010
            [3] "Springer Handbook of Robotics", Siciliano et al., 2008
            [4] Lecture on "Impedance Control" by Prof. De Luca, Universita di Roma,
                http://www.diag.uniroma1.it/~deluca/rob2_en/15_ImpedanceControl.pdf
        """
        # convert numpy arrays to lists
        if isinstance(q, np.ndarray):
            q = q.ravel().tolist()
        if isinstance(dq, np.ndarray):
            dq = dq.ravel().tolist()
        if isinstance(des_ddq, np.ndarray):
            des_ddq = des_ddq.ravel().tolist()

        # return the joint torques to be applied for the desired joint accelerations
        return np.array(self.sim.calculateInverseDynamics(body_id, q, dq, des_ddq))

    def calculate_forward_dynamics(self, body_id, q, dq, torques):
        r"""
       Given the specified joint positions :math:`q` and velocities :math:`\dot{q}`, and joint torques :math:`\tau`,
       it computes the joint accelerations :math:`\ddot{q}`. That is, :math:`\ddot{q} = FD(model, q, \dot{q}, \tau)`.

       Specifically, it uses the rigid-body equation of motion in joint space given by (see [1]):

       .. math:: \ddot{q} = H(q)^{-1} (\tau - C(q,\dot{q}))

       where :math:`\tau` is the vector of applied torques, :math:`H(q)` is the inertia matrix, and
       :math:`C(q,\dot{q}) \dot{q}` is the vector accounting for Coriolis, centrifugal forces, gravity, and any
       other forces acting on the system except the applied torques :math:`\tau`.

       Normally, a more popular form of this equation of motion (in joint space) is given by:

       .. math:: H(q) \ddot{q} + S(q,\dot{q}) \dot{q} + g(q) = \tau + J^T(q) F

       which is the same as the first one with :math:`C = S\dot{q} + g(q) - J^T(q) F`. However, this last formulation
       is useful to understand what happens when we set some variables to 0.
       Assuming that there are no forces acting on the system, and giving desired joint torques of 0, this
       method will return :math:`\ddot{q} = - H(q)^{-1} (S(q,\dot{q}) \dot{q} + g(q))`. If in addition
       the joint velocities are also 0, it will return :math:`\ddot{q} = - H(q)^{-1} g(q)` which are
       the accelerations due to gravity.

       For inverse dynamics, which computes the joint torques given the joint positions, velocities, and
       accelerations (that is, :math:`\tau = ID(model, q, \dot{q}, \ddot{q})`, this can be computed using
       :math:`\tau = H(q)\ddot{q} + C(q,\dot{q})`. For more information about different
       control schemes (position, force, impedance control and others), or about the formulation of the equation
       of motion in task/operational space (instead of joint space), check the references [1-4].

       Args:
           body_id (int): unique body id.
           q (np.float[N]): joint positions
           dq (np.float[N]): joint velocities
           torques (np.float[N]): desired joint torques

       Returns:
           float[N]: joint accelerations computed using the rigid-body equation of motion

       References:
           [1] "Rigid Body Dynamics Algorithms", Featherstone, 2008, chap1.1
           [2] "Robotics: Modelling, Planning and Control", Siciliano et al., 2010
           [3] "Springer Handbook of Robotics", Siciliano et al., 2008
           [4] Lecture on "Impedance Control" by Prof. De Luca, Universita di Roma,
               http://www.diag.uniroma1.it/~deluca/rob2_en/15_ImpedanceControl.pdf
       """
        # convert numpy arrays to lists
        if isinstance(q, np.ndarray):
            q = q.ravel().tolist()

        # compute and return joint accelerations
        torques = np.array(torques)
        Hinv = np.linalg.inv(self.calculate_mass_matrix(body_id, q))
        C = self.calculate_inverse_dynamics(body_id, q, dq, np.zeros(len(q)))
        acc = Hinv.dot(torques - C)
        return acc

    #########
    # Debug #
    #########

    def add_user_debug_line(self, from_pos, to_pos, rgb_color=None, width=None, lifetime=None, parent_object_id=None,
                            parent_link_id=None, line_id=None):
        """Add a user debug line in the simulator.

        You can add a 3d line specified by a 3d starting point (from) and end point (to), a color [red,green,blue],
        a line width and a duration in seconds.

        Args:
            from_pos (np.float[3]): starting point of the line in Cartesian world coordinates
            to_pos (np.float[3]): end point of the line in Cartesian world coordinates
            rgb_color (np.float[3]): RGB color (each channel in range [0,1])
            width (float): line width (limited by OpenGL implementation).
            lifetime (float): use 0 for permanent line, or positive time in seconds (afterwards the line with be
                removed automatically)
            parent_object_id (int): draw line in local coordinates of a parent object.
            parent_link_id (int): draw line in local coordinates of a parent link.
            line_id (int): replace an existing line item (to avoid flickering of remove/add).

        Returns:
            int: unique user debug line id.
        """
        kwargs = {}
        if rgb_color is not None:
            kwargs['lineColorRGB'] = rgb_color
        if width is not None:
            kwargs['lineWidth'] = width
        if lifetime is not None:
            kwargs['lifeTime'] = lifetime
        if parent_object_id is not None:
            kwargs['parentObjectUniqueId'] = parent_object_id
        if parent_link_id is not None:
            kwargs['parentLinkIndex'] = parent_link_id
        if line_id is not None:
            kwargs['replaceItemUniqueId'] = line_id

        return self.sim.addUserDebugLine(lineFromXYZ=from_pos, lineToXYZ=to_pos, **kwargs)

    def add_user_debug_text(self, text, position, rgb_color=None, size=None, lifetime=None, orientation=None,
                            parent_object_id=None, parent_link_id=None, text_id=None):
        """
        Add 3D text at a specific location using a color and size.

        Args:
            text (str): text.
            position (np.float[3]): 3d position of the text in Cartesian world coordinates.
            rgb_color (list/tuple of 3 floats): RGB color; each component in range [0..1]
            size (float): text size
            lifetime (float): use 0 for permanent text, or positive time in seconds (afterwards the text with be
                removed automatically)
            orientation (np.float[4]): By default, debug text will always face the camera, automatically rotation.
                By specifying a text orientation (quaternion), the orientation will be fixed in world space or local
                space (when parent is specified). Note that a different implementation/shader is used for camera
                facing text, with different appearance: camera facing text uses bitmap fonts, text with specified
                orientation uses TrueType font.
            parent_object_id (int): draw text in local coordinates of a parent object.
            parent_link_id (int): draw text in local coordinates of a parent link.
            text_id (int): replace an existing text item (to avoid flickering of remove/add).

        Returns:
            int: unique user debug text id.
        """
        kwargs = {}
        if rgb_color is not None:
            kwargs['textColorRGB'] = rgb_color
        if size is not None:
            kwargs['textSize'] = size
        if lifetime is not None:
            kwargs['lifeTime'] = lifetime
        if orientation is not None:
            kwargs['textOrientation'] = orientation
        if parent_object_id is not None:
            kwargs['parentObjectUniqueId'] = parent_object_id
        if parent_link_id is not None:
            kwargs['parentLinkIndex'] = parent_link_id
        if text_id is not None:
            kwargs['replaceItemUniqueId'] = text_id

        return self.sim.addUserDebugText(text=text, textPosition=position, **kwargs)

    def add_user_debug_parameter(self, name, min_range, max_range, start_value):
        """
        Add custom sliders to tune parameters.

        Args:
            name (str): name of the parameter.
            min_range (float): minimum value.
            max_range (float): maximum value.
            start_value (float): starting value.

        Returns:
            int: unique user debug parameter id.
        """
        return self.sim.addUserDebugParameter(paramName=name, rangeMin=min_range, rangeMax=max_range,
                                              startValue=start_value)

    def read_user_debug_parameter(self, parameter_id):
        """
        Read the value of the parameter / slider.

        Args:
            parameter_id: unique user debug parameter id.

        Returns:
            float: reading of the parameter.
        """
        return self.sim.readUserDebugParameter(parameter_id)

    def remove_user_debug_item(self, item_id):
        """
        Remove the specified user debug item (line, text, parameter) from the simulator.

        Args:
            item_id (int): unique id of the debug item to be removed (line, text etc)
        """
        self.sim.removeUserDebugItem(item_id)

    def remove_all_user_debug_items(self):
        """
        Remove all user debug items from the simulator.
        """
        self.sim.removeAllUserDebugItems()

    def set_debug_object_color(self, object_id, link_id, rgb_color=(1, 0, 0)):
        """
        Override the color of a specific object and link.

        Args:
            object_id (int): unique object id.
            link_id (int): link id.
            rgb_color (float[3]): RGB debug color.
        """
        self.sim.setDebugObjectColor(object_id, link_id, rgb_color)

    def add_user_data(self, object_id, key, value):
        """
        Add user data (at the moment text strings) attached to any link of a body. You can also override a previous
        given value. You can add multiple user data to the same body/link.

        Args:
            object_id (int): unique object/link id.
            key (str): key string.
            value (str): value string.

        Returns:
            int: user data id.
        """
        return self.sim.addUserData(object_id, key, value)

    def num_user_data(self, object_id):
        """
        Return the number of user data associated with the specified object/link id.

        Args:
            object_id (int): unique object/link id.

        Returns:
            int: the number of user data
        """
        return self.sim.getNumUserData(object_id)

    def get_user_data(self, user_data_id):
        """
        Get the specified user data value.

        Args:
            user_data_id (int): unique user data id.

        Returns:
            str: value string.
        """
        return self.sim.getUserData(user_data_id)

    def get_user_data_id(self, object_id, key):
        """
        Get the specified user data id.

        Args:
            object_id (int): unique object/link id.
            key (str): key string.

        Returns:
            int: user data id.
        """
        return self.sim.getUserDataId(object_id, key)

    def get_user_data_info(self, object_id, index):
        """
        Get the user data info associated with the given object and index.

        Args:
            object_id (int): unique object id.
            index (int): index (should be between [0, self.num_user_data(object_id)]).

        Returns:
            int: user data id.
            str: key.
            int: body id.
            int: link index
            int: visual shape index.
        """
        return self.sim.getUserDataInfo(object_id, index)

    def remove_user_data(self, user_data_id):
        """
        Remove the specified user data.

        Args:
            user_data_id (int): user data id.
        """
        self.sim.removeUserData(user_data_id)

    def sync_user_data(self):
        """
        Synchronize the user data.
        """
        self.sim.syncUserData()

    def configure_debug_visualizer(self, flag, enable):
        """Configure the debug visualizer camera.

        Configure some settings of the built-in OpenGL visualizer, such as enabling or disabling wireframe,
        shadows and GUI rendering.

        Args:
            flag (int): The feature to enable or disable, such as
                        COV_ENABLE_WIREFRAME (=3): show/hide the collision wireframe
                        COV_ENABLE_SHADOWS (=2): show/hide shadows
                        COV_ENABLE_GUI (=1): enable/disable the GUI
                        COV_ENABLE_VR_PICKING (=5): enable/disable VR picking
                        COV_ENABLE_VR_TELEPORTING (=4): enable/disable VR teleporting
                        COV_ENABLE_RENDERING (=7): enable/disable rendering
                        COV_ENABLE_TINY_RENDERER (=12): enable/disable tiny renderer
                        COV_ENABLE_VR_RENDER_CONTROLLERS (=6): render VR controllers
                        COV_ENABLE_KEYBOARD_SHORTCUTS (=9): enable/disable keyboard shortcuts
                        COV_ENABLE_MOUSE_PICKING (=10): enable/disable mouse picking
                        COV_ENABLE_Y_AXIS_UP (Z is default world up axis) (=11): enable/disable Y axis up
                        COV_ENABLE_RGB_BUFFER_PREVIEW (=13): enable/disable RGB buffer preview
                        COV_ENABLE_DEPTH_BUFFER_PREVIEW (=14): enable/disable Depth buffer preview
                        COV_ENABLE_SEGMENTATION_MARK_PREVIEW (=15): enable/disable segmentation mark preview
            enable (bool): False (disable) or True (enable)
        """
        self.sim.configureDebugVisualizer(flag, int(enable))

    def get_debug_visualizer(self):
        """Get information about the debug visualizer camera.

        Returns:
            float: width of the visualizer camera
            float: height of the visualizer camera
            np.float[4,4]: view matrix [4,4]
            np.float[4,4]: perspective projection matrix [4,4]
            np.float[3]: camera up vector expressed in the Cartesian world space
            np.float[3]: forward axis of the camera expressed in the Cartesian world space
            np.float[3]: This is a horizontal vector that can be used to generate rays (for mouse picking or creating
                a simple ray tracer for example)
            np.float[3]: This is a vertical vector that can be used to generate rays (for mouse picking or creating a
                simple ray tracer for example)
            float: yaw angle (in radians) of the camera, in Cartesian local space coordinates
            float: pitch angle (in radians) of the camera, in Cartesian local space coordinates
            float: distance between the camera and the camera target
            np.float[3]: target of the camera, in Cartesian world space coordinates
        """
        width, height, view, proj, up_vec, forward_vec,\
            horizontal, vertical, yaw, pitch, dist, target = self.sim.getDebugVisualizerCamera()

        # convert data to the correct data type
        view = np.array(view).reshape(4, 4).T
        proj = np.array(proj).reshape(4, 4).T
        up_vec = np.array(up_vec)
        forward_vec = np.array(forward_vec)
        horizontal = np.array(horizontal)
        vertical = np.array(vertical)
        target = np.array(target)
        yaw = np.deg2rad(yaw)
        pitch = np.deg2rad(pitch)

        # return the data
        return width, height, view, proj, up_vec, forward_vec, horizontal, vertical, yaw, pitch, dist, target

    def reset_debug_visualizer(self, distance, yaw, pitch, target_position):
        """Reset the debug visualizer camera.

        Reset the 3D OpenGL debug visualizer camera distance (between eye and camera target position), camera yaw and
        pitch and camera target position

        Args:
            distance (float): distance from eye to camera target position
            yaw (float): camera yaw angle (in radians) left/right
            pitch (float): camera pitch angle (in radians) up/down
            target_position (np.float[3]): target focus point of the camera
        """
        self.sim.resetDebugVisualizerCamera(cameraDistance=distance, cameraYaw=np.rad2deg(yaw),
                                            cameraPitch=np.rad2deg(pitch), cameraTargetPosition=target_position)

    ############################
    # Events (mouse, keyboard) #
    ############################

    def get_keyboard_events(self):
        """Get the key events.

        Returns:
            dict: {keyId: keyState}
                * `keyID` is an integer (ascii code) representing the key. Some special keys like shift, arrows,
                and others are are defined in pybullet such as `B3G_SHIFT`, `B3G_LEFT_ARROW`, `B3G_UP_ARROW`,...
                * `keyState` is an integer. 3 if the button has been pressed, 1 if the key is down, 2 if the key has
                been triggered.
        """
        return self.sim.getKeyboardEvents()

    def get_mouse_events(self):
        """Get the mouse events.

        Returns:
            list of mouse events:
                eventType (int): 1 if the mouse is moving, 2 if a button has been pressed or released
                mousePosX (float): x-coordinates of the mouse pointer
                mousePosY (float): y-coordinates of the mouse pointer
                buttonIdx (int): button index for left/middle/right mouse button. It is -1 if nothing,
                                 0 if left button, 1 if scroll wheel (pressed), 2 if right button
                buttonState (int): 0 if nothing, 3 if the button has been pressed, 4 is the button has been released,
                                   1 if the key is down (never observed), 2 if the key has been triggered (never
                                   observed).
        """
        return self.sim.getMouseEvents()

    def get_mouse_and_keyboard_events(self):
        """Get the mouse and key events.

        Returns:
            list: list of mouse events
            dict: dictionary of key events
        """
        return self.sim.getMouseEvents(), self.sim.getKeyboardEvents()


# Tests
if __name__ == "__main__":
    pass
    # import inspect
    # import pybullet as p
    #
    # f = p.createCollisionShape
    # print(f)
    # print(dir(f))
    # specs = inspect.getargspec(f)
    # print(zip(specs.args[-len(specs.defaults):], specs.defaults))
    # print('')
    #
    # exit()
    # sim = Bullet()
    # s = sim.sim._client
    # print('')
    # # print(sim.get_physics_properties())
    # f = s.createCollisionShape
    # print(f)
    # print(f.keywords)
    # print(dir(f))
    # specs = inspect.getargspec(f)
    # print(zip(specs.args[-len(specs.defaults):], specs.defaults))
    # print('')