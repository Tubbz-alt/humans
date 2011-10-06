#include <ros/ros.h>
#include <interactive_markers/interactive_marker_server.h>
#include <tf/transform_broadcaster.h>
#include <geometry_msgs/Pose.h>
#include <hrl_phri_2011/EllipsoidParams.h>
#include <hrl_phri_2011/utils.h>

class InteractiveEllipse 
{
private:
    interactive_markers::InteractiveMarkerServer im_server_;
    tf::TransformBroadcaster tf_broad_;
    ros::Publisher params_pub;
    std::string parent_frame_, child_frame_;
    double rate_;
    ros::Timer tf_timer_;
    geometry_msgs::Pose marker_pose_;
    double z_axis_, y_axis_, old_z_axis_, old_y_axis_;
    geometry_msgs::Transform old_marker_tf_;
    geometry_msgs::TransformStamped tf_msg_;
public:
    InteractiveEllipse(const std::string& parent_frame, const std::string& child_frame, double rate = 100);
    void processTFControl(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback);
    void processEllipseControlY(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback);
    void processEllipseControlZ(const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback);
    void addTFMarker();
    void addEllipseMarker();
    void publishTF(const ros::TimerEvent& event);
    void loadEllipsoidParams(const hrl_phri_2011::EllipsoidParams& e_params);
};

InteractiveEllipse::InteractiveEllipse(const std::string& parent_frame, 
                                       const std::string& child_frame, double rate) :
    im_server_("transform_marker"),
    parent_frame_(parent_frame),
    child_frame_(child_frame),
    rate_(rate), z_axis_(0.0), y_axis_(0.0) 
    {
    ros::NodeHandle nh;
    marker_pose_.orientation.w = 1;
    params_pub = nh.advertise<hrl_phri_2011::EllipsoidParams>("/ellipsoid_params", 1);
}

void InteractiveEllipse::addTFMarker() 
{
    ros::NodeHandle nh;
    visualization_msgs::InteractiveMarker tf_marker;
    tf_marker.header.frame_id = parent_frame_;
    tf_marker.name = "tf_marker";
    tf_marker.scale = 0.2;
    visualization_msgs::InteractiveMarkerControl tf_control;
    tf_control.orientation_mode = visualization_msgs::InteractiveMarkerControl::INHERIT;
    // x
    tf_control.orientation.x = 1; tf_control.orientation.y = 0;
    tf_control.orientation.z = 0; tf_control.orientation.w = 1;
    tf_control.name = "rotate_x";
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
    tf_marker.controls.push_back(tf_control);
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
    tf_marker.controls.push_back(tf_control);
    // y
    tf_control.orientation.x = 0; tf_control.orientation.y = 1;
    tf_control.orientation.z = 0; tf_control.orientation.w = 1;
    tf_control.name = "rotate_y";
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
    tf_marker.controls.push_back(tf_control);
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
    tf_marker.controls.push_back(tf_control);
    // z
    tf_control.orientation.x = 0; tf_control.orientation.y = 0;
    tf_control.orientation.z = 1; tf_control.orientation.w = 1;
    tf_control.name = "rotate_z";
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::ROTATE_AXIS;
    tf_marker.controls.push_back(tf_control);
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
    tf_marker.controls.push_back(tf_control);
    im_server_.insert(tf_marker, boost::bind(&InteractiveEllipse::processTFControl, this, _1));
    im_server_.applyChanges();
    tf_timer_ = nh.createTimer(ros::Duration(1.0 / rate_), &InteractiveEllipse::publishTF, this);
}

void InteractiveEllipse::processTFControl(
        const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback) 
        {
    ROS_INFO_STREAM(tf_msg_.transform.translation.x << " " << 
                    tf_msg_.transform.translation.y << " " <<
                    tf_msg_.transform.translation.z << " " <<
                    tf_msg_.transform.rotation.x << " " <<
                    tf_msg_.transform.rotation.y << " " <<
                    tf_msg_.transform.rotation.z << " " <<
                    tf_msg_.transform.rotation.w);
    marker_pose_ = feedback->pose;
}

void InteractiveEllipse::addEllipseMarker() 
{
    visualization_msgs::InteractiveMarker tf_marker;
    tf_marker.header.frame_id = child_frame_;
    tf_marker.name = "ellipse_marker_y";
    tf_marker.scale = 0.4;
    visualization_msgs::InteractiveMarkerControl tf_control;
    tf_control.orientation_mode = visualization_msgs::InteractiveMarkerControl::INHERIT;
    // y
    tf_control.orientation.x = 0; tf_control.orientation.y = 1;
    tf_control.orientation.z = 0; tf_control.orientation.w = 1;
    tf_control.name = "shift_y";
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
    tf_marker.controls.push_back(tf_control);
    im_server_.insert(tf_marker, boost::bind(&InteractiveEllipse::processEllipseControlY, this, _1));
    tf_marker.controls.clear();
    // z
    tf_marker.name = "ellipse_marker_z";
    tf_control.orientation.x = 0; tf_control.orientation.y = 0;
    tf_control.orientation.z = 1; tf_control.orientation.w = 1;
    tf_control.name = "shift_z";
    tf_control.interaction_mode = visualization_msgs::InteractiveMarkerControl::MOVE_AXIS;
    tf_marker.controls.push_back(tf_control);
    im_server_.insert(tf_marker, boost::bind(&InteractiveEllipse::processEllipseControlZ, this, _1));
    im_server_.applyChanges();
}

void InteractiveEllipse::processEllipseControlY(
        const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback) 
        {
    z_axis_ = feedback->pose.position.z;
}

void InteractiveEllipse::processEllipseControlZ(
        const visualization_msgs::InteractiveMarkerFeedbackConstPtr& feedback) 
        {
    y_axis_ = feedback->pose.position.y;
}

void InteractiveEllipse::publishTF(const ros::TimerEvent& event) 
{
    tf_msg_.header.stamp = ros::Time::now();
    tf_msg_.header.frame_id = parent_frame_;
    tf_msg_.child_frame_id = child_frame_;
    tf_msg_.transform.translation.x = marker_pose_.position.x;
    tf_msg_.transform.translation.y = marker_pose_.position.y;
    tf_msg_.transform.translation.z = marker_pose_.position.z;
    tf_msg_.transform.rotation.x = marker_pose_.orientation.x;
    tf_msg_.transform.rotation.y = marker_pose_.orientation.y;
    tf_msg_.transform.rotation.z = marker_pose_.orientation.z;
    tf_msg_.transform.rotation.w = marker_pose_.orientation.w;
    tf::Transform cur_tf, old_tf;
    tf::transformMsgToTF(tf_msg_.transform, cur_tf);
    tf::transformMsgToTF(old_marker_tf_, old_tf);
    Eigen::Affine3d cur_tf_eig, old_tf_eig;
    tf::TransformTFToEigen(cur_tf, cur_tf_eig);
    tf::TransformTFToEigen(old_tf, old_tf_eig);
    cur_tf_eig = cur_tf_eig;
    tf::TransformEigenToTF(cur_tf_eig, cur_tf);
    tf::transformTFToMsg(cur_tf, tf_msg_.transform);
    tf_broad_.sendTransform(tf_msg_);
    hrl_phri_2011::EllipsoidParams e_params;
    e_params.e_frame = tf_msg_;
    e_params.height = y_axis_ + old_y_axis_;
    e_params.E = z_axis_ + old_z_axis_;
    params_pub.publish(e_params);
}

void InteractiveEllipse::loadEllipsoidParams(const hrl_phri_2011::EllipsoidParams& e_params) 
{
    old_marker_tf_ = e_params.e_frame.transform;
    old_y_axis_ = e_params.height;
    old_z_axis_ = e_params.E;
}

int main(int argc, char **argv)
{
    if(argc != 3 && argc != 4 && argc != 5) {
        printf("Usage: interative_ellipse parent_frame child_frame [rate] [inital_params]\n");
        return 1;
    }
    ros::init(argc, argv, "interative_ellipse");
    if(argc >= 4) {
        InteractiveEllipse itf(argv[1], argv[2], atof(argv[3]));
        if(argc == 5) {
            // load params
            std::vector<hrl_phri_2011::EllipsoidParams::Ptr> params;
            readBagTopic<hrl_phri_2011::EllipsoidParams>(argv[4], params, "/ellipsoid_params");
            itf.loadEllipsoidParams(*params[0]);
        }
        itf.addTFMarker();
        itf.addEllipseMarker();
        ros::spin();
    } else {
        InteractiveEllipse itf(argv[1], argv[2]);
        itf.addTFMarker();
        itf.addEllipseMarker();
        ros::spin();
    }

    return 0;
}