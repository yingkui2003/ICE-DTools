# A) ArcGIS Pro Toolbox
The ArcGIS Pro toolbox can be directly used in ArcGIS Pro after adding a folder connection of the ArcGIS Pro toolbox folder to the ArcGIS Pro project. This toolbox includes three tools:

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/9f1e43a8-1eae-4aa1-b86f-5a29a68e6bae)

The “Retrieve ICE-D Data From HeidiSQL Connection” tool is used to retrieve exposure ages (ICE-D Alpine) based on specified latitude and longitude ranges. The user also needs to select a scaling model for the ages (St, Lm, or LSDn).

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/72b1d02b-e382-43b2-b032-d7d82f4f13e7)

Note that this tool is limited to the computer that has the HeidiSQL and ICE-D database installed. The user also needs to keep the ICE-D database open to run this tool. In addition, the pymysql, shapely, and fiona libraries are also needed to be installed in the ArcGIS Pro python version. To do that, open the “Python Command Prompt” under the ArcGIS Pro program folder by clicking the Microsoft Window icon on the left-bottom bar of the computer and find the ArcGIS or ArcGIS Pro app folder. Then, run the following commands:
```
pip install pymysql
pip install shapely
pip install fiona

```
The ICE-D dataset can be imported into ArcGIS Pro as a WFS layer. However, ArcGIS Pro uses a limit of 3000 for the ICE-D dataset. To retrieve more exposure ages, a new tool, “Retrieve ICE-D Data From WFS”, is developed. The users can select a dataset from ICE-D and provide a maximum number of features to retrieve the exposure ages as a feature class in ArcGIS Pro.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/9626dc91-2e92-4f82-908e-6f570f681138)

The “Create Camel Plots based on ICE-D ExpAges” tool is developed to create the camelplot for each site based on multiple exposure ages. All camelplots are saved into a folder and a site feature class is created to save the summary info of the exposure ages, such as mean, std, variances, skewness, and chi-square values. Each camelplot is also associated with its corresponding site so that the plot can be viewed interactively in ArcGIS Pro. The following is a screenshot of the interface of this tool in ArcGIS Pro.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/febd08cf-58ea-415e-b5cb-c103ef8a3a94)

# B) QGIS Plugin
How to install and use the ICE-D Analysis plugin in QGIS
1. Unzip the iced_camelplots.zip file to a folder in your computer. Find the “iced_camelplots” folder and check if there are a set of folders and files (similar to the following screenshot) within the folder:

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/cb4180ed-c5b3-4869-b656-c59ce1dd744b)

2. Open QGIS and under the “Setting” menu, choose User profile -> Open Active Profile Folder. See the following screenshot.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/f0f8f8b6-0e43-47eb-a983-06fd4f52cc7d)

 

This will open the active profile folder. Then, copy the “iced_camelplots” folder to the “python->plugins” folder in the active profile folder. If there is no the “plugins” folder, create one.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/8fca79ef-fa58-4e5f-8d72-9c57e3d95f12)
 

Close and reopen QGIS. Under the “Plugin” menu, Click “Manage and Install Plugins…”.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/852afcdf-43d8-4ed3-ae9b-f9c621ec9772)
 

In the left panel of the Plugins window, Click “Installed” and You should find the “ICE-D Camelplots” plugin (the following screenshot). Chick it and close the window.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/b0b3c3e9-59cb-4ca1-b17c-d475845ff5d6)


Note that this plugin is in the development mode. More functions will be added in the future. After the plugin is finalized, it can be published directly in QGIS, so that no copy/paste folder is needed in the future. 

You should be able to see the plugin in three locations: the Plugin menu, the toolbar, and the processing toolbox. 
 
![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/74a25244-8322-41df-b16a-a1927ffdb46c)
 
![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/1bf2593d-4b41-48ed-99b3-2c77ef900884)

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/fd75c697-10bd-4ba0-9bc3-82b852f6beb6)
 

You can run the “Camel Plots” tool from one of these three locations.

 
# How to use the “Camel Plots” tool and view the camelplots in QGIS

The following screenshot shows the interface of the “Camel Plots” tool after running it.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/37dec74d-0da4-4616-b2f7-d184891d4bb5)


You need to specify the ExpAge data (a subset layer of the WFS feature of the ICE-D database), then select the Sample Name Field (name), Site Name Field (site_name), ExpAge Field (t_LSDn or t_St), and Age Error Field (t_dint_LSDn or t_dint_St). You also need to choose a folder to save the camelplot for each site and an Output Site Point Feature as a shapefile or other GIS format. After that, click Run to run the tool.
The progress bar will show the progress of the calculation. After finishing, a site point layer will be added to the map to show the summary (#samples, mean, std, variance, skewness, and Chi-square) of each site and the link to the camelplot images. The following is a screenshot of the attribute table of the created site layer.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/02254fba-93da-4998-8aaf-74ff76d9aa80)


You can “Ctrl + Click” the image path to view the camelplot for each site. You can also view the camelplot in QGIS as HTML map tips. To enable this function, right click the create site layer and choose “Properties”. In the Layer Properties Dialog, chick “Display” on the left panel. 

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/81084c8f-6d3d-4ded-95a4-85117f141012)


Make sure to check “Enable Map tips” (QGIS 3.32). If using the old version of QGIS, you need to Click the “View” menu and click “Show Map Tips” to enable this function (see the following screenshot). 

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/2689fe25-ddbb-4593-8485-685c0c9734bc)

In the Layer Properties Dialog, type in the following part to the box under “HTML Map Tip”:

```
<style>
   body {width:800px!;}
   div {width:800px;}
   img { width:100%; max-width:500px; }
</style>
<div>
   <img src=[% "CamelPlot" %] >
</div>

```

Click OK. This will show the camelplot as a map tip when the cursor is close to each site (the site layer needs to be selected). The following screenshot is an example.
 
![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/c00f5d96-dfb4-43db-afa2-90d269797a44)



# How to download and use this toolbox in ArcGIS or ArcGIS Pro
The github site includes an ArcGIS Pro toolbox folder with the python codes and ArcGIS Pro toolbox and a QGIS plugin folder with the QGIS plugin folder and files. The user can click "Code" (green color) on the right side of the github page and choose Download Zip.

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/e11aee09-65b7-40d4-b119-69cba359c135)


A zip file of the whole github folder will be downloaded to the local computer. Unzip this file will create a ICE-DTools-main folder with all folder and files. Then, the user can follow the instructions in the folder and Github page to use the ArcGIS Pro toolbox or QGIS plugin.   

# Contact info
Yingkui Li

Department of Geography & Sustainability

University of Tennessee

Knoxville, TN 37996

Email: yli32@utk.edu

Website: https://geography.utk.edu/about-us/faculty/dr-yingkui-li/

Google Scholar: https://scholar.google.com/citations?user=JoNuyCMAAAAJ&hl=en&oi=ao
