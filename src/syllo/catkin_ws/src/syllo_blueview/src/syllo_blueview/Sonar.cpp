#include <stdio.h>
#include <syllo_blueview/Sonar.h>

#if ENABLE_SONAR == 1
#include <bvt_sdk.h>
#endif

using std::cout;
using std::endl;

namespace sonar {
     Sonar::Sonar()
     {
	  mCurPing = 0;
     }

     Sonar::Sonar(int mode, std::string sonarFile, int minRange, int maxRange)
     {
	  fn = sonarFile;
	  mMode = mode;
	  mMinRange = minRange;
	  mMaxRange = maxRange; 
     }

     Sonar::~Sonar()
     {
#if ENABLE_SONAR == 1
          // Causing seg faults after just init, but no grab
	  //BVTColorImage_Destroy(cimg);
	  //BVTMagImage_Destroy(img);
	  //BVTColorMapper_Destroy(mapper);
	  //BVTSonar_Destroy(son);
#endif
     }
     
     int Sonar::net_init(const std::string &ip)
     {
          //Create the discovery agent
          BVTSonarDiscoveryAgent agent = BVTSonarDiscoveryAgent_Create();
          if( agent == NULL )
          {
               printf("BVTSonarDiscoverAgent_Create: failed\n");
               return 1;
          }
          
          // Kick off the discovery process
          int ret;
          ret = BVTSonarDiscoveryAgent_Start(agent);
          
          //Let the discovery process run for a short while (5 secs)
          cout << "Searching for sonar" << endl;
          sleep(2);
          
          // See what we found
          int numSonars = 0;
          numSonars = BVTSonarDiscoveryAgent_GetSonarCount(agent);
          
          char SonarIPAddress[20];
          
          for(int i = 0; i < numSonars; i++)
          {
               ret = BVTSonarDiscoveryAgent_GetSonarInfo(agent, i, &SonarIPAddress[0], 20);
               printf("Found Sonar: %d, IP address: %s\n", i, SonarIPAddress);
          }
          
          if(numSonars == 0)
          {
               printf("No Sonars Found\n");
               return(1);
          }
          
          mCurPing = 0;

          son = BVTSonar_Create();
	  if (son == NULL ) {
	       printf("BVTSonar_Create: failed\n");
	       //return 1;
	  }

          // Open the sonar
          ret = BVTSonar_Open(son, "NET", "192.168.1.45");
          if( ret != 0 )
          {
               printf("BVTSonar_Open: ret=%d\n", ret);
               //return 1;
          }

	  //// Open the sonar
	  //ret = BVTSonar_Open(son, "FILE", fn.c_str());
	  //if (ret != 0 ) {
	  //     printf("BVTSonar_Open: ret=%d\n", ret);
	  //     //return 1;
	  //}

	  // Make sure we have the right number of heads
	  heads = -1;
	  heads = BVTSonar_GetHeadCount(son);
	  printf("BVTSonar_GetHeadCount: %d\n", heads);
	  
	  // Get the first head
	  head = NULL;
	  ret = BVTSonar_GetHead(son, 0, &head);
	  if (ret != 0 ) {

               ret = BVTSonar_GetHead(son, 1, &head);
               if (ret != 0) {
                    printf( "BVTSonar_GetHead: ret=%d\n", ret) ;
                    //return 1;
               }
               //return 1;
	  }
	
	  //// Check the ping count
	  //pings = -1;
	  //pings = BVTHead_GetPingCount(head);
	  //printf("BVTHead_GetPingCount: %d\n", pings);

	  // Set the range window to be 10m to 40m
	  BVTHead_SetRange(head, mMinRange, mMaxRange);

	  // Build a color mapper
	  mapper = BVTColorMapper_Create();
	  if (mapper == NULL) {
	       printf("BVTColorMapper_Create: failed\n");
	       //return 1;
	  }

	  // Load the bone colormap
	  ret = BVTColorMapper_Load(mapper, "../sonar-processing/bvtsdk/colormaps/jet.cmap");
	  if(ret != 0) {
	       printf("BVTColorMapper_Load: ret=%d\n", ret);
	       //return 1;
	  }
     }

     int Sonar::init()
     {
#if ENABLE_SONAR == 1
          mCurPing = 0;

	  int ret;
	  son = BVTSonar_Create();
	  if (son == NULL ) {
	       printf("BVTSonar_Create: failed\n");
	       //return 1;
	  }

          // Open the sonar
	  ret = BVTSonar_Open(son, "FILE", fn.c_str());
	  if (ret != 0 ) {
	       printf("BVTSonar_Open: ret=%d\n", ret);
	       //return 1;
	  }

	  // Make sure we have the right number of heads
	  heads = -1;
	  heads = BVTSonar_GetHeadCount(son);
	  printf("BVTSonar_GetHeadCount: %d\n", heads);
	  
	  // Get the first head
	  head = NULL;
	  ret = BVTSonar_GetHead(son, 0, &head);
	  if (ret != 0 ) {
	       printf("BVTSonar_GetHead: ret=%d\n", ret);
	       //return 1;
	  }
	
	  // Check the ping count
	  pings = -1;
	  pings = BVTHead_GetPingCount(head);
	  printf("BVTHead_GetPingCount: %d\n", pings);

	  // Set the range window to be 10m to 40m
	  BVTHead_SetRange(head, mMinRange, mMaxRange);

	  // Build a color mapper
	  mapper = BVTColorMapper_Create();
	  if (mapper == NULL) {
	       printf("BVTColorMapper_Create: failed\n");
	       //return 1;
	  }

	  // Load the bone colormap
	  ret = BVTColorMapper_Load(mapper, "../sonar-processing/bvtsdk/colormaps/jet.cmap");
	  if(ret != 0) {
	       printf("BVTColorMapper_Load: ret=%d\n", ret);
	       //return 1;
	  }
#else
          return -1;
#endif
          
     }

     void Sonar::setSonarFile(std::string fn)
     {
	  this->fn = fn;
     }

     void Sonar::setRange(int minRange, int maxRange)
     {
	  mMinRange = minRange;
	  mMaxRange = maxRange;
     }

     int Sonar::getNumPings()
     {
	  return pings;
     }

     int Sonar::getCurrentPingNum()
     {
          return mCurPing;
     }

     void Sonar::setFrameNum(int num)
     {
          mCurPing = num;
     }

     int Sonar::reset()
     {
	  mCurPing = 0;
          return 0;
     }

     int Sonar::getNextSonarImage(cv::Mat &image)
     {
	  int status = -1;
	  if (mCurPing < pings) {
	       status = getSonarImage(image, mCurPing++);
	  } else {
	       status = 0;
	  }
	  return status;
     }

     int Sonar::getSonarImage(cv::Mat &image, int index)
     {
#if ENABLE_SONAR == 1
	  BVTPing ping = NULL;
	  int ret = BVTHead_GetPing(head, index, &ping);
	  
	  if(ret != 0) {
	       printf("BVTHead_GetPing: ret=%d\n", ret);
	       return 0;
	  }
	
	  ret = BVTPing_GetImage(ping, &img);
	  //ret = BVTPing_GetImageXY(ping, &img);
	  //ret = BVTPing_GetImageRTheta(ping, &img);
	  if (ret != 0) {
	       printf("BVTPing_GetImage: ret=%d\n", ret);
	       return 0;
	  }

	  // Perform the colormapping
	  ret = BVTColorMapper_MapImage(mapper, img, &cimg);
	  if (ret != 0) {
	       printf("BVTColorMapper_MapImage: ret=%d\n", ret);
	       return 0;
	  }
	
	  height_ = BVTColorImage_GetHeight(cimg);
	  width_ = BVTColorImage_GetWidth(cimg);

	  IplImage* sonarImg;
	  sonarImg = cvCreateImageHeader(cvSize(width_,height_), IPL_DEPTH_8U, 4);
	
	  // And set it's data
	  cvSetImageData(sonarImg,  BVTColorImage_GetBits(cimg), width_*4);
	
	  cv::Mat tempImg(sonarImg);
	  image = sonarImg;

	  cvReleaseImageHeader(&sonarImg);
	  BVTPing_Destroy(ping);

	  return 1;
#else
          return -1;
#endif
     }

     int Sonar::width() 
     { 
          return width_;
     }

     int Sonar::height()
     {
          return height_;
     }
}
