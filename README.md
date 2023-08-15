#How to install and use the ICE-D Analysis plugin in QGIS
1. Unzip the iced_camelplots.zip file to a folder in your computer. Find the “iced_camelplots” folder and check if there are a set of folders and files (similar to the following screenshot) within the folder:

![image](https://github.com/yingkui2003/ICE-DTools/assets/24683137/cb4180ed-c5b3-4869-b656-c59ce1dd744b)

2. Open QGIS and under the “Setting” menu, choose User profile -> Open Active Profile Folder. See the following screenshot.

 

This will open the active profile folder. Then, copy the “iced_camelplots” folder to the “python->plugins” folder in the active profile folder. If there is no the “plugins” folder, create one.
 

Close and reopen QGIS. Under the “Plugin” menu, Click “Manage and Install Plugins…”.
 

In the left panel of the Plugins window, Click “Installed” and You should find the “ICE-D Camelplots” plugin (the following screenshot). Chick it and close the window.
 
Note that this plugin is in the development mode. More functions will be added in the future. After the plugin is finalized, it can be published directly in QGIS, so that no copy/paste folder is needed in the future. 

You should be able to see the plugin in three locations: the Plugin menu, the toolbar, and the processing toolbox. 
 
 

 

You can run the “Camel Plots” tool from one of these three locations.

 
How to use the “Camel Plots” tool and view the camelplots in QGIS
The following screenshot shows the interface of the “Camel Plots” tool after running it.
 
You need to specify the ExpAge data (a subset layer of the WFS feature of the ICE-D database), then select the Sample Name Field (name), Site Name Field (site_name), ExpAge Field (t_LSDn or t_St), and Age Error Field (t_dint_LSDn or t_dint_St). You also need to choose a folder to save the camelplot for each site and an Output Site Point Feature as a shapefile or other GIS format. After that, click Run to run the tool.
The progress bar will show the progress of the calculation. After finishing, a site point layer will be added to the map to show the summary (#samples, mean, std, variance, skewness, and Chi-square) of each site and the link to the camelplot images. The following is a screenshot of the attribute table of the created site layer.
 
You can “Ctrl + Click” the image path to view the camelplot for each site. You can also view the camelplot in QGIS as HTML map tips. To enable this function, right click the create site layer and choose “Properties”. In the Layer Properties Dialog, chick “Display” on the left panel. 
 
Make sure to check “Enable Map tips” (QGIS 3.32). If using the old version of QGIS, you need to Click the “View” menu and click “Show Map Tips” to enable this function (see the following screenshot). 
 
In the Layer Properties Dialog, add the following part to the box under “HTML Map Tip”:
<style>
   body {width:800px!;}
   div {width:800px;}
   img { width:100%; max-width:500px; }
</style>
<div>
   <img src=[% "CamelPlot" %] >
</div>

Click OK. This will show the camelplot as a map tip when the cursor is close to each site (the site layer needs to be selected). The following screenshot is an example.
 



