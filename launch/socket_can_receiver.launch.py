# Copyright 2021 the Autoware Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Co-developed by Tier IV, Inc. and Apex.AI, Inc.


from email.policy import default
from pydoc_data import topics
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, LogInfo, 
                            RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch.logging import LaunchConfig
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
import logging

"""
working version for set log level
however console message does not changed
"""
logger = LaunchConfig()
logger.level = logging.INFO

def generate_launch_description():
    socket_can_receiver_node = LifecycleNode(
        package='ros2_socketcan',
        executable='socket_can_receiver_node_exe',
        name=LaunchConfiguration('node_name'),
        namespace=TextSubstitution(text=''),
        parameters=[{
            'interface': LaunchConfiguration('interface'),
            'interval_sec': LaunchConfiguration('interval_sec'),
            'use_bus_time': LaunchConfiguration('use_bus_time'),
            'topic_name' : LaunchConfiguration('topic_name'),
        }],
        arguments=[{        # no effect version
            #'--ros-args',
            #'--log-level'
            #'__log_level:=WARN'        # no effect
            #'WARN' # no effect
        }],
        output='screen')


    socket_can_receiver_configure_event_handler = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=socket_can_receiver_node,
            on_start=[
                LogInfo(msg='Launch file log test test!'),
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(socket_can_receiver_node),
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_configure')),
    )

    socket_can_receiver_activate_event_handler = RegisterEventHandler(
        event_handler=OnStateTransition(
            target_lifecycle_node=socket_can_receiver_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(socket_can_receiver_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_activate')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('interface', default_value='can0'),
        DeclareLaunchArgument('interval_sec', default_value='0.01'),
        DeclareLaunchArgument('use_bus_time', default_value='false'),
        DeclareLaunchArgument('auto_configure', default_value='true'),
        DeclareLaunchArgument('auto_activate', default_value='true'),
        DeclareLaunchArgument(name='log-level', default_value=['WARN']),
        DeclareLaunchArgument('node_name', default_value='socket_can_receiver'),  # added by csj on 06-15
        DeclareLaunchArgument('topic_name', default_value='testtest'),
        socket_can_receiver_node,
        socket_can_receiver_configure_event_handler,
        socket_can_receiver_activate_event_handler,
    ])
