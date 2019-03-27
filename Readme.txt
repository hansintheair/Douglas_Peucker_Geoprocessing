I created a script implimenting the Douglas_Peucker Algorithm during my Master's study as a side project (12/1/2013). 
The script is now upadted to run as a geoprocessing tool in ArcGIS 3/24/2019. 

Included:
Douglas_Peucker.py			> Python script
DouglasPeucker_Math.pdf			> Math used in script developed from principles of Douglas-Peucker algorithm as described at
					  https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
DouglasPeucker_TestMapDoc.mxd		> Map document used for testing. Tool also tested and working in Pro
DouglasPeucker_TestData.gdb		> Geodatabase
	\DouglassPeuckerAlg		> Toolbox containing the Douglas-Peucker Algorithm geoprocessing tool, which references Douglas_Peucker.py
					  Tool description available when running tool from ArcMap
	\Test_Line			> A polyline featureclass I used for testing

A good value for tolerance with the included test data is 3000.
