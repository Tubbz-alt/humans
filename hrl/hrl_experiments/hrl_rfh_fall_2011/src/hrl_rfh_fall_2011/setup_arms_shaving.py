#! /usr/bin/python

import sys
import numpy as np

import roslib
roslib.load_manifest('hrl_pr2_arms')
roslib.load_manifest('hrl_rfh_summer_2011')
roslib.load_manifest('hrl_rfh_fall_2011')
import rospy

import smach
import actionlib
from smach_ros import SimpleActionState, ServiceState, IntrospectionServer
from std_srvs.srv import Empty, EmptyResponse

from hrl_rfh_fall_2011.sm_register_head_ellipse import SMEllipsoidRegistration
from hrl_trajectory_playback.srv import TrajPlaybackSrv, TrajPlaybackSrvRequest
from pr2_controllers_msgs.msg import SingleJointPositionAction, SingleJointPositionGoal
from hrl_rfh_fall_2011.sm_topic_monitor import TopicMonitor
from hrl_pr2_arms.pr2_arm import create_pr2_arm, PR2ArmJTransposeTask
from hrl_pr2_arms.pr2_controller_switcher import ControllerSwitcher

class SetupArmsShaving():
        def __init__(self):
            self.ctrl_switcher = ControllerSwitcher()
            self.untuck = rospy.ServiceProxy('traj_playback/untuck_l_arm', TrajPlaybackSrv)
            self.torso_sac = actionlib.SimpleActionClient('torso_controller/position_joint_action',
                                                          SingleJointPositionAction)
            self.torso_sac.wait_for_server()
            rospy.loginfo("[setup_arms_shaving] SetupArmsShaving ready.")

        def adjust_torso(self):
            # move torso up
            tgoal = SingleJointPositionGoal()
            tgoal.position = 0.300  # all the way up is 0.300
            tgoal.min_duration = rospy.Duration( 2.0 )
            tgoal.max_velocity = 1.0
            self.torso_sac.send_goal_and_wait(tgoal)

        def run(self, req):
            self.adjust_torso()
            self.untuck(False)
            self.setup_task_controller()
            return EmptyResponse()

        def setup_task_controller(self):
            self.ctrl_switcher.carefree_switch('l', '%s_cart_jt_task', 
                                               "$(find hrl_rfh_fall_2011)/params/l_jt_task_shaver45.yaml") 
            rospy.sleep(0.3)
            self.arm = create_pr2_arm('l', PR2ArmJTransposeTask, 
                                      controller_name='%s_cart_jt_task', 
                                      end_link="%s_gripper_shaver45_frame")
            setup_angles = [0, 0, np.pi/2, -np.pi/2, -np.pi, -np.pi/2, -np.pi/2]
            self.arm.set_posture(setup_angles)
            self.arm.set_gains([200, 800, 800, 80, 80, 80], [15, 15, 15, 1.2, 1.2, 1.2])
            rospy.sleep(0.3)


def main():
    rospy.init_node("setup_arms_shaving")
    assert(len(sys.argv) > 1)
    sas = SetupArmsShaving()
    if sys.argv[1] == "-s":
        rospy.Service("/setup_arms_shaving", Empty, sas.run)
        rospy.spin()
    else:
        sas.run(None)
        
if __name__ == "__main__":
    main()
