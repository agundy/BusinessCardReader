# BusinessCardReader
Computer vision final project to find and extract information from business cards.

#Proposal

Batbouta-Gunderson CV Final Project Proposal
Aaron Gunderson & Andrew Batbouta
April 2015

##Overview

The application of computer vision that we will be exploring is extracting contact info from business cards. Our software will ideally take in camera images for business cards. Find the card and transform it so that it is aligned parallel to the viewing plane. This will be done by taking Hough Line Transforms to outline the card. Processing will then be done to increase contrast. To find the text we will apply an algorithm like the Canny Edge Detector to find the text edges. And then group text by finding rectangular regions of interest. Once a region has been isolated it will be run through OCR and the returned text will be matched to business card fields. Checks will be done to find if the quality of a card is sufficient enough to extract text. One check that could be done is seeing if an image is sharp enough to extract text from by checking the gradient magnitude. 

##Sources

One great set of images we found was from Stanford and available [here](http://web.cs.wpi.edu/~claypool/mmsys-dataset/2011/stanford/mvs_images/business_cards.html). This data is originally part of a collection of data sets for image search with smartphone photos. It provides 100 business cards of varying styles and languages with 5 versions of each business card. One version is a scanned high contrast and then the other 4 are of various orientations and blur levels taken with a Droid, E63, Palm, and a Canon. 
Business cards can also be sourced for extra test cases and examples with relative ease and minimal effort.

##Helpful Software

Tesseract is open source software maintained by Google that will be helpful for reading the text once we have the text chunks extracted from the card. This will make the difficult job of reading text much easier. Instead we can focus on making a robust system that can handle variations of cards and varying camera conditions and make them readable to the OCR. Then after running through OCR we should be able to associate fields with standard business card fields.
