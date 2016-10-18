//=============================================================================
// Copyright © 2013 Point Grey Research, Inc. All Rights Reserved.
//
// This software is the confidential and proprietary information of Point
// Grey Research, Inc. ("Confidential Information").  You shall not
// disclose such Confidential Information and shall use it only in
// accordance with the terms of the license agreement you entered into
// with Point Grey Research, Inc. (PGR).
//
// PGR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
// SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
// PURPOSE, OR NON-INFRINGEMENT. PGR SHALL NOT BE LIABLE FOR ANY DAMAGES
// SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
// THIS SOFTWARE OR ITS DERIVATIVES.
//=============================================================================

void ConvertImageToOpenCV(FlyCaptureContext context, FlyCaptureImage* pImage, IplImage* cvImage)
{
    if (pImage->bStippled) {
        FlyCaptureImage colorImage; //new image to be referenced by cvImage
        colorImage.pData       = new unsigned char[pImage->iRows*pImage->iCols*3];
        colorImage.pixelFormat = FLYCAPTURE_BGR;
     
        flycaptureConvertImage(context, pImage, &colorImage); //needs to be as BGR to be saved
        CvSize mySize;
        mySize.width = colorImage.iCols;
        mySize.height = colorImage.iRows;

		cvImage = cvCreateImageHeader(mySize, 8, 3);

 

        cvImage->width = colorImage.iCols;
        cvImage->height = colorImage.iRows;
        cvImage->widthStep = colorImage.iRowInc;

 

        // 24 bit BGR
         cvImage->depth = IPL_DEPTH_8U;
         cvImage->nChannels = 3;
        
         cvImage->origin = 0; //interleaved color channels

 

        cvImage->imageDataOrigin = (char*)(colorImage.pData); //DataOrigin and Data same pointer, no ROI
        cvImage->imageData         = (char*)(colorImage.pData);
        cvImage->nSize = sizeof (IplImage);
        cvImage->imageSize = cvImage->height * cvImage->widthStep;
     }   
     else
     {
		FlyCaptureImage colorImage; 

        CvSize mySize;
        mySize.width = pImage->iCols;
        mySize.height = pImage->iRows;

        bool needToTransform = false;

        switch(pImage->pixelFormat) {
     
             // 8 bit of mono.
             case FLYCAPTURE_MONO8:  cvImage = cvCreateImageHeader(mySize, 8, 1 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 1;
                                     break;
            
             // 16 bit mono.
             case FLYCAPTURE_MONO16:    cvImage = cvCreateImageHeader(mySize, 16, 1 );
                                     cvImage->depth = IPL_DEPTH_16U;
                                     cvImage->nChannels = 1;
                                     break;
            
             // 16 bit signed mono .
             case FLYCAPTURE_S_MONO16:    cvImage = cvCreateImageHeader(mySize, 16, 1 );
                                         cvImage->depth = IPL_DEPTH_16S;
                                         cvImage->nChannels = 1;
                                         break;
            
             // 8 bit raw data output from sensor.
             case FLYCAPTURE_RAW8:    cvImage = cvCreateImageHeader(mySize, 8, 1 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 1;
                                     needToTransform = pImage->bStippled;
                                     printf("Should not be reached");
                                     break;
            
             // 16 bit raw data output from  sensor.
             case FLYCAPTURE_RAW16:    cvImage = cvCreateImageHeader(mySize, 16, 1 );
                                     cvImage->depth = IPL_DEPTH_16U;
                                     cvImage->nChannels = 1;
                                     needToTransform = pImage->bStippled;
                                     printf("Should not be reached");
                                     break;
            
             // YUV 4:1:1.
             case FLYCAPTURE_411YUV8:cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // YUV 4:2:2.
             case FLYCAPTURE_422YUV8:cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // YUV 4:4:4.
             case FLYCAPTURE_444YUV8:cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // R, G and B are the same and equal 8 bits.
             case FLYCAPTURE_RGB8:    cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // RR, G and B are the same and equal 16 bits.
             case FLYCAPTURE_RGB16:    cvImage = cvCreateImageHeader(mySize, 8, 3 ); //would be mySize,16,3 with 16bit BGR
                                     cvImage->depth = IPL_DEPTH_16U;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // RR, G and B are the same and equal 16 bits signed
             case FLYCAPTURE_S_RGB16:cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_16S;
                                     cvImage->nChannels = 3;
                                     needToTransform = true;
                                     break;
            
             // 24 bit BGR
             case FLYCAPTURE_BGR:    cvImage = cvCreateImageHeader(mySize, 8, 3 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 3;
                                     break;
            
             // 32 bit BGRU
             case FLYCAPTURE_BGRU:    cvImage = cvCreateImageHeader(mySize, 8, 4 );
                                     cvImage->depth = IPL_DEPTH_8U;
                                     cvImage->nChannels = 4;
                                     break;
             default: printf("Should not reach mey!");
         }

 

        cvImage->origin = 0; //interleaved color channels

 

        cvImage->imageDataOrigin = (char*)(pImage->pData);
         cvImage->imageData         = (char*)(pImage->pData);
         cvImage->widthStep         = pImage->iRowInc;
         cvImage->nSize             = sizeof (IplImage);
         cvImage->imageSize         = cvImage->height * cvImage->widthStep;
        
         if(needToTransform) {
             colorImage.pData       = new unsigned char[pImage->iRows*pImage->iCols*3];
             colorImage.pixelFormat = FLYCAPTURE_BGR;
             flycaptureConvertImage(context, pImage, &colorImage);
             cvImage->imageDataOrigin = (char*)(colorImage.pData);
             cvImage->imageData         = (char*)(colorImage.pData);
             cvImage->nSize = sizeof (IplImage);
             cvImage->widthStep = colorImage.iRowInc;
             cvImage->imageSize = cvImage->height * cvImage->widthStep;
         }
 

        //at this point cvImage contains a valid IplImage
     }
}