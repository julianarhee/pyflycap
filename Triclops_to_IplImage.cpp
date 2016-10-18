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

IplImage* TriclopsToOpenCVImage(TriclopsImage myImage) {
	IplImage* result = NULL;
	CvSize mySize;
	mySize.height = myImage.nrows;
	mySize.width = myImage.ncols;
	result = cvCreateImageHeader(mySize, 8, 1); //triclopsImage should be 8bit per pixel / 1 channel
	result->depth = IPL_DEPTH_8U;
	result->nChannels = 1;
	result->imageDataOrigin = (char*) myImage.data;
	result->imageData       = (char*) myImage.data;
	result->widthStep		= myImage.rowinc;
	result->nSize           = sizeof(IplImage);
	result->imageSize       = result->height * result->widthStep;
	return result;
}

IplImage* TriclopsToOpenCVImage(TriclopsColorImage myImage) {
	IplImage* result = NULL;
	CvSize mySize;
	mySize.height = myImage.nrows;
	mySize.width = myImage.ncols;
	result = cvCreateImageHeader(mySize, 8, 3); //triclopsImage should be 8bit per pixel / 1 channel
	result->depth = IPL_DEPTH_8U;
	result->nChannels = 3;
	int index = 0;
	unsigned char* data = new unsigned char[myImage.ncols * myImage.nrows * 3];
	for(int row = 0; row < myImage.nrows; row++) {
		unsigned char* red = myImage.red + myImage.rowinc * row;
		unsigned char* green = myImage.green + myImage.rowinc * row;
		unsigned char* blue = myImage.blue + myImage.rowinc * row;
		for(int col = 0; col < myImage.ncols; col++) {
			data[index++] = red[col];
			data[index++] = green[col];
			data[index++] = blue[col];
		}
	}

	result->imageDataOrigin = (char*)data;
	result->imageData       = (char*)data;
	result->widthStep		= myImage.rowinc;
	result->nSize           = sizeof(IplImage);
	result->imageSize       = result->height * result->widthStep;
	return result;
}
