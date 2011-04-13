
#
# subscribe to thw joint angles and raw forces topics,  and provide FK
# etc.
#
#

import math
import numpy as np
import copy
import sys, time, os
from threading import RLock

import roslib; roslib.load_manifest('epc_core')
import rospy
from hrl_lib.msg import FloatArray
from roslib.msg import Header
from std_msgs.msg import Bool
from std_msgs.msg import Empty

class MekaArmClient():
    ##
    # @param arms: object of the ArmKinematics class.
    def __init__(self, arms):
        self.cb_lock = RLock()
        self.r_arm_jep = None
        self.l_arm_jep = None
        self.r_arm_q = None
        self.l_arm_q = None
        self.r_arm_force = None
        self.r_arm_raw_force = None
        self.l_arm_force = None
        self.l_arm_raw_force = None
        self.pwr_state = False

        self.left_arm_ft = {'force': np.matrix(np.zeros((3,1),dtype='float32')),
                             'torque': np.matrix(np.zeros((3,1),dtype='float32'))}
        self.right_arm_ft = {'force': np.matrix(np.zeros((3,1),dtype='float32')),
                            'torque': np.matrix(np.zeros((3,1),dtype='float32'))}
        self.fts_bias = {'left_arm': self.left_arm_ft, 'right_arm': self.right_arm_ft}
        self.arms = arms

        self.l_jep_cmd_pub = rospy.Publisher('/l_arm/command/jep', FloatArray)
        self.r_jep_cmd_pub = rospy.Publisher('/r_arm/command/jep', FloatArray)
        self.stop_pub = rospy.Publisher('/arms/stop', Empty)
        self.motors_off_pub = rospy.Publisher('/arms/command/motors_off', Empty)

        rospy.Subscriber('/r_arm/jep', FloatArray, self.r_arm_jep_cb)
        rospy.Subscriber('/l_arm/jep', FloatArray, self.l_arm_jep_cb)
        rospy.Subscriber('/r_arm/q', FloatArray, self.r_arm_q_cb)
        rospy.Subscriber('/l_arm/q', FloatArray, self.l_arm_q_cb)
        rospy.Subscriber('/r_arm/force', FloatArray,
                         self.r_arm_force_cb)
        rospy.Subscriber('/l_arm/force', FloatArray,
                         self.l_arm_force_cb)
        rospy.Subscriber('/r_arm/force_raw', FloatArray,
                         self.r_arm_raw_force_cb)
        rospy.Subscriber('/l_arm/force_raw', FloatArray,
                         self.l_arm_raw_force_cb)
        rospy.Subscriber('/arms/pwr_state', Bool, self.pwr_state_cb)

        try:
            rospy.init_node('cody_arm_client', anonymous=True)
        except rospy.ROSException:
            pass

    #---------- ROS callbacks -----------------
    def pwr_state_cb(self, msg):
        self.cb_lock.acquire()
        self.pwr_state = msg.data
        self.cb_lock.release()

    def r_arm_jep_cb(self, msg):
        self.cb_lock.acquire()
        self.r_arm_jep = list(msg.data)
        self.cb_lock.release()

    def l_arm_jep_cb(self, msg):
        self.cb_lock.acquire()
        self.l_arm_jep = list(msg.data)
        self.cb_lock.release()

    def r_arm_q_cb(self, msg):
        self.cb_lock.acquire()
        self.r_arm_q = list(msg.data)
        self.cb_lock.release()

    def l_arm_q_cb(self, msg):
        self.cb_lock.acquire()
        self.l_arm_q = list(msg.data)
        self.cb_lock.release()

    def r_arm_force_cb(self, msg):
        self.cb_lock.acquire()
        self.r_arm_force = msg.data
        self.cb_lock.release()

    def l_arm_force_cb(self, msg):
        self.cb_lock.acquire()
        self.l_arm_force = msg.data
        self.cb_lock.release()

    def r_arm_raw_force_cb(self, msg):
        self.cb_lock.acquire()
        self.r_arm_raw_force = msg.data
        self.cb_lock.release()

    def l_arm_raw_force_cb(self, msg):
        self.cb_lock.acquire()
        self.l_arm_raw_force = msg.data
        self.cb_lock.release()

    #--------- functions to use -----------------

    ##
    # @return list of 7 joint angles.
    def get_joint_angles(self, arm):
        self.cb_lock.acquire()
        if arm == 'right_arm':
            q = copy.copy(self.r_arm_q)
        elif arm == 'left_arm':
            q = copy.copy(self.l_arm_q)
        else:
            self.cb_lock.release()
            raise RuntimeError('Undefined arm: %s'%(arm))
        self.cb_lock.release()
        return q

    def get_wrist_force(self, arm, bias=True, base_frame=False,
                        filtered = True):
        self.cb_lock.acquire()
        if arm == 'right_arm':
            if filtered:
                f = copy.copy(self.r_arm_force)
            else:
                f = copy.copy(self.r_arm_raw_force)
        elif arm == 'left_arm':
            if filtered:
                f = copy.copy(self.l_arm_force)
            else:
                f = copy.copy(self.l_arm_raw_force)
        else:
            self.cb_lock.release()
            raise RuntimeError('Undefined arm: %s'%(arm))
        self.cb_lock.release()

        f_mat = np.matrix(f).T
        if bias:
            f_mat = f_mat - self.fts_bias[arm]['force']
        
        if base_frame:
            q = self.get_joint_angles(arm)
            rot = self.arms.FK_rot(arm, q)
            f_mat = rot.T*f_mat
        return f_mat
            
    def bias_wrist_ft(self, arm):
        f_list = []
        t_list = []
        print 'Starting biasing...'
        for i in range(20):
            f_list.append(self.get_wrist_force(arm, bias=False))
            rospy.sleep(0.02)

        f_b = np.mean(np.column_stack(f_list), 1)
        # torque is unimplemented.
        t_b = self.get_wrist_torque(arm, bias=False)
        self.fts_bias[arm]['force'] = f_b
        self.fts_bias[arm]['torque'] = t_b
        print 'self.fts_bias[arm][\'force\']', self.fts_bias[arm]['force']
        print 'arm:', arm
        print '...done'

    def get_jep(self, arm):
        self.cb_lock.acquire()
        if arm == 'right_arm':
            jep = copy.copy(self.r_arm_jep)
        elif arm == 'left_arm':
            jep = copy.copy(self.l_arm_jep)
        else:
            self.cb_lock.release()
            raise RuntimeError('Undefined arm: %s'%(arm))
        self.cb_lock.release()
        return jep

    ##
    # @param q - list of 7 joint angles in RADIANS. according to meka's coordinate frames.
    def set_jep(self, arm, q):
        if arm == 'right_arm': 
            pub = self.r_jep_cmd_pub
        elif arm == 'left_arm':
            pub = self.l_jep_cmd_pub
        else:
            raise RuntimeError('Undefined arm: %s'%(arm))
        time_stamp = rospy.Time.now()
        h = Header()
        h.stamp = time_stamp
        pub.publish(FloatArray(h, q))

    ##
    #Function that commands the arm(s) to incrementally move to a jep
    #@param speed the max angular speed (in radians per second)
    #@return 'reach'
    def go_jep(self, arm, q, stopping_function=None, speed=math.radians(30)):
        if speed>math.radians(90.):
            speed = math.radians(90.)

        qs_list,qe_list,ns_list,qstep_list = [],[],[],[]
        done_list = []
        time_between_cmds = 0.025
        
        #qs = np.matrix(self.get_joint_angles(arm))
        qs = np.matrix(self.get_jep(arm))
        qe = np.matrix(q)
        max_change = np.max(np.abs(qe-qs))

        total_time = max_change/speed
        n_steps = int(total_time/time_between_cmds+0.5)

        qstep = (qe-qs)/n_steps

        if stopping_function != None:
            done = stopping_function()
        else:
            done = False

        step_number = 0
        t0 = rospy.Time.now().to_time()
        t_end = t0
        while done==False:
            t_end += time_between_cmds
            t1 = rospy.Time.now().to_time()

            if stopping_function != None:
                done = stopping_function()
            if step_number < n_steps and done == False:
                q = (qs + step_number*qstep).A1.tolist()
                self.set_jep(arm, q)
            else:
                done = True

            while t1 < t_end:
                if stopping_function != None:
                    done = done or stopping_function()
                rospy.sleep(time_between_cmds/5)
                t1 = rospy.Time.now().to_time()
            step_number += 1

        rospy.sleep(time_between_cmds)
        return 'reach'

    # Expect this to crash the program because sending a stop crashes
    # the meka server
    def stop(self):
        self.stop_pub.publish()

    def is_motor_power_on(self):
        return self.pwr_state

    def go_cep(self, arm, p, rot, speed = 0.10,
                     stopping_function = None, q_guess = None):
        q = self.arms.IK(arm, p, rot, q_guess)
        if q == None:
            print 'IK soln NOT found.'
            print 'trying to reach p= ', p
            return 'fail'
        else:
            q_start = np.matrix(self.get_joint_angles(arm))
            p_start = self.arms.FK(arm, q_start.A1.tolist())
            q_end = np.matrix(q)
    
            dist = np.linalg.norm(p-p_start)
            total_time = dist/speed
            max_change = np.max(np.abs(q_end-q_start))
            ang_speed = max_change/total_time
            return self.go_jep(arm, q, stopping_function, speed=ang_speed)

    ##
    # linearly interpolates the commanded cep.
    # @param arm - 'left_arm' or 'right_arm'
    # @param p - 3x1 np matrix
    # @param rot - rotation matrix
    # @param speed - linear speed (m/s)
    # @param stopping_function - returns True or False
    # @return string (reason for stopping)
    def go_cep_interpolate(self, arm, p, rot=None, speed=0.10,
                                 stopping_function=None):
        rot = None # Rotational interpolation not implemented right now.
        time_between_cmds = 0.025

        q_guess = self.get_jep(arm)
        cep = self.arms.FK(arm, q_guess)
        if rot == None:
            rot = self.arms.FK_rot(arm, q_guess)

        vec = p-cep
        dist = np.linalg.norm(vec)
        total_time = dist/speed
        n_steps = int(total_time/time_between_cmds + 0.5)
        vec = vec/dist
        vec = vec * speed * time_between_cmds
        
        pt = cep
        all_done = False
        i = 0 
        t0 = rospy.Time.now().to_time()
        t_end = t0
        while all_done==False:
            t_end += time_between_cmds
            t1 = rospy.Time.now().to_time()
            pt = pt + vec
            q = self.arms.IK(arm, pt, rot, q_guess)

            if q == None:
                all_done = True
                stop = 'IK fail'
                continue
            self.set_jep(arm, q)
            q_guess = q
            while t1<t_end:
                if stopping_function != None:
                    all_done = stopping_function()
                if all_done:
                    stop = 'Stopping Condition'
                    break
                rospy.sleep(time_between_cmds/5)
                t1 = rospy.Time.now().to_time()

            i+=1
            if i == n_steps:
                all_done = True
                stop = ''
        return stop

    ##  
    # @param vec - displacement vector (base frame)
    # @param q_guess - previous JEP?
    # @return string
    def move_till_hit(self, arm, vec=np.matrix([0.3,0.,0.]).T, force_threshold=3.0,
                      speed=0.1, bias_FT=True):
        unit_vec =  vec/np.linalg.norm(vec)
        def stopping_function():
            force = self.get_wrist_force(arm, base_frame = True)
            force_projection = force.T*unit_vec *-1 # projection in direction opposite to motion.
            if force_projection>force_threshold:
                return True
            elif np.linalg.norm(force)>45.:
                return True
            else:
                return False

        jep = self.get_jep(arm)
        cep, rot = self.arms.FK_all(arm, jep)

        if bias_FT:
            self.bias_wrist_ft(arm)
        time.sleep(0.5)

        p = cep + vec
        return self.go_cep_interpolate(arm, p, rot, speed,
                                       stopping_function)

    def motors_off(self):
        self.motors_off_pub.publish()

#    def step(self):
#        rospy.sleep(0.01)

    #-------- unimplemented functions -----------------

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    def get_joint_velocities(self, arm):
        pass

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    def get_joint_accelerations(self, arm):
        pass

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    def get_joint_torques(self, arm):
        pass

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    def get_wrist_torque(self, arm, bias=True):
        pass

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    def power_on(self):
        pass

    # leaving this unimplemented for now. Advait Nov 14, 2010.
    # something to change and get arm_settings.


if __name__ == '__main__':
    import arms as ar
    import m3.toolbox as m3t
    import hrl_lib.transforms as tr

    r_arm = 'right_arm'
    l_arm = 'left_arm'

    arms = ar.M3HrlRobot()
    ac = MekaArmClient(arms)


    # print FT sensor readings.
    if False:
        ac.bias_wrist_ft(r_arm)
        while not rospy.is_shutdown():
            f = ac.get_wrist_force(r_arm)
            print 'f:', f.A1
            rospy.sleep(0.05)


    # move the arms.
    if True:
        print 'hit a key to move the arms.'
        k=m3t.get_keystroke()

        rot_mat = tr.Ry(math.radians(-90)) #* tr.Rx(math.radians(45))
        p = np.matrix([0.3, -0.24, -0.3]).T
    #    q = arms.IK(l_arm, p, rot_mat)
    #    ac.go_jep(l_arm, q)
    #    ac.go_cep(l_arm, p, rot_mat)
        ac.go_cep(r_arm, p, rot_mat)

    #    jep = ac.get_jep(r_arm)
    #    ac.go_jep(r_arm, jep)

        rospy.sleep(0.5)
        #ac.move_till_hit(l_arm)
        #ac.motors_off()
    #    ac.stop()


